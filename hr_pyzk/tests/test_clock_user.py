# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.errors import ForeignKeyViolation, NotNullViolation

from .test_common import TestClockCommon


class TestClockUser(TestClockCommon):

    def test_required_name(self):

        with self.assertRaises(NotNullViolation):
            self.ClockUser.create({
                "state": "odoo",
            })

    def test_defaults(self):

        user = self.ClockUser.create({"name": "Bob"})
        self.assertEqual(
            user.state,
            "device",
            "By default the clock user is in 'Imported' state"
        )

    def test_employee_ondelete(self):
        ee, clock_user = self.new_employee_with_clock_user("Bob")
        with self.assertRaises(ForeignKeyViolation):
            ee.unlink()

    def test_create_employee(self):
        users = self.new_clock_user("Alice")
        users |= self.new_clock_user("Bob")
        employees = users.create_hr_employee()

        self.assertEqual(len(employees), 2, "Two hr.employee records were created")
        self.assertEqual(
            employees[0].name,
            "Alice",
            "The first employees name maches the clock user's name"
        )
        self.assertEqual(
            employees[1].name,
            "Bob",
            "The first employees name maches the clock user's name"
        )
        self.assertEqual(
            employees[0].clock_user_id.id,
            users[0].id,
            "The first employee points to the correct clock user"
        )
        self.assertEqual(
            employees[1].clock_user_id.id,
            users[1].id,
            "The second employee points to the correct clock user"
        )
        self.assertEqual(
            users[0].employee_id.id,
            employees[0].id,
            "The first clock user points to the correct employee"
        )
        self.assertEqual(
            users[1].employee_id.id,
            employees[1].id,
            "The second clock user points to the correct employee"
        )

    def test_skip_if_already_linked(self):
        ee, user = self.new_employee_with_clock_user("Charlie")
        ee_count = self.HrEmployee.search_count([])
        original_ee_id = user.employee_id.id
        user.create_hr_employee()

        ee_count_new = self.HrEmployee.search_count([])
        self.assertEqual(ee_count_new, ee_count, "Num. of employees remains constant")
        self.assertEqual(
            user.employee_id.id,
            original_ee_id,
            "The Clock User is still linked to the employee")
