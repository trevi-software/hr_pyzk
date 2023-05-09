# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.errors import NotNullViolation

from .test_common import TestClockCommon


class TestImportClockPunch(TestClockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ImportPunchWiz = cls.env["wizard.import.device.punch"]
