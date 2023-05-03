# Copyright (C) 2022,2023 TREVI Software
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    clock_punch_ids = fields.One2many(
        "hr.attendance.clock.punch", "attendance_id", "Clock Punches"
    )

    # originally copied _check_validity() from odoo/addons/model/hr_attendance.py
    # I've modified it to return a meaningful error instead of rasing exceptions.
    #
    @api.model
    def check_conflicting_attendance(self, employee_id, check_in, check_out=None):
        """ Verifies the validity of the attendance record compared to the others
            for the same employee. For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
            Returns a containing two fields:
                "result" - string containing one of four values:
                    None                        - no conflicts were detected
                    "overlap_on_checkin"        - the check-in time straddles another
                                                  attendance
                    "multiple_open_attendances" - there is another "open" attendance
                    "overlap_on_checkout"       - the check-out time straddles
                                                  another attendance
                "hr_attendance" - the 'hr.attendance' record conflicting with the
                                  propsed employee_id's check-in/check-out times
        """

        res = {
            "result": None,
            "hr_attendance": None,
        }

        last_attendance_before_check_in = self.env['hr.attendance'].search([
            ('employee_id', '=', employee_id),
            ('check_in', '<=', check_in),
        ], order='check_in desc', limit=1)
        if last_attendance_before_check_in                    \
                and last_attendance_before_check_in.check_out \
                and last_attendance_before_check_in.check_out > check_in:
            res["result"] = "overlap_on_checkin"
            res["hr_attendance"] = last_attendance_before_check_in

        if check_out is None:
            no_check_out_attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee_id),
                ('check_out', '=', False),
            ], order='check_in desc', limit=1)
            if no_check_out_attendances:
                res["result"] = "multiple_open_attendances"
                res["hr_attendance"] = no_check_out_attendances
        else:
            last_attendance_before_check_out = self.env['hr.attendance'].search([
                ('employee_id', '=', employee_id),
                ('check_in', '<', check_out),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_out \
                    and last_attendance_before_check_in != last_attendance_before_check_out:  # noqa
                res["result"] = "overlap_on_checkout"
                res["hr_attendance"] = last_attendance_before_check_out

        return res
