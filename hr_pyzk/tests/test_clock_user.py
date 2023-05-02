# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.errors import NotNullViolation

from .test_common import TestClockCommon


class TestClockUser(TestClockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ClockUser = cls.env["hr.attendance.clock.user"]

    def test_required_fields(self):

        invalid_cases = [
            (
                {
                    "state": "linked",
                },
                NotNullViolation,
                "missing name",
            ),
            (
                {
                    "name": "Alice",
                },
                NotNullViolation,
                "missing state",
            ),
        ]

        for values, ex, msg in invalid_cases:
            with self.assertRaises(ex, msg):
                self.ClockUser.create(values)

    def test_create_from_employee(self):

        ee_alice = self.new_employee("Alice")
        device_user = ee_alice.create_clock_device_user()

        self.assert_true(
            device_user.id,
            "A clock device user was successfully created"
        )
        self.assert_eq(
            device_user.state,
            "linked",
            "The clock device user has the correct state"
        )
