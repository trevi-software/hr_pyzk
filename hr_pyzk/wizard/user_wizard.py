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
        users_object = self.env["device.users"]
        odoo_users = users_object.search([])
        odoo_users_id = [user.device_user_id for user in odoo_users]
        unique_data = c.DeviceUsers.get_users(devices)

        for user in unique_data:
            if int(user.user_id) not in odoo_users_id:
                users_object.create(
                    {
                        "device_user_id": int(user.user_id),
                        "device_uid": user.uid,
                        "name": user.name,
                    }
                )

    def import_attendance(self):  # Import Attendance Wizard
        all_attendances = []
        all_attendances.clear()
        all_clocks = []
        all_clocks.clear()
        device_user_object = self.env["device.users"]
        device_users = device_user_object.search([])
        attendance_object = self.env["device.attendances"]
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
                    "device_datetime": device_tz.localize(a[1], is_dst=False)
                    .astimezone(utc)
                    .replace(tzinfo=None),
                    "device_punch": str(a[2]),
                    # 'repeat': a[4],
                    "attendance_state": "0",
                    "device_id": a[3],
                }
            )

    def employee_attendance(self):  # combining employee attendances
        device_user_object = self.env["device.users"]
        device_attendances_object = self.env["device.attendances"]
        odoo_users = device_user_object.search([])

        user_punches2 = []
        user_punches2.clear()
        all_attendance = []
        all_attendance.clear()
        user_clocks = []
        user_clocks.clear()
        attendance = []
        attendance.clear()
        # clock = []
        # clock.clear()

        for user in odoo_users:
            device_attendances = []
            device_attendances.clear()
            device_attendances = device_attendances_object.search(
                [("device_user_id", "=", user.id), ("attendance_state", "=", "0")]
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
                # user_clocks.extend(clock)

                for record in device_attendances:
                    if record.attendance_state == "0":
                        record.attendance_state = "1"
        return all_attendance

    def combine_attendance(self):
        combined_attendances_object = self.env["combined.attendances"]
        valid_attendances = []
        valid_attendances.clear()
        valid_attendances = self.employee_attendance()
        for attendance in valid_attendances:
            combined_attendances_object.create(
                {
                    "device_user_id": int(attendance[0]),
                    "device_date": attendance[1].date(),
                    "device_clockin": attendance[1],
                    "device_clockout": attendance[2],
                }
            )

    def transfer_attendance(self):
        combined_attendance_object = self.env["combined.attendances"]
        hr_attendance_object = self.env["hr.attendance"]
        all_data = combined_attendance_object.search(
            [("state", "=", "not_transferred"), ("employee_id", "!=", False)]
        )

        for attendance in all_data:
            hr_attendance_object.create(
                {
                    "employee_id": attendance.employee_id.id,
                    "check_in": attendance.device_clockin,
                    "check_out": attendance.device_clockout,
                }
            )

            attendance.state = "transferred"
