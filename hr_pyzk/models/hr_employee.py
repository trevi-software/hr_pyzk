# Copyright (C) 2022,2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    clock_device_user_id = fields.Many2one(
        "hr.attendance.clock.user", ondelete="restrict"
    )
