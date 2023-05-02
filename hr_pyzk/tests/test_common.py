# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestClockCommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.HrEmployee = cls.env["hr.employee"]

    def new_employee(self, name):
        return self.HrEmployee.create({"name": name})
