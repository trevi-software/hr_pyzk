# Copyright (C) 2022,2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BiometricId(models.Model):
    _name = "hr.attendance.clock.user.biometric"
    _description = "Biometric identifier for Attendance Clock User"

    device_user_id = fields.Many2one("hr.attendance.clock.user")
    type = fields.Selection(
        selection=[
            ("finger", "Fingerprint"),
            ("face", "Faceprint"),
        ]
    )
    faceprint = fields.Binary(attachment=False)
    fingerprint_0 = fields.Binary(attachement=False)
    fingerprint_1 = fields.Binary(attachement=False)
    fingerprint_2 = fields.Binary(attachement=False)
    fingerprint_3 = fields.Binary(attachement=False)
    fingerprint_4 = fields.Binary(attachement=False)
    fingerprint_5 = fields.Binary(attachement=False)
    fingerprint_6 = fields.Binary(attachement=False)
    fingerprint_7 = fields.Binary(attachement=False)
    fingerprint_8 = fields.Binary(attachement=False)
    fingerprint_9 = fields.Binary(attachement=False)
