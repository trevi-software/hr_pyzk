# Copyright (C) 2022,2023 TREVI Software
# Copyright (C) Sheikh M. Salahuddin <smsalah@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from . import controller_pyzk as c
import logging
logger = logging.getLogger(__name__)


class DeviceUsers(models.Model):
    _name = "hr.attendance.clock.user"
    _description = "Attendance Clock User"
    _order = "device_user_id"

    device_user_id = fields.Integer(
        string="Device User ID",
        required=True,
    )
    # uid in the device. Important to delete user in the future
    device_uid = fields.Integer(
        string="Device UID",
        required=True,
    )
    name = fields.Char("Device User Name", required=True)
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Related employee",
        ondelete="restrict",
    )
    device_id = fields.Many2one(
        comodel_name="hr.attendance.clock",
        string="Source Device",
        readonly=True,
        help="Device from which this record was originaly imported",
    )
    device_ids = fields.Many2many(
        comodel_name="hr.attendance.clock",
        string="Devices",
        help="Devices to which user record should be synced.",
    )
    privilege_ids = fields.Many2many("hr.attendance.clock.user.privilege")
    template_ids = fields.One2many(
        comodel_name="hr.attendance.clock.user.template",
        inverse_name="device_user_id",
        string="Fingerprints"
    )
    template_ids_count = fields.Integer(
        compute="_compute_template_ids_count",
        string="Fingers scanned"
    )
    state = fields.Selection(
        [
            ("device", "Imported"),
            ("odoo", "Linked")
        ],
        default="device",
        help="""
        The device user can be in one of two states:
        Imported - Imported from a clock device but not yet linked to an
                   Employee record.
        Linked - Either the record was created directly from an Odoo employee
                 or it was imported from a device and then linked to an Odoo
                 employee."""
    )

    _sql_constraints = [
        (
            "employee_id_uniq",
            "unique (employee_id)",
            "It is not possible to relate an employee with a pyzk user "
            "more than once!",
        ),
    ]

    _sql_constraints = [
        (
            "device_user_id_uniq",
            "unique (device_user_id)",
            "It is not possible to create more than one user "
            "with the same device_user_id",
        ),
    ]

    @api.depends("template_ids")
    def _compute_template_ids_count(self):
        for device_user in self:
            device_user.template_ids_count = len(device_user.template_ids)

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        for clock_user in self:
            if clock_user.name is False and clock_user.employee_id:
                clock_user.name = clock_user.employee_id.name
            if not clock_user.device_user_id and clock_user.employee_id:
                clock_user.device_user_id = clock_user.employee_id.id

    def _do_notify(self, title="", msg="", mtype="info", sticky=False):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': msg,
                'sticky': sticky,
                }
        }
        return notification

    def register_to_enrollment_device(self):
        pass

    def enroll_user(self):
        for dev in self.device_id:
            with c.ConnectToDevice(
                dev.ip_address, dev.port, dev.device_password
            ) as connection:
                res = connection.enroll_user(
                    str(self.device_uid), str(0), str(self.device_user_id)
                )
                if res is True:
                    return self._do_notify(
                        "Success",
                        "The finger has been enrolled on the device.",
                        type="success",
                    )
                else:
                    return self._do_notify(
                        "Error",
                        "Finger enrollment has failed.",
                        type="danger",
                    )

    def upload_to_clock(self):
        pass

    def create_user(self):
        """
        Function uses to get attendances
        """
        for dev in self.device_ids:
            ip_address = dev.ip_address
            port = dev.port
            device_password = dev.device_password

            with c.ConnectToDevice(ip_address, port, device_password) as conn:

                device_users = conn.get_users()
                device_user_ids = [int(x.user_id) for x in device_users]
                if self.device_user_id not in device_user_ids:
                    conn.set_user(
                        uid=self.device_user_id,
                        name=self.name,
                        privilege=c.USER_DEFAULT,
                        user_id=str(self.device_user_id),
                    )
                    self.device_uid = self.device_user_id
                    return self._do_notify(
                        "Success",
                        "The user has been created on the device.",
                        type="success",
                    )
                else:
                    return self._do_notify(
                        "Error",
                        f"The User ID '{self.device_user_id}' is already in "
                        f"use on '{dev.name}'. Please choose another ID.",
                        type="danger",
                    )

    def edit_user(self, device_ids=None):
        """
        Function uses to get attendances
        """
        self.ensure_one()
        if device_ids is None:
            device_ids = self.device_ids
        if not device_ids:
            raise UserError(_("Fingerprint device is not selected"))

        for dev in device_ids:
            ip_address = dev.ip_address
            port = dev.port
            device_password = dev.device_password
            with c.ConnectToDevice(ip_address, port, device_password) as conn:

                device_users = conn.get_users()
                device_user_ids = [int(x.user_id) for x in device_users]
                if self.device_user_id in device_user_ids:
                    conn.set_user(
                        uid=self.device_uid,
                        name=self.name,
                        privilege=c.USER_DEFAULT,
                        user_id=str(self.device_user_id),
                    )
                    return self._do_notify(
                        "Success",
                        f"The record for '{self.name}' has been successfuly "
                        f"updated.",
                        type="success",
                    )
                else:
                    return self._do_notify(
                        "Error",
                        f"The User ID '{self.device_user_id}' does not exist "
                        f"on device '{dev.name}'. ",
                        type="danger",
                    )

    def action_create_hr_attendance(self):
        self.create_hr_attendance()

        return self.env.ref("hr_pyzk.device_attendances_action").read()[0]

    def create_hr_attendance(self):
        max_delta = timedelta(hours=14)
        clock_punches = self.env["hr.attendance.clock.punch"]
        for user in self:
            device_punches = clock_punches.search(
                [
                    ("device_user_id", "=", user.id),
                    ("attendance_id", "=", False),
                ]
            )
            lst = []
            device_punches = device_punches.sorted("device_datetime")
            prv_punches = user.get_previous_punch_record()
            _first_run = True
            for punch in device_punches:
                delta = max_delta
                if len(prv_punches) > 0:
                    delta = \
                        punch.device_datetime - prv_punches[-1].device_datetime
                if len(prv_punches) == 0 or delta < max_delta:
                    prv_punches |= punch
                    if _first_run is True:
                        _first_run = False
                    continue
                elif delta > max_delta:
                    if _first_run is False:
                        lst.append(prv_punches)
                    else:  # _first_run is True
                        _first_run = False
                    prv_punches = punch

            # There may be a left-over device punch that has a missing
            # counter-part
            if len(prv_punches) == 1:
                lst.append(prv_punches)
            elif len(prv_punches) > 1:
                raise ValidationError(
                    _("Internal error. Unexpeced device punches.")
                )

            # Create attendance records
            for grouped_punches in lst:
                if len(grouped_punches) == 1:
                    grouped_punches.create_check_in_attendance()
                    continue
                _check_in = True
                single_attendance = self.env["hr.attendance.clock.punch"]
                for punch in grouped_punches:
                    if _check_in:
                        single_attendance |= punch
                        _check_in = False
                    else:
                        single_attendance |= punch
                        single_attendance.create_complete_attendance()
                        _check_in = True
                        single_attendance = self.env[
                            "hr.attendance.clock.punch"
                        ]
                if len(single_attendance) > 0:
                    single_attendance.create_check_in_attendance()

    def get_previous_punch_record(self):

        self.ensure_one()
        return self.env["hr.attendance.clock.punch"].search(
            [
                ("device_user_id", "=", self.id),
                ("attendance_id", "!=", False),
            ],
            order="device_datetime desc",
            limit=1,
        )

    def action_create_hr_employee(self):
        self.create_hr_employee()

        return self.env.ref("hr_pyzk.device_users_action").read()[0]

    def create_hr_employee(self):
        HrEmployee = self.env["hr.employee"]
        res = HrEmployee
        for user in self:
            if user.employee_id:
                continue
            ee = HrEmployee.create({
                "name": user.name,
                "clock_user_id": user.id,
            })
            user.employee_id = ee
            res |= ee

        return res

    def get_effective_privilege(self, device_id):
        self.ensure_one()
        priv = 'default'
        for p in self.privilege_ids:
            if p.device_id.id == device_id.id:
                priv = p.privilege
        return self.map_privilege(priv)

    @api.model
    def map_privilege(self, privilege):
        res = c.USER_DEFAULT
        if privilege == "enroller":
            res = c.USER_ENROLLER
        elif privilege == "manager":
            res = c.USER_MANAGER
        elif privilege == "admin":
            res = c.USER_ADMIN
        return res

    @api.model_create_multi
    def create(self, lst):
        for vals in lst:
            if vals.get("device_uid", 0) == 0:
                vals["device_uid"] = int(
                    self.env["ir.sequence"].next_by_code(
                        "hr.attendance.clock.user.uid.ref")
                )
            if vals.get("device_user_id", 0) == 0:
                vals["device_user_id"] = int(
                    self.env["ir.sequence"].next_by_code(
                        "hr.attendance.clock.user.device_user_id.ref")
                )

        return super().create(lst)
