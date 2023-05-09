# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from .test_common import TestClockCommon


class TestClockImportUser(TestClockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ImportUserWiz = cls.env["wizard.import.clock.user"]
