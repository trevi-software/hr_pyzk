# Copyright (C) 2022 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    clock_punch_ids = fields.One2many(
        "hr.attendance.clock.punch", "attendance_id", "Clock Punches"
    )
