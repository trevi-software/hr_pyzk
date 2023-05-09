# Copyright (C) 2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.errors import NotNullViolation

from odoo import api, registry

from .test_common import TestClockCommon


class TestClock(TestClockCommon):

    def test_required_name(self):

        with self.assertRaises(NotNullViolation):
            self.Clock.create({
                "ip_address": "10.0.0.1",
                "tz": "UTC",
            })

    def test_required_ip_address(self):

        with self.assertRaises(NotNullViolation):
            self.Clock.create({
                "name": "Example",
                "tz": "UTC",
            })

    def test_required_tz(self):

        with self.assertRaises(NotNullViolation):
            self.Clock.create({
                "name": "Example",
                "ip_address": "10.0.0.1",
            })

    def test_defaults(self):

        clock = self.new_clock("Clock A", "192.168.1.1")

        self.assertEqual(
            clock.port,
            4370,
            "By default the clock IP port is 4370"
        )

        self.assertTrue(
            clock.active,
            "By default a clock should be active"
        )
