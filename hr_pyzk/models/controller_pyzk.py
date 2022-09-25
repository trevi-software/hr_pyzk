from genericpath import exists
from odoo import exceptions
from zk import ZK


class DeviceUsers:
    def get_users(devices):
        all_users = []
        all_users.clear()
        for device in devices:
            with ConnectToDevice(
                device.ip_address, device.port, device.device_password
            ) as conn:
                users = conn.get_users()
                all_users.extend(users)
                added = []
                added.clear()
                unique_data = []
                unique_data.clear()
                for user in all_users:
                    if int(user.user_id) not in added:
                        added.append(int(user.user_id))
                        added.sort()
                        unique_data.append(user)
        return unique_data

    def get_attendance(device):
        """
        Function uses to get attendances
        """

        with ConnectToDevice(
            device.ip_address, device.port, device.device_password
        ) as conn:
            attendances = conn.get_attendance()
            device_attendance = [
                [x.user_id, x.timestamp, x.punch, device.id] for x in attendances
            ]

        return device_attendance

    def outputresult(self):

        user_clock = []
        user_clock.clear()
        user_attendance = []
        user_attendance.clear()
        initial_number = 1

        for clock in self:
            if clock[2] == initial_number:
                initial_number = clock[2]
            else:
                user_clock.append(clock)
                initial_number = clock[2]

        if len(user_clock) != 0 and user_clock[-1][2] == 0:
            del user_clock[-1]

        user_attendance = [
            [i[0], i[1], j[1]] for i, j in zip(user_clock[::2], user_clock[1::2])
        ]

        return user_attendance


class ConnectToDevice(object):
    """
    Class uses to assure connetion to a device and closing of the same
    It is using to disable the device when it is been reading or busy
    """

    def __init__(self, ip_address, port, device_password, timeout=10):

        self.conn = None
        self.users = 0
        self.fingers = 0
        self.users_cap = 0
        self.fingers_cap = 0
        try:
            zk = ZK(
                ip_address,
                port,
                timeout=timeout,
                password=device_password,
                ommit_ping=True
            )
            conn = zk.connect()

        except Exception as e:
            raise exceptions.Warning(e)

        conn.disable_device()
        self.conn = conn
        conn.read_sizes()
        self.users = conn.users
        self.fingers = conn.fingers
        self.users_cap = conn.users_cap
        self.fingers_cap = conn.fingers_cap
        self.records = conn.records
        self.rec_cap = conn.rec_cap

    def __del__(self):
        self._enable_and_disconnect()

    def __enter__(self):
        """
        return biometric connection
        """
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        enable device and close connection
        """
        self._enable_and_disconnect()

    def _enable_and_disconnect(self):
        if self.conn:
            self.conn.enable_device()
            self.conn.disconnect()
            self.conn = None

    def get_device_name(self):
        return self.conn.get_device_name()

    def get_serial(self):
        return self.conn.get_serialnumber()

    def get_firmware(self):
        return self.conn.get_firmware_version()

    def get_platform(self):
        return self.conn.get_platform()

    def get_fp_version(self):
        return self.conn.get_fp_version()

    def get_mac(self):
        return self.conn.get_mac()

    def get_time(self):
        return self.conn.get_time()

    def set_time(self, dt):
        return self.conn.set_time(dt)
