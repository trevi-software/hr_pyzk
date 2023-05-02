# Copyright (C) 2022,2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UserDevicePrivilege(models.Model):

    _name = "hr.attendance.clock.user.privilege"
    _description = "User Clock Device Privilege Mapping"

    device_user_id = fields.Many2one("hr.attendance.clock.user")
    device_id = fields.Many2one("hr.attendance.clock")
    privilege = fields.Selection(
        selection=[
            ("default", "Default"),
            ("enroller", "Enroller"),
            ("manager", "Manager"),
            ("admin", "Admin"),
        ],
    )
