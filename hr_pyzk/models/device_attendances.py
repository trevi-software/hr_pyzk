# Copyright (C) 2022,2023 TREVI Software
# Copyright (C) Sheikh M. Salahuddin <smsalah@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class DeviceAttendances(models.Model):
    _name = "hr.attendance.clock.punch"
    _description = "Clock Device Punch"
    _order = "device_datetime desc"

    device_user_id = fields.Many2one("hr.attendance.clock.user", "Device User ID")
    employee_id = fields.Many2one(
        "hr.employee",
        related="device_user_id.employee_id",
        store=True
    )
    device_datetime = fields.Datetime(string="Device Datetime")
    device_punch = fields.Selection(
        [
            ("0", "Check In"),
            ("1", "Check Out"),
            ("2", "Break Out"),
            ("3", "Break In"),
            ("4", "OT In"),
            ("5", "OT Out"),
        ],
        string="Device Punch"
    )
    attendance_state = fields.Selection(
        selection=[("0", "Not Recorded"), ("1", "Recorded")],
        string="Status",
        default="0"
    )
    device_id = fields.Many2one("hr.attendance.clock", "Attendance Device")
    active = fields.Boolean(default=True)
    attendance_id = fields.Many2one("hr.attendance", readonly=True)

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
                _("Punches that have already been recorded may not be deleted.")
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
        res = hr_attendance.create(attendance_record)
        self.mark_device_attendance_converted(res)

    def create_check_in_attendance(self):
        self.ensure_one()
        hr_attendance = self.env["hr.attendance"]
        attendance_record = {
            "employee_id": self.employee_id.id,
            "check_in": self.device_datetime,
        }
        res = hr_attendance.create(attendance_record)
        self.mark_device_attendance_converted(res)

    def update_attendance_check_out(self):
        hr_attendance = self[0].attendance_id
        if hr_attendance:
            hr_attendance.check_out = self[1].device_datetime
        self[1].mark_device_attendance_converted(hr_attendance)

    def mark_device_attendance_converted(self, hr_attendance):
        self.write(
            {"attendance_id": hr_attendance.id, "attendance_state": "1"}
        )
