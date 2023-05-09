# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from pytz import timezone, utc

from ..models import controller_pyzk as c

import logging
logger = logging.getLogger(__name__)


class ConvertClockPunch(models.TransientModel):
    _name = "wizard.convert.clock.punch"
    _description = "Wizard to convert clock punches to attendance records"

    @api.model
    def _default_clock_punch_ids(self):
        punches = self.env["hr.attendance.clock.punch"].search(
            [("attendance_id", "=", False)]
        )
        print(f"punch_ids: {punches}")
        return punches
        # ids = [p.id for p in punches]
        # self.clock_punch_ids = [(6, 0, ids)]

    clock_punch_ids = fields.Many2many(
        comodel_name="hr.attendance.clock.punch",
        string="Clock Punches",
        default=_default_clock_punch_ids,
    )

    def convert_to_attendance(self):
        clock_users = self.clock_punch_ids.mapped("device_user_id")
        clock_users.create_hr_attendance()

        action = self.env.ref("hr_pyzk.device_attendances_action").read()[0]
        return action
