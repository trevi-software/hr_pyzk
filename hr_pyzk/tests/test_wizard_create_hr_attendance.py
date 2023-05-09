# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .test_common import TestClockCommon


class TestCreateHrAttendance(TestClockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
