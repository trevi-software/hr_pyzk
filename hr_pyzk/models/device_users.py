from odoo import _, exceptions, fields, models
from zk import const

from . import controller_pyzk as c


class DeviceUsers(models.Model):
    _name = "device.users"
    _order = "device_user_id"

    device_user_id = fields.Integer("Device User ID")
    device_uid = fields.Integer(
        "Device UID"
    )  # uid in the device. Important to delete user in the future
    name = fields.Char("Device User Name")
    employee_id = fields.Many2one("hr.employee", "Related employee")
    device_id = fields.Many2one("hr.attendance.clock", "Clock Device")

    _sql_constraints = [
        (
            "employee_id_uniq",
            "unique (employee_id)",
            "It is not possible to relate an employee with a pyzk user "
            "more than once!",
        ),
    ]

    _sql_constraints = [
        (
            "device_user_id_uniq",
            "unique (device_user_id)",
            "It is not possible to create more than one user "
            "with the same device_user_id",
        ),
    ]

    def create_user(self):
        """
        Function uses to get attendances
        """
        ip_address = self.device_id.ip_address
        port = self.device_id.port
        device_password = self.device_id.device_password
        user_id = str(self.device_user_id)

        with c.ConnectToDevice(ip_address, port, device_password) as conn:

            device_users = conn.get_users()
            device_user_ids = [int(x.user_id) for x in device_users]
            if self.device_user_id not in device_user_ids:
                conn.set_user(
                    uid=self.device_user_id,
                    name=self.name,
                    privilege=const.USER_DEFAULT,
                    user_id=user_id,
                )
                self.device_uid = self.device_user_id
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "device.users",
                    "views": [[False, "form"]],
                    "res_id": self.id,
                    "target": "main",
                    "context": {"show_message1": True},
                }

            else:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "device.users",
                    "views": [[False, "form"]],
                    "res_id": self.id,
                    "target": "main",
                    "context": {"show_message2": True},
                }

    def edit_user(self):
        """
        Function uses to get attendances
        """
        ip_address = self.device_id.ip_address
        port = self.device_id.port
        device_password = self.device_id.device_password

        if self.device_id.id is False:
            raise exceptions.Warning(_("Fingerprint device is not selected"))

        with c.ConnectToDevice(ip_address, port, device_password) as conn:

            try:
                conn.set_user(
                    uid=self.device_user_id,
                    name=self.name,
                    privilege=const.USER_DEFAULT,
                    user_id=str(self.device_user_id),
                )
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "device.users",
                    "views": [[False, "form"]],
                    "res_id": self.id,
                    "target": "main",
                    "context": {"show_message3": True},
                }

            except Exception:
                raise exceptions.Warning(_("User does not exist in the device"))
            # else:
            #     return {
            #         "type": "ir.actions.act_window",
            #         "res_model": "device.users",
            #         "views": [[False, "form"]],
            #         "res_id": self.id,
            #         "target": "main",
            #         "context": {'show_message4': True},
            #     }
