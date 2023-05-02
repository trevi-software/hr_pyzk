# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from psycopg2.errors import NotNullViolation

from .test_common import TestClockCommon


class TestClockPunch(TestClockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ClockPunch = cls.env["hr.attendance.clock.punch"]

    def test_required_fields(self):

        ee_alice = self.new_employee("Alice")
        invalid_cases = [
            (
                {
                    "device_user_id": 0,
                    "device_datetime": datetime.now(),
                    "device_punch": "0",
                    "employee_id": ee_alice.id,
                },
                NotNullViolation,
                "missing device_id",
            ),
            (
                {
                    "device_id": 0,
                    "device_datetime": datetime.now(),
                    "device_punch": "0",
                    "employee_id": ee_alice.id,
                },
                NotNullViolation,
                "missing device_user_id",
            ),
            (
                {
                    "device_id": 0,
                    "device_user_id": 0,
                    "device_punch": "0",
                    "employee_id": ee_alice.id,
                },
                NotNullViolation,
                "missing device_datetime",
            ),
            (
                {
                    "device_id": 0,
                    "device_user_id": 0,
                    "device_datetime": datetime.now(),
                    "employee_id": ee_alice.id,
                },
                NotNullViolation,
                "missing device_punch",
            ),
            (
                {
                    "device_id": 0,
                    "device_user_id": 0,
                    "device_datetime": datetime.now(),
                    "device_punch": "0",
                },
                NotNullViolation,
                "missing employee_id",
            ),
        ]

        for values, ex, msg in invalid_cases:
            with self.assertRaises(ex, msg):
                self.ClockUser.create(values)
