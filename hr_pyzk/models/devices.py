# Copyright (C) 2022,2023 TREVI Software
# Copyright (C) Sheikh M. Salahuddin <smsalah@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime
from odoo import api, fields, models
from pytz import common_timezones, timezone, utc

from . import controller_pyzk as c

logger = logging.getLogger(__name__)


class Devices(models.Model):

    _name = "hr.attendance.clock"
    _description = "Attendance Clock"

    @api.model
    def _tz_list(self):

        res = tuple()
        for name in common_timezones:
            res += ((name, name),)
        return res

    name = fields.Char(required=True)
    ip_address = fields.Char(required=True)
    port = fields.Integer(default=4370)
    sequence = fields.Integer()
    device_password = fields.Char()
    active = fields.Boolean(default=True)
    tz = fields.Selection(
        selection=_tz_list,
        required=True,
        string="Timezone",
        help="Timezone of attendance records read from the device.",
    )
    for_enrollment = fields.Boolean()
    device_name = fields.Char(readonly=True)
    device_serial = fields.Char(string="Serial no.", readonly=True)
    device_platform = fields.Char(readonly=True)
    device_firmware = fields.Char(string="Firmware ver.", readonly=True)
    device_fp_version = fields.Char(
        string="Fingerprint Algorithm ver.", readonly=True
    )
    device_mac = fields.Char(string="Hardware Address", readonly=True)
    device_datetime = fields.Datetime(
        compute="_compute_device_datetime", string="Device Time", readonly=True
    )
    device_users = fields.Integer(
        compute="_compute_device_users",
        string="Users",
        readonly=True
    )
    device_fingers = fields.Integer(
        compute="_compute_device_users",
        string="Fingerprints",
        readonly=True
    )
    device_records = fields.Integer(
        compute="_compute_device_users",
        string="Records",
        readonly=True
    )
    device_max_users = fields.Integer(string="Max Users", readonly=True)
    device_max_fingers = fields.Integer(string="Max Fingerprints", readonly=True)
    device_max_records = fields.Integer(string="Max Records", readonly=True)
    for_enrollment = fields.Boolean(help="The device is used for enrollment employees")
    for_attendance = fields.Boolean(help="The device is used for recording attendance")

    def _compute_device_datetime(self):
        for dev in self:
            try:
                conn = c.ConnectToDevice(
                    dev.ip_address, dev.port, dev.device_password, timeout=1
                )
            except Exception:
                dev.device_datetime = False
                continue
            # Odoo expects database datetime fields are in naive UTC
            dev.device_datetime = timezone(dev.tz) \
                .localize(conn.get_time())         \
                .astimezone(utc)                   \
                .replace(tzinfo=None)

    def _compute_device_users(self):
        for dev in self:
            try:
                conn = c.ConnectToDevice(
                    dev.ip_address, dev.port, dev.device_password, timeout=1
                )
            except Exception as ex:
                logger.error(f"unable to connect to clock device '{dev}: {ex}")
                dev.device_users = 0
                dev.device_fingers = 0
                dev.device_records = 0
            else:
                dev.device_users = conn.users
                dev.device_fingers = conn.fingers
                dev.device_records = conn.records

    def test_connection(self):
        with c.ConnectToDevice(
            self.ip_address, self.port, self.device_password
        ) as conn:
            if conn:
                self.device_name = conn.get_device_name()
                self.device_serial = conn.get_serialnumber()
                self.device_platform = conn.get_platform()
                self.device_firmware = conn.get_firmware_version()
                self.device_fp_version = conn.get_fp_version()
                self.device_mac = conn.get_mac()
                self.device_datetime = conn.get_time()
                self.device_users = conn.users
                self.device_max_users = conn.users_cap
                self.device_fingers = conn.fingers
                self.device_max_fingers = conn.fingers_cap
                self.device_records = conn.records
                self.device_max_records = conn.rec_cap
                return {
                    "effect": {
                        "fadeout": "slow",
                        "message": "The device connected successfuly.",
                        "type": "rainbow_man",

                    }
                }

    def sync_time(self):
        for dev in self:
            with c.ConnectToDevice(
                dev.ip_address, dev.port, dev.device_password
            ) as conn:
                if conn:
                    # Get current d/t as server tz then convert to device tz
                    dt = datetime.now()                 \
                        .astimezone()                   \
                        .astimezone(timezone(dev.tz))   \
                        .replace(tzinfo=None)
                    conn.set_time(dt)

    def sync_users(self, user_ids, update_templates=False):

        # If not in Odoo import from device
        # If on device update from odoo
        # If not on device add to device
        DeviceUsers = self.env["hr.attendance.clock.user"]
        odoo_users = DeviceUsers.search(
            [
                ("device_user_id", "in", user_ids),
            ]
        )
        odoo_user_ids = odoo_users.mapped("device_user_id")
        new_users = self.env["hr.attendance.clock.user"]
        update_users = self.env["hr.attendance.clock.user"]
        remove_users = self.env["hr.attendance.clock.user"]

        for dev in self:
            unique_data = c.DeviceUsers.get_users(dev)
            for user in unique_data:

                # Not in Odoo, import from device
                if int(user.user_id) not in odoo_user_ids:
                    res = DeviceUsers.create({
                            "device_user_id": int(user.user_id),
                            "device_uid": user.uid,
                            "name": user.name,
                            "device_id": dev.id,
                    })
                    if len(user["templates"]) > 0:
                        tobj = self.env["hr.attendance.clock.user.template"]
                        for i in range(len(user["templates"])):
                            if user["templates"][i] is not False:
                                tobj.create({
                                    "device_user_id": res.id,
                                    "sequence": i,
                                    "template": user["templates"][i]
                                })
                    new_users |= res

        return {
            "new_users": len(new_users),
            "updated_on_device": len(update_users),
            "removed_from_device": len(remove_users),
        }
