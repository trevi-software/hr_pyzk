from odoo import api, fields, models
from pytz import common_timezones

from ..controllers import controller as c


class Devices(models.Model):

    _name = "devices"

    @api.model
    def _tz_list(self):

        res = tuple()
        for name in common_timezones:
            res += ((name, name),)
        return res

    name = fields.Char(string="Device Name")
    ip_address = fields.Char(string="Ip address")
    port = fields.Integer(string="Port", default=4370)
    sequence = fields.Integer(string="Sequence")
    device_password = fields.Char(string="Device Password")
    state = fields.Selection(
        [("0", "Active"), ("1", "Inactive")], string="Status", default="1"
    )
    tz = fields.Selection(
        selection=_tz_list,
        required=True,
        string="Timezone",
        help="Timezone of the device",
    )

    def test_connection(self):
        with c.ConnectToDevice(
            self.ip_address, self.port, self.device_password
        ) as conn:
            if conn:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "devices",
                    "views": [[False, "form"]],
                    "res_id": self.id,
                    "target": "main",
                    "context": {"show_message1": True},
                }
