from odoo import api, fields, models


class DeviceAttendances(models.Model):
    _name = "device.attendances"
    _description = "Device Attendances"
    _order = "device_datetime desc"

    @api.depends("device_id")
    def _compute_get_employee_id(self):
        for dev in self:
            if dev.device_user_id.employee_id:
                dev.employee_id = dev.device_user_id.employee_id

    device_user_id = fields.Many2one("hr.attendance.clock.user", "Device ID")
    employee_id = fields.Many2one(
        "hr.employee", "Related employee", compute=_compute_get_employee_id, store=True
    )
    device_datetime = fields.Datetime(string="Device Datetime")
    device_punch = fields.Selection(
        [("0", "Check In"), ("1", "Check Out")], string="Device Punch"
    )
    attendance_state = fields.Selection(
        selection=[("0", "Not Logged"), ("1", "Logged")], string="Status", default="0"
    )
    # validity = fields.Selection([(0, 'Valid'), (1, 'Invalid')], string='Validity', default=0)
    device_id = fields.Many2one("hr.attendance.clock", "Attendance Device")
