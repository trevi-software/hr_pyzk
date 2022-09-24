##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################


# from datetime import datetime
from odoo import models
from pytz import timezone, utc

from ..models import controller_pyzk as c


class UserWizard(models.TransientModel):
    _name = "user.wizard"

    def import_users(self):  # Import User for fur Import user Wizard
        device_object = self.env["hr.attendance.clock"]
        devices = device_object.search([])
        users_object = self.env["hr.attendance.clock.user"]
        odoo_users = users_object.search([])
        odoo_users_id = [user.device_user_id for user in odoo_users]

        for dev in devices:
            unique_data = c.DeviceUsers.get_users(dev)
            for user in unique_data:
                if int(user.user_id) not in odoo_users_id:
                    users_object.create(
                        {
                            "device_user_id": int(user.user_id),
                            "device_uid": user.uid,
                            "name": user.name,
                            "device_id": dev.id,
                        }
                    )

    def import_attendance(self):  # Import Attendance Wizard
        all_attendances = []
        all_attendances.clear()
        all_clocks = []
        all_clocks.clear()
        device_user_object = self.env["hr.attendance.clock.user"]
        device_users = device_user_object.search([])
        attendance_object = self.env["hr.attendance.clock.punch"]
        devices_object = self.env["hr.attendance.clock"]
        devices = devices_object.search([])
        for device in devices:
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

    def employee_attendance(self):  # combining employee attendances
        device_user_object = self.env["hr.attendance.clock.user"]
        device_attendances_object = self.env["hr.attendance.clock.punch"]
        odoo_users = device_user_object.search([])

        user_punches2 = []
        user_punches2.clear()
        all_attendance = []
        all_attendance.clear()
        attendance = []
        attendance.clear()

        for user in odoo_users:
            device_attendances = []
            device_attendances.clear()
            device_attendances = device_attendances_object.search(
                [
                    ("device_user_id", "=", user.id),
                    ("attendance_state", "=", "0"),
                ]
            )

            if len(device_attendances) != 0:
                user_punches = [
                    [
                        int(x.device_user_id),
                        x.device_datetime,
                        x.device_punch,
                    ]
                    for x in device_attendances
                ]
                user_punches.sort()
                attendance = c.DeviceUsers.outputresult(user_punches)
                user_punches2.extend(user_punches)
                all_attendance.extend(attendance)

                for record in device_attendances:
                    if record.attendance_state == "0":
                        record.attendance_state = "1"
        return all_attendance

    def combine_attendance(self):
        hr_attendance_object = self.env["hr.attendance"]
        valid_attendances = []
        valid_attendances.clear()
        valid_attendances = self.employee_attendance()
        punch_obj = self.env["hr.attendance.clock.punch"]
        for attendance in valid_attendances:
            punch_ids = punch_obj.search(
                [
                    ("device_user_id", "=", attendance[0]),
                    "|",
                    ("device_datetime", "=", attendance[1]),
                    ("device_datetime", "=", attendance[2]),
                ]
            )
            hr_attendance_object.create(
                {
                    "employee_id": punch_ids[0].employee_id.id,
                    "clock_punch_ids": [(4, p.id) for p in punch_ids],
                    "check_in": attendance[1],
                    "check_out": attendance[2],
                }
            )
