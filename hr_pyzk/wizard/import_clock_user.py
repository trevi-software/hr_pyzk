# Copyright (C) 2022,2023 TREVI Software
# Copyright (C) Sheikh M. Salahuddin <smsalah@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..models import controller_pyzk as c

import logging
logger = logging.getLogger(__name__)


class ImportClockUser(models.TransientModel):
    _name = "wizard.import.clock.user"
    _description = "Wizard to import attendance clock users"

    for_enrollment_only = fields.Boolean(default=True)
    clock_ids = fields.Many2many(
        comodel_name="hr.attendance.clock",
        string="Clocks",
        domain=[('for_enrollment', '=', True)]
    )

    def import_users(self):  # Import User for fur Import user Wizard
        users_object = self.env["hr.attendance.clock.user"]
        tobj = self.env["hr.attendance.clock.user.template"]
        odoo_users = users_object.search([])
        odoo_users_id = [user.device_user_id for user in odoo_users]

        for dev in self.clock_ids:
            with c.ConnectToDevice(
                dev.ip_address, dev.port, dev.device_password
            ) as connection:
                unique_data, templates = connection.get_users(with_templates=True)
                for user in unique_data:
                    if int(user.user_id) not in odoo_users_id:
                        dev_user = users_object.create({
                                "device_user_id": int(user.user_id),
                                "device_uid": user.uid,
                                "name": user.name,
                                "device_id": dev.id,
                        })
                        for i in range(len(templates[user.uid]["templates"])):
                            if templates[user.uid]["templates"][i] is not False:
                                tobj.create({
                                    "device_user_id": dev_user.id,
                                    "sequence": i,
                                    "template": templates[user.uid]["templates"][i]
                                })

        return self.env.ref("hr_pyzk.device_users_action").read()[0]
