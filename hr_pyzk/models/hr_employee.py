# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    clock_user_id = fields.Many2one(
        comodel_name="hr.attendance.clock.user",
        string="Related clock user",
    )

    clock_template_count = fields.Integer(
        compute="_compute_clock_template_count",
        store=True,
    )

    @api.depends("clock_user_id")
    def _compute_clock_template_count(self):
        for ee in self:
            ee.clock_template_count = ee.clock_user_id.template_ids_count

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

    def open_clock_user_form(self):
        self.ensure_one()

        if not self.clock_user_id:
            self.create_clock_user()
        action = self.env.ref(
            "hr_pyzk.act_hr_employee_2_hr_attendance_clock_user"
        ).read()[0]
        action["res_id"] = self.clock_user_id.id

        return action
