# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestClockCommon(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.HrEmployee = cls.env["hr.employee"]
        cls.Clock = cls.env["hr.attendance.clock"]
        cls.ClockUser = cls.env["hr.attendance.clock.user"]

    def new_employee(self, name):
        return self.HrEmployee.create({"name": name})

    def new_clock_user(self, name):
        return self.ClockUser.create({
            "name": name,
        })

    def new_employee_with_clock_user(self, name):
        employee = self.new_employee(name)
        clock_user = self.new_clock_user(name)
        clock_user.employee_id = employee
        employee.clock_user_id = clock_user

        return (employee, clock_user)

    def new_clock(self, name, ip_address, tz="UTC", for_enrollment=False):

        values = {
            "name": name,
            "ip_address": ip_address,
            "tz": tz,
        }

        updates = {}
        if for_enrollment is True:
            updates.update({"for_enrollment": True})
        values.update(updates)

        return self.Clock.create(values)
