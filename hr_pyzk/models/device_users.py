from odoo import _, api, fields, models
from odoo.exceptions import UserError
from zk import const

from . import controller_pyzk as c


class DeviceUsers(models.Model):
    _name = "hr.attendance.clock.user"
    _description = "Attendance Clock User"
    _order = "device_user_id"

    device_user_id = fields.Integer(string="Device User ID", readonly=False)
    # uid in the device. Important to delete user in the future
    device_uid = fields.Integer(string="Device UID", readonly=True)
    name = fields.Char("Device User Name", required=True)
    employee_id = fields.Many2one("hr.employee", "Related employee")
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

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        for clock_user in self:
            if clock_user.name is False and clock_user.employee_id:
                clock_user.name = clock_user.employee_id.name
            if not clock_user.device_user_id and clock_user.employee_id:
                clock_user.device_user_id = clock_user.employee_id.id

    def _do_notify(self, title="", msg="", type="info", sticky=False):
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
                        privilege=const.USER_DEFAULT,
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
                        f"The User ID is already in use on device '{dev.name}'. "
                        "Please choose another ID.",
                        type="danger",
                    )

    def edit_user(self):
        """
        Function uses to get attendances
        """
        if not self.device_ids:
            raise UserError(_("Fingerprint device is not selected"))

        for dev in self.device_ids:
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
                        privilege=const.USER_DEFAULT,
                        user_id=str(self.device_user_id),
                    )
                    return self._do_notify(
                        "Success",
                        "The user record has been updated on the device.",
                        type="success",
                    )
                else:
                    return self._do_notify(
                        "Error",
                        f"The User ID does not exist on device '{dev.name}'. ",
                        type="danger",
                    )
