# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from psycopg2.errors import NotNullViolation

from odoo.exceptions import UserError
from odoo.tests import Form

from .test_common import TestClockCommon


class TestClockPunch(TestClockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ClockPunch = cls.env["hr.attendance.clock.punch"]

    def test_required_device_id(self):

        with self.assertRaises(NotNullViolation):
            self.ClockPunch.create({
                "device_user_id": 0,
                "device_datetime": datetime.now(),
                "device_punch": "0",
            })

    def test_required_device_user_id(self):

        with self.assertRaises(NotNullViolation):
            self.ClockPunch.create({
                "device_id": 0,
                "device_datetime": datetime.now(),
                "device_punch": "0",
            })

    def test_required_device_datetime(self):

        with self.assertRaises(NotNullViolation):
            self.ClockPunch.create({
                "device_id": 0,
                "device_user_id": 0,
                "device_punch": "0",
            })

    def test_required_device_punch(self):

        with self.assertRaises(NotNullViolation):
            self.ClockPunch.create({
                "device_id": 0,
                "device_user_id": 0,
                "device_datetime": datetime.now(),
            })

    def test_related_employee_id(self):

        clock = self.new_clock("Clock A", "192.168.1.1")
        employee, clock_user = self.new_employee_with_clock_user("Alice")
        punch = Form(self.env["hr.attendance.clock.punch"])
        punch.device_datetime = datetime.now()
        punch.device_punch = "0"
        punch.device_id = clock
        punch.device_user_id = clock_user
        punch = punch.save()

        self.assertEqual(
            punch.employee_id,
            employee,
            "Creating a new punch sets the related employee_id field"
        )

    def test_attendance_id_ondelete(self):
        clock = self.new_clock("A", "10.0.0.1")
        ee, clock_user = self.new_employee_with_clock_user("Bob")
        punch = self.ClockPunch.create({
            "device_id": clock.id,
            "device_user_id": clock_user.id,
            "device_datetime": datetime.now(),
            "device_punch": "0",
        })
        punch.create_check_in_attendance()
        self.assertEqual(
            punch.attendance_state, "1", "Punch has been recorded"
        )
        self.assertTrue(punch.attendance_id, "Punch has an hr.attendance record")

        punch.attendance_id.unlink()
        self.assertEqual(
            punch.attendance_state, "0", "Punch has NOT been recorded"
        )
        self.assertFalse(punch.error_state, "The Punch's error state is cleared")
        self.assertFalse(punch.attendance_id, "Punch attendance_id is set to NULL")

    def test_unlink_after_attendance_created(self):
        clock = self.new_clock("A", "10.0.0.1")
        ee, clock_user = self.new_employee_with_clock_user("Bob")
        punch = self.ClockPunch.create({
            "device_id": clock.id,
            "device_user_id": clock_user.id,
            "device_datetime": datetime.now(),
            "device_punch": "0",
        })
        punch.create_check_in_attendance()
        self.assertEqual(
            punch.attendance_state, "1", "Punch has been recorded"
        )
        self.assertTrue(punch.attendance_id, "Punch has an hr.attendance record")

        with self.assertRaises(UserError):
            punch.unlink()
