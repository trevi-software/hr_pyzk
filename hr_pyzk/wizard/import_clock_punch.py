# Copyright (C) 2022,2023 TREVI Software
# Copyright (C) Sheikh M. Salahuddin <smsalah@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from pytz import timezone, utc

from ..models import controller_pyzk as c

import logging
logger = logging.getLogger(__name__)


class ImportClockPunch(models.TransientModel):
    _name = "wizard.import.clock.punch"
    _description = "Wizard to import attendance clock punches"

    only_attendance_clocks = fields.Boolean(default=True)
    clock_ids = fields.Many2many(
        comodel_name="hr.attendance.clock",
        domain=[("for_attendance", "=", True)]
    )

    def import_punches(self):  # Import Attendance Wizard
        all_attendances = []
        all_attendances.clear()
        all_clocks = []
        all_clocks.clear()
        device_user_object = self.env["hr.attendance.clock.user"]
        device_users = device_user_object.search([])
        attendance_object = self.env["hr.attendance.clock.punch"]
        for device in self.clock_ids:
            device_tz = timezone(device.tz)
            attendances = c.DeviceUsers.get_attendance(device)
            latest_rec = attendance_object.search(
                [("device_id", "=", device.id)], limit=1
            )
            if latest_rec:
                latest_datetime = (
                    utc.localize(latest_rec.device_datetime, is_dst=False)
                    .astimezone(device_tz)
                    .replace(tzinfo=None)
                )

                all_attendances = [
                    [y.id, x[1], x[2], x[3]]
                    for x in attendances
                    for y in device_users
                    if int(x[0]) == y.device_user_id
                    and x[2] <= 1
                    and x[1] > latest_datetime
                ]
            else:

                all_attendances = [
                    [y.id, x[1], x[2], x[3]]
                    for x in attendances
                    for y in device_users
                    if int(x[0]) == y.device_user_id and x[2] <= 1
                ]
            all_clocks.extend(all_attendances)

        for a in all_clocks:
            attendance_object.create(
                {
                    "device_user_id": int(a[0]),
                    "device_datetime":
                    device_tz.localize(a[1], is_dst=False)
                        .astimezone(utc)
                        .replace(tzinfo=None),
                    "device_punch": str(a[2]),
                    "attendance_state": "0",
                    "device_id": a[3],
                }
            )

        return self.env.ref("hr_pyzk.device_attendances_action").read()[0]
