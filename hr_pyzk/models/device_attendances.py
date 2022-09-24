from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DeviceAttendances(models.Model):
    _name = "hr.attendance.clock.punch"
    _description = "Clock Device Punch"
    _order = "device_datetime desc"

    @api.depends("device_id")
    def _compute_get_employee_id(self):
        for dev in self:
            if dev.device_user_id.employee_id:
                dev.employee_id = dev.device_user_id.employee_id

    device_user_id = fields.Many2one("hr.attendance.clock.user", "Device User ID")
    employee_id = fields.Many2one(
        "hr.employee",
        "Related employee",
        compute=_compute_get_employee_id,
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
