from datetime import datetime, tzinfo
from odoo import api, fields, models
from pytz import common_timezones, timezone, utc

from . import controller_pyzk as c


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
    ip_address = fields.Char()
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
    device_name = fields.Char(readonly=True)
    device_serial = fields.Char(string="Serial no.", readonly=True)
    device_platform = fields.Char(readonly=True)
    device_firmware = fields.Char(string="Firmware ver.", readonly=True)
    device_fp_version = fields.Char(string="Fingerprint Algorithm ver.", readonly=True)
    device_mac = fields.Char(string="Hardware Address", readonly=True)
    device_datetime = fields.Datetime(
        compute="_compute_device_datetime", string="Device Time", readonly=True
    )

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
