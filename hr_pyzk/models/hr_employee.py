# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    clock_user_id = fields.Many2one(
        comodel_name="hr.attendance.clock.user",
        string="Related clock user",
    )

    def create_clock_user(self):
        ClockUser = self.env["hr.attendance.clock.user"]
        res = ClockUser
        for employee in self:
            if employee.clock_user_id:
                continue
            if ClockUser.search_count([("employee_id", "=", employee.id)]) > 0:
                raise exceptions.ValidationError(
                    _("There is a Clock User already linked to this employee")
                )
            employee.clock_user_id = ClockUser.create({
                "name": employee.name,
                "state": "odoo",
            })
            res |= employee.clock_user_id

        return res
