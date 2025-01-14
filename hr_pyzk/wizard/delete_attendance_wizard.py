##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from odoo import _, exceptions, fields, models

from ..models import controller_pyzk as c


class DeleteAttendanceWizard(models.TransientModel):
    _name = "delete.attendance.wizard"

    device_id = fields.Many2one(
        "hr.attendance.clock",
        "Clock Device",
    )

    def delete_attendance(self):

        with c.ConnectToDevice(
            self.device_id.ip_address,
            self.device_id.port,
            self.device_id.device_password,
        ) as conn:
            conn.clear_attendance()
            raise exceptions.Warning(_("Attendances deleted successfully"))
