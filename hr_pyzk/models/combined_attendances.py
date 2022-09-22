# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models


class CombinedAttendances(models.Model):
    _name = "combined.attendances"
    _description = "combined.attendances"
    _order = "device_date desc"

    # @api.one
    # def _compute_get_employee_id(self):
    #     if self.pyzk_employee_id.employee_id:
    #         self.employee_id = self.pyzk_employee_id.employee_id
    #
    # @api.one
    # def _compute_get_name(self):
    #     if self.pyzk_employee_id:
    #         self.name = self.pyzk_employee_id.name

    @api.depends("device_user_id")
    def _compute_get_employee_id(self):
        for dev in self:
            if dev.device_user_id.employee_id:
                dev.employee_id = dev.device_user_id.employee_id

    device_user_id = fields.Many2one("device.users", "Device User ID")
    employee_id = fields.Many2one(
        "hr.employee",
        "Related employee",
        compute=_compute_get_employee_id,
        store=True
    )
    device_date = fields.Date(string="Date")
    device_clockin = fields.Datetime(string="Clock In")
    device_clockout = fields.Datetime(string="Clock Out")
    state = fields.Selection(
        selection=[
            ("not_ransferred", "Not Transferred"),
            ("invalid", "Invalid"),
            ("transferred", "Transferred"),
        ],
        string="Status",
        default="not_ransferred",
    )
