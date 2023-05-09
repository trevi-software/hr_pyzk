# Part of Odoo. See LICENSE file for full copyright and licensing details.

# pylint: disable=pointless-statement
{
    "name": "ZKTeco Biometric Attendance",
    "version": "14.0.1.0.0",
    "category": "Human Resources",
    "summary": "Employee Attendance using ZKTeco Time & Attendance devices.",
    "author": "Sheikh M. Salahuddin, TREVI Software",
    "license": "GPL-3",
    "images": ["static/src/img/main_screenshot.png"],
    "website": "https://github.com/trevi-software/trevi-hr",
    "depends": ["hr", "hr_attendance"],
    "external_dependencies": {
        "python": ["pyzk"],
    },
    "data": [
        "views/hr_pyzk_views.xml",
        "views/device_users_view.xml",
        "views/devices_view.xml",
        "views/device_attendances_view.xml",
        "views/hr_attendance_view.xml",
        "wizard/import_clock_user.xml",
        "wizard/import_clock_punch.xml",
        "wizard/convert_clock_punch.xml",
        "wizard/delete_attendance_wizard_view.xml",
        "security/pyzk_security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
