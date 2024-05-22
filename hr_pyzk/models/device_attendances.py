# Copyright (C) 2022,2023 TREVI Software
# Copyright (C) Sheikh M. Salahuddin <smsalah@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)


class DeviceAttendances(models.Model):
    _name = "hr.attendance.clock.punch"
    _description = "Clock Device Punch"
    _order = "device_datetime desc"

    device_user_id = fields.Many2one("hr.attendance.clock.user", required=True)
    employee_id = fields.Many2one(
        related="device_user_id.employee_id",
        store=True
    )
    device_datetime = fields.Datetime(required=True)
    device_punch = fields.Selection(
        [
            ("0", "Check In"),
            ("1", "Check Out"),
            ("2", "Break Out"),
            ("3", "Break In"),
            ("4", "OT In"),
            ("5", "OT Out"),
        ],
        string="Device Punch",
        required=True,
    )
    attendance_state = fields.Selection(
        selection=[("0", "New"), ("1", "Recorded")],
        compute="_compute_attendance_state",
        store=False
    )
    device_id = fields.Many2one(
        comodel_name="hr.attendance.clock",
        string="Attendance Device",
        required=True,
    )
    active = fields.Boolean(default=True)
    attendance_id = fields.Many2one("hr.attendance", ondelete='set null')
    error_state = fields.Selection(
        selection=[("ok", "Ok"), ("ex", "Exception")]
    )

    @api.depends("attendance_id")
    def _compute_attendance_state(self):
        for punch in self:
            if punch.attendance_id:
                punch.attendance_state = "1"
            else:
                punch.write({
                    "attendance_state": "0",
                    "error_state": False,
                })

    def name_get(self):
        res = []
        for rec in self:
            res.append(
                (rec.id, f"{rec.employee_id.name} {rec.device_datetime}")
            )
        return res

    def unlink(self):

        logged_ids = self.filtered(lambda a: a.attendance_state == "1")
        if logged_ids:
            raise UserError(
                _("Punches that have been recorded may not be deleted.")
            )
        return super().unlink()

    def create_complete_attendance(self):
        hr_attendance = self.env["hr.attendance"]
        if len(self) != 2:
            raise ValidationError(
                _("Internal error. Expected only two punches")
            )
        if self[0].attendance_id:
            self.update_attendance_check_out()
            return

        assert self[0].employee_id == self[1].employee_id
        attendance_record = {
            "employee_id": self[0].employee_id.id,
            "check_in": self[0].device_datetime,
            "check_out": self[1].device_datetime,
        }
        try:
            res = hr_attendance.create(attendance_record)
        except Exception as ex:
            logger.error(f"unable to create full attendance: {ex}")
        else:
            self.mark_device_attendance_converted(res)

    def create_check_in_attendance(self):
        assert len(self) == 1
        hr_attendance = self.env["hr.attendance"]
        attendance_record = {
            "employee_id": self[0].employee_id.id,
            "check_in": self[0].device_datetime,
        }
        try:
            res = hr_attendance.create(attendance_record)
        except Exception as ex:
            logger.error(f"unable to create check-in attendance: {ex}")
            self.error_state = "ex"
        else:
            self.mark_device_attendance_converted(res)

    def update_attendance_check_out(self):
        hr_attendance = self.attendance_id
        if hr_attendance:
            try:
                hr_attendance.check_out = self[1].device_datetime
            except Exception as ex:
                logger.error(f"unable to update attendance: {ex}")
                self.error_state = "ex"
            else:
                self[1].mark_device_attendance_converted(hr_attendance)

    def mark_device_attendance_converted(self, hr_attendance):
        self.write(
            {
                "attendance_id": hr_attendance.id,
                "error_state": "ok",
            }
        )
