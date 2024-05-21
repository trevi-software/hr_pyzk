# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .test_common import TestClockCommon


class TestHrEmployee(TestClockCommon):

    def test_create_clock_user(self):

        ee_alice = self.new_employee("Alice")
        device_user = ee_alice.create_clock_user()

        self.assertTrue(
            device_user.id,
            "A clock user was successfully created"
        )
        self.assertEqual(
            device_user.state,
            "odoo",
            "The clock user has the correct state"
        )

    def test_duplicate_clock_user(self):
        ee, clock_user = self.new_employee_with_clock_user("Bob")
        ee.clock_user_id = False

        with self.assertRaises(ValidationError):
            ee.create_clock_user()

    def test_skip_if_clock_user_exists(self):
        ee, clock_user = self.new_employee_with_clock_user("Bob")
        original_clock_user_id = clock_user.id
        self.assertEqual(
            ee.clock_user_id,
            clock_user,
            "Employee is linked with a clock user record"
        )

        clock_user = ee.create_clock_user()

        self.assertEqual(len(clock_user), 0, "No record was created")
        self.assertEqual(
            ee.clock_user_id.id,
            original_clock_user_id,
            "the call to create a clock user was a NOP"
        )

    def test_fingerprint_count_matches_clock_user(self):
        ee, clock_user = self.new_employee_with_clock_user("Bob")
        self.fail()
