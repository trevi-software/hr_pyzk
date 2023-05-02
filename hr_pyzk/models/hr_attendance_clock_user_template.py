# Copyright (C) 2022,2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UserTemplate(models.Model):

    _name = "hr.attendance.clock.user.template"
    _description = "Attendance Clock User Fingerprint"

    device_user_id = fields.Many2one("hr.attendance.clock.user", index=True)
    sequence = fields.Integer(
        string="Finger Template Index",
    )
    template = fields.Binary(attachment=False)
