"""
License:
--------
Copyright 2022 Tangi0 Ltd. (trading as TG0)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


File description:
-----------------
Main file for package: etee.
Classes and methods for eteeController events, communication and data retrieval.

"""

import os
import time

from .tangio_for_etee import TG0Driver, serial_ports, parse_utf8
from . import Ahrs

ETEE_CONTROLLER_DATA_CONFIG = os.path.join(os.path.dirname(__file__), "config", "etee_controller.yaml")


class EteeControllerEvent:
    """
    This class manages eteeController driver events by allowing callback functions to be connected or disconnected from them.
    """
    def __init__(self):
        """
        Class constructor method.
        """
        self.callbacks = list()

    def connect(self, callback):
        """
        Connect a callback function to the event.

        :param callable callback: Callback function.
        """
        self.callbacks.append(callback)

    def disconnect(self, callback):
        """
        Remove a function from the event callbacks.

        :param callable callback: Callback function.
        """
        self.callbacks.remove(callback)

    def emit(self):
        """
        Emit event.
        """
        for cb in self.callbacks:
            cb()


class EteeController:
    """
    This class manages the communication between the driver and the eteeControllers, through the eteeDongle.
    It also handles the data loop which retrieves and stores the eteeControllers data into an internal buffer,
    allowing for their retrieval through its class methods.
    """
    ETEE_DONGLE_VID = 9114
    ETEE_DONGLE_PID = None

    def __init__(self):
        """
        Class constructor method.
        """
        self._hand_last_on_left = 0
        self._hand_last_on_right = 0
        self._api_data_left = None
        self._api_data_right = None
        self._frameno_left = 0
        self._frameno_right = 0
        self._ahrs_left = Ahrs()
        self._ahrs_right = Ahrs()
        self._quaternion_left = None
        self._quaternion_right = None
        self._absolute_imu_on = False
        self._euler_left = None
        self._euler_right = None

        self.driver = TG0Driver(ETEE_CONTROLLER_DATA_CONFIG)
        self.driver.add_callback(self._api_data_callback)
        self.driver.add_print_callback(self._print_callback)
        self.driver.add_serial_exception_callbacks(self._serial_exception_callback)

        self.connection_port = None
        self.dongle_connection = False

        # ---------------- Events ----------------
        self.left_hand_received = EteeControllerEvent()
        """Event for receiving left controller data.
        
        :type: Event """

        self.right_hand_received = EteeControllerEvent()
        """Event for receiving right controller data.
        
        :type: Event """

        self.hand_received = EteeControllerEvent()
        """Event for receiving data from any controller.

        :type: Event """

        self.left_hand_lost = EteeControllerEvent()
        """Event for losing left controller connection. Occurs when data is not received for more than 0.5 seconds.
        
        :type: Event """

        self.right_hand_lost = EteeControllerEvent()
        """Event for losing right controller connection. Occurs when data is not received for more than 0.5 seconds.
        
        :type: Event """

        self.data_lost = EteeControllerEvent()
        """Event for losing data from both controllers. Occurs when data is not received for more than 0.5 seconds.
        
        :type: Event """

        self.left_connected = EteeControllerEvent()
        """Event for left controller connection detected by the dongle.
        
        :type: Event """

        self.right_connected = EteeControllerEvent()
        """Event for right controller connection detected by the dongle.
        
        :type: Event """

        self.left_disconnected = EteeControllerEvent()
        """Event for left controller disconnection from the dongle.
        
        :type: Event """

        self.right_disconnected = EteeControllerEvent()
        """Event for right controller disconnection from the dongle.
        
        :type: Event """

        self.dongle_disconnected = EteeControllerEvent()
        """Event for dongle disconnection.
        
        :type: Event """

    # ---------------- Utility ----------------
    def connect_port(self, port=None):
        """
        Attempt to establish serial connection to an etee dongle port. If a COM port argument is provided,
        connection is attempted with the specified port. If the port argument is None, the driver automatically detects
        any COM ports with an etee dongle and connects to the first available one. Default port value is None.

        :param str or None port: etee dongle COM port.
        :return: Success flag - True if the connection is successful, False if otherwise
        :rtype: bool
        """
        if port[0:3] == 'COM':
            return self.driver.connect(port)
        else:
            raise ValueError("The port value should be of the form 'COMx', where x is the COM port number.")

    def connect(self):
        """
        Establish serial connection to an etee dongle. This function automatically detects etee dongles connected to a COM port
        and connects to the first available one.
        """
        available_ports = self.get_available_etee_ports()
        print("The following ports found: {}".format(available_ports))
        if len(available_ports) > 0:
            port = available_ports[0]
            connected = self.connect_port(port)
            if connected:
                self.connection_port = port
                self.dongle_connection = True
                print("Connection to etee dongle successful.")
            else:
                self.connection_port = None
                self.dongle_connection = False
                print("Connection to etee dongle unsuccessful.")
        else:
            self.dongle_connection = False

    def get_number_available_etee_ports(self):
        """
        Get the number of available etee dongle COM ports.

        :return: Number of available etee dongle ports.
        :rtype: int
        """
        available_ports = self.get_available_etee_ports()
        return len(available_ports)

    def get_available_etee_ports(self):
        """
        Get all available etee dongle COM ports. Other devices are automatically filtered out through a
        VID and PID filtering method.

        :return: List of COM port names with etee dongles connected.
        :rtype: list[str]
        """
        return [x[0] for x in serial_ports(self.ETEE_DONGLE_VID, self.ETEE_DONGLE_PID)]

    def disconnect(self):
        """
        Close serial connection to etee dongle.

        :return: Success flag - True if the connection was closed successfully, False if otherwise
        :rtype: bool
        """
        return self.driver.disconnect()

    def run(self):
        """
        Initiates the data loop in a separate thread. The data loop reads serial data, parses it and stores it in an internal buffer.
        The data loop also listens to serial and data events and manages event callback functions.
        """
        self.driver.run()

    def stop(self):
        """
        Stops the data loop.
        """
        self.driver.stop()

    def start_data(self):
        """
        Sends command to the etee controller to start the data stream.
        """
        self.driver.send_command(b"BP+AG\r\n")

    def stop_data(self):
        """
        Sends command to the etee controller to stop the data stream.
        """
        self.driver.send_command(b"BP+AS\r\n")

    def _api_data_callback(self, frameno, data):
        """
        Manages part of the data loop. Parses the argument data and stores it in the corresponding hand's
        internal buffer and update the API events (e.g. hand received or hand lost).

        :param dict data: Dictionary of the parsed controller data.
        """
        if data["hand"] == 0:
            # print(time.time() - self.hand_last_on_left)
            self._api_data_left = data
            self._hand_last_on_left = time.time()
            self._frameno_left += 1
            self._update_quaternion_left()
            self.left_hand_received.emit()

        elif data["hand"] == 1:
            self._api_data_right = data
            self._hand_last_on_right = time.time()
            self._frameno_right += 1
            self._update_quaternion_right()
            self.right_hand_received.emit()

        self.hand_received.emit()

        if time.time() - self._hand_last_on_left > 0.1 and self._api_data_left is not None:
            self._api_data_left = None
            self.left_hand_lost.emit()
        if time.time() - self._hand_last_on_right > 0.1 and self._api_data_left is not None:
            self._api_data_right = None
            self.right_hand_lost.emit()

    def _serial_exception_callback(self):
        """
        Emit a disconnection event if the etee dongle connection is lost.
        """
        ports = self.get_available_etee_ports()
        if self.driver.serial_reader.port not in ports:
            self.driver.disconnect()
            self.dongle_disconnected.emit()

    def _print_callback(self, reading):
        """
        Print messages received from the dongle, which are not data packets, and emits the corresponding connection events.

        :param bytes reading: Print message received from dongle.
        """
        if reading == b"R connection complete\r\n":
            self.right_connected.emit()
        elif reading == b"L connection complete\r\n":
            self.left_connected.emit()
        elif reading == b"R disconnected\r\n":
            self._api_data_right = None
            self.right_disconnected.emit()
        elif reading == b"L disconnected\r\n":
            self._api_data_left = None
            self.left_disconnected.emit()

    def _rest_callback(self, reading):
        """
        Handles controller connection loss events.
        Either controller's connection is lost if no data from the controller is received in 100ms.

        :param bytes reading: Print message received from dongle.
        """
        if reading is not None:
            return
        left_lost = time.time() - self._hand_last_on_left > 0.1 and self._api_data_left is not None
        right_lost = time.time() - self._hand_last_on_right > 0.1 and self._api_data_right is not None
        if left_lost:
            self._api_data_left = None
            self.left_hand_lost.emit()
        if right_lost:
            self._api_data_right = None
            self.right_hand_lost.emit()
        if left_lost and right_lost:
            self.data_lost.emit()

    # ---------------- IMU Processing ----------------
    def absolute_imu_enabled(self, on):
        """
        Enables or disables absolute orientation. Absolute orientation uses data from the accelerometer,
        gyroscope and magnetometer sensors for quaternion calculations. If disabled, the default mode will be enabled,
        which uses relative orientation, calculated only though the accelerometer and gyroscope data.

        :param bool on: True to switch to absolute orientation, False for relative orientation.
        """
        self._absolute_imu_on = on

    def _update_quaternion_left(self):
        """
        Calculates and updates the left controller's quaternion and euler.
        """
        accel = [
            self.get_left("accel_x"),
            self.get_left("accel_y"),
            self.get_left("accel_z")]
        gyro = [
            self.get_left("gyro_x"),
            self.get_left("gyro_y"),
            self.get_left("gyro_z")]
        if None in gyro or None in accel:
            return
        if self._absolute_imu_on:
            mag = [
                self.get_left("mag_x"),
                self.get_left("mag_y"),
                self.get_left("mag_z")]
            if None in mag:
                return
        else:
            mag = None
        self._quaternion_left = self._ahrs_left.get_quaternion(gyro, accel, mag)
        self._euler_left = self._ahrs_left.get_euler(gyro, accel, mag)

    def _update_quaternion_right(self):
        """
        Calculates and updates the right controller's quaternion and euler.
        """
        accel = [self.get_right("accel_x"), self.get_right("accel_y"), self.get_right("accel_z")]
        gyro = [self.get_right("gyro_x"), self.get_right("gyro_y"), self.get_right("gyro_z")]
        if None in gyro or None in accel:
            return
        if self._absolute_imu_on:
            mag = [self.get_right("mag_x"),  self.get_right("mag_y"), self.get_right("mag_z")]
            if None in mag:
                return
        else:
            mag = None
        self._quaternion_right = self._ahrs_right.get_quaternion(gyro, accel, mag)
        self._euler_right = self._ahrs_right.get_euler(gyro, accel, mag)

    def update_gyro_offset_left(self):
        """
        Retrieves the gyroscope calibration parameters saved on the left etee controller, and updates the calibration
        offsets in the driver model.
        """
        response = self.driver.send_command(b"BL+gf\r\n")
        try:
            x = float(response.split(b"X:")[1].split(b" ")[0].decode())
            y = float(response.split(b"Y:")[1].split(b" ")[0].decode())
            z = float(response.split(b"Z:")[1].split(b"\r\n")[0].decode())
            self._ahrs_left.set_gyro_offset([x, y, z])
        except:
            pass

    def update_gyro_offset_right(self):
        """
        Retrieves the gyroscope calibration parameters saved on the right etee controller, and updates the calibration
        offsets in the driver model.
        """
        response = self.driver.send_command(b"BR+gf\r\n")
        try:
            x = float(response.split(b"X:")[1].split(b" ")[0].decode())
            y = float(response.split(b"Y:")[1].split(b" ")[0].decode())
            z = float(response.split(b"Z:")[1].split(b"\r\n")[0].decode())
            self._ahrs_right.set_gyro_offset([x, y, z])
        except:
            pass

    def update_mag_offset_left(self):
        """
        Retrieves the magnetometer calibration parameters saved on the left etee controller, and updates the calibration
        offsets in the driver model.
        """
        response = self.driver.send_command(b"BL+mf\r\n")
        try:
            x = float(response.split(b"X:")[1].split(b" ")[0].decode())
            y = float(response.split(b"Y:")[1].split(b" ")[0].decode())
            z = float(response.split(b"Z:")[1].split(b"\r\n")[0].decode())
            self._ahrs_left.set_mag_offset([x, y, z])
        except:
            pass

    def update_mag_offset_right(self):
        """
        Retrieves the magnetometer calibration parameters saved on the right etee controller, and updates the calibration
        offsets in the driver model.
        """
        response = self.driver.send_command(b"BR+mf\r\n")
        try:
            x = float(response.split(b"X:")[1].split(b" ")[0].decode())
            y = float(response.split(b"Y:")[1].split(b" ")[0].decode())
            z = float(response.split(b"Z:")[1].split(b"\r\n")[0].decode())
            self._ahrs_right.set_mag_offset([x, y, z])
        except:
            pass

    def update_imu_offsets(self):
        """
        Retrieves the gyroscope and magnetometer calibration parameters from both controllers, and updates the calibration
        offsets in the driver model.
        """
        print("Updating gyro and magnetometer offsets. Please, wait...")
        time.sleep(2)
        self.update_gyro_offset_left()
        self.update_gyro_offset_right()
        self.update_mag_offset_left()
        self.update_mag_offset_right()
        print("Gyro and magnetometer offsets updated!")

    # ---------------- Firmware Versions ----------------
    def get_dongle_version(self):
        """
        Retrieve the firmware version of the connected dongle.

        :return: Returns the dongle firmware version if a dongle is connected.
                If no dongle is connected, the firmware version value will be None.
        :rtype: str
        """
        ret = None
        response = self.driver.send_command(b"AT+AB\r\n")
        response = parse_utf8(response)
        if "NRF" in response:
            ret = response.split("NRF")[1].split("\r\n")[0]
        return ret

    def get_etee_versions(self):
        """
        Retrieve the firmware version from the connected controllers.

        :return: Returns the firmware versions of the connected controllers.
                If a controller is not connected, its firmware version value will be None.
        :rtype: list[str]
        """
        ret = [None, None]
        response = self.driver.send_command(b"BP+AB\r\n", response_keys=[b"R:AB=etee", b"L:AB=etee"], verbose=True)
        if response is None:
            return ret
        if response[b"R:AB=etee"] is not None and b'-' in response[b"R:AB=etee"]:
            ret[1] = response[b"R:AB=etee"].decode().split("-")[1]
        if response[b"L:AB=etee"] is not None and b'-' in response[b"L:AB=etee"]:
            ret[0] = response[b"L:AB=etee"].decode().split("-")[1]
        return ret

    # ---------------- Get controller data by key ----------------
    def get_left(self, w):
        """
        Get a key value in the current internal data buffer for the left device.

        :param str w: Key for the device data to be retrieved, as defined in the YAML file.
        :return: Left controller's value for the key provided.
        """
        if self._api_data_left:
            return self._api_data_left[w]
        else:
            return None

    def get_right(self, w):
        """
        Get a key value in the current internal data buffer for the right device.

        :param str w: Key for the device data to be retrieved, as defined in the YAML file.
        :return: Right controller's value for the key provided.
        """
        if self._api_data_right:
            return self._api_data_right[w]
        else:
            return None

    def get_data(self, dev, w):
        """
        Get a key value in the current internal data buffer for the specified device (left or right).

        :param str dev: Selected controller hand. Possible values: "left", "right".
        :param str w: Key for the device data to be retrieved, as defined in the YAML file.
        :return: Selected controller's value for the key provided.
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left(w)
        elif dev == "right":
            return self.get_right(w)
        else:
            raise ValueError("Input 'dev' must be: 'left' or 'right'")

    # ---------------- Get hand/controller connection status ----------------
    def all_hands_on(self):
        """
        Check if both left and right controllers are connected.

        :return: Returns true if data has been recently received from both controllers.
        :rtype: bool
        """
        return (self.get_left is not None) and (self.get_right is not None)

    def any_hand_on(self):
        """
        Check if either left or right controller is connected.

        :return: Returns true if data has been recently received from any of the controller.
        :rtype: bool
        """
        return (self._api_data_left is not None) or (self._api_data_right is not None)

    def left_hand_on(self):
        """
        Check if the left controller is connected.

        :return: Returns true if data has been recently received from the left controller.
        :rtype: bool
        """
        return self._api_data_left is not None

    def right_hand_on(self):
        """
        Check if the right controller is connected.

        :return: Returns true if data has been recently received from the right controller.
        :rtype: bool
        """
        return self._api_data_right is not None

    # ================ Getter functions for sensor data ================
    # ---------------- Get pinky finger data ----------------
    def get_pinky_pull(self, dev):
        """
        Returns the pinky finger pull value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Pinky finger pull pressure (i.e. first pressure range, corresponding to light touch) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("pinky_pull")
        elif dev == "right":
            return self.get_right("pinky_pull")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_pinky_force(self, dev):
        """
        Returns the pinky finger force value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Pinky finger force pressure (i.e. second pressure range, corresponding to squeeze levels) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("pinky_force")
        elif dev == "right":
            return self.get_right("pinky_force")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_pinky_touched(self, dev):
        """
        Returns the pinky finger touch value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's pinky finger is touched.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("pinky_touched")
        elif dev == "right":
            return self.get_right("pinky_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_pinky_clicked(self, dev):
        """
        Returns the pinky finger click value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's pinky finger is clicked.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("pinky_clicked")
        elif dev == "right":
            return self.get_right("pinky_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get ring finger data ----------------
    def get_ring_pull(self, dev):
        """
        Returns the ring finger pull value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Ring finger pull pressure (i.e. first pressure range, corresponding to light touch) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("ring_pull")
        elif dev == "right":
            return self.get_right("ring_pull")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_ring_force(self, dev):
        """
        Returns the ring finger force value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Ring finger force pressure (i.e. second pressure range, corresponding to squeeze levels) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("ring_force")
        elif dev == "right":
            return self.get_right("ring_force")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_ring_touched(self, dev):
        """
        Returns the ring finger touch value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's ring finger is touched.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("ring_touched")
        elif dev == "right":
            return self.get_right("ring_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_ring_clicked(self, dev):
        """
        Returns the ring finger click value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's ring finger is clicked.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("ring_clicked")
        elif dev == "right":
            return self.get_right("ring_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get middle finger data ----------------
    def get_middle_pull(self, dev):
        """
        Returns the middle finger pull value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Middle finger pull pressure (i.e. first pressure range, corresponding to light touch) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("middle_pull")
        elif dev == "right":
            return self.get_right("middle_pull")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_middle_force(self, dev):
        """
        Returns the middle finger force value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Middle finger force pressure (i.e. second pressure range, corresponding to squeeze levels) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("middle_force")
        elif dev == "right":
            return self.get_right("middle_force")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_middle_touched(self, dev):
        """
        Returns the middle finger touch value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's middle finger is touched.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("middle_touched")
        elif dev == "right":
            return self.get_right("middle_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_middle_clicked(self, dev):
        """
        Returns the middle finger click value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's middle finger is clicked.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("middle_clicked")
        elif dev == "right":
            return self.get_right("middle_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get index finger data ----------------
    def get_index_pull(self, dev):
        """
        Returns the index finger pull value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Index finger pull pressure (i.e. first pressure range, corresponding to light touch) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("index_pull")
        elif dev == "right":
            return self.get_right("index_pull")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_index_force(self, dev):
        """
        Returns the index finger force value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Index finger force pressure (i.e. second pressure range, corresponding to squeeze levels) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("index_force")
        elif dev == "right":
            return self.get_right("index_force")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_index_touched(self, dev):
        """
        Returns the index finger touch value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's index finger is touched.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("index_touched")
        elif dev == "right":
            return self.get_right("index_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_index_clicked(self, dev):
        """
        Returns the index finger click value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's index finger is clicked.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("index_clicked")
        elif dev == "right":
            return self.get_right("index_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get thumb finger data ----------------
    def get_thumb_pull(self, dev):
        """
        Returns the thumb finger pull value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Thumb finger pull pressure (i.e. first pressure range, corresponding to light touch) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("thumb_pull")
        elif dev == "right":
            return self.get_right("thumb_pull")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_thumb_force(self, dev):
        """
        Returns the thumb finger force value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Thumb finger force pressure (i.e. second pressure range, corresponding to squeeze levels) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("thumb_force")
        elif dev == "right":
            return self.get_right("thumb_force")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_thumb_touched(self, dev):
        """
        Returns the thumb finger touch value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's thumb finger is touched.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("thumb_touched")
        elif dev == "right":
            return self.get_right("thumb_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_thumb_clicked(self, dev):
        """
        Returns the thumb finger click value for the selected device/controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected controller's thumb finger is clicked.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("thumb_clicked")
        elif dev == "right":
            return self.get_right("thumb_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get all fingers data ----------------
    def get_device_finger_pressures(self, dev):
        """
        Returns all the fingers pull and force pressure values.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Two arrays containing the pull and force pressures for the selected controller's five finger sensors.
                The first element of each array will be the thumb, and the las the pinky. For example: fingers_pull[2] = index finger pull.
                Pull and force values range: 0-126. Base values: 0.
        :rtype: list[int], list[int]
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left" or "right":
            fingers_pull = [self.get_data(dev, "thumb_pull"), self.get_data(dev, "index_pull"),
                            self.get_data(dev, "middle_pull"),
                            self.get_data(dev, "ring_pull"), self.get_data(dev, "pinky_pull")]
            fingers_force = [self.get_data(dev, "thumb_force"), self.get_data(dev, "index_force"),
                             self.get_data(dev, "middle_force"),
                             self.get_data(dev, "ring_force"), self.get_data(dev, "pinky_force")]
            return fingers_pull, fingers_force
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get tracker data ----------------
    def get_tracker_connections(self):
        """
        Checks if both eteeTrackers are connected to the controllers.

        :return: Returns True if both trackers are connected.
        :rtype: bool
        """
        return self.get_left("tracker_on") and self.get_right("tracker_on")

    def get_tracker_connection(self, dev):
        """
        Checks if the selected controller has an eteeTracker connected.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Returns True if the selected tracker is connected.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("tracker_on")
        elif dev == "right":
            return self.get_right("tracker_on")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get proximity sensor data from tracker ----------------
    def get_proximity(self, dev):
        """
        Returns the proximity sensor analog value for the selected controller.
        This sensor is only available when an eteeTracker is connected.
        If disconnected, the value will always be 0, even when the sensor is interacted with.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Value of the selected tracker's proximity sensor.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("proximity_value")
        elif dev == "right":
            return self.get_right("proximity_value")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_proximity_touched(self, dev):
        """
        Returns the proximity sensor touch value for the selected controller.
        This sensor is only available when an eteeTracker is connected.
        If disconnected, the value will always be false, even when the sensor is touched.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected tracker's proximity sensor value is at touch level.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("proximity_touched")
        elif dev == "right":
            return self.get_right("proximity_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_proximity_clicked(self, dev):
        """
        Returns the proximity sensor click value for the selected controller.
        This sensor is only available when an eteeTracker is connected.
        If disconnected, the value will always be false, even when the sensor is touched.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected tracker's proximity sensor value is at click level.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("proximity_clicked")
        elif dev == "right":
            return self.get_right("proximity_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get trackpad data ----------------
    def get_trackpad_x(self, dev):  # Location
        """
        Returns the trackpad x-axis position for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Trackpad X (horizontal) coordinate for the selected controller.
                Range: 0-255. If not touched, the value is 126.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("trackpad_x")
        elif dev == "right":
            return self.get_right("trackpad_x")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_trackpad_y(self, dev):
        """
        Returns the trackpad y-axis position for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Trackpad Y (vertical) coordinate for the selected controller.
                Range: 0-255. If not touched, the value is 126.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("trackpad_y")
        elif dev == "right":
            return self.get_right("trackpad_y")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_trackpad_xy(self, dev):
        """
        Returns the trackpad x-axis and y-axis positions for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Trackpad XY coordinates for the selected controller.
                Range for each axis coordinate: 0-255. If not touched, the value is 126.
        :rtype: list[int]
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left" or "right":
            xy = [self.get_data(dev, "trackpad_x"), self.get_data(dev, "trackpad_y")]
            if None in xy:
                return None
            else:
                return xy
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_trackpad_pull(self, dev):   # Pressure
        """
        Returns the trackpad pull pressure value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Trackpad pull pressure (i.e. first pressure range, corresponding to light touch) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("trackpad_pull")
        elif dev == "right":
            return self.get_right("trackpad_pull")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_trackpad_force(self, dev):
        """
        Returns the trackpad force pressure value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Trackpad force pressure (i.e. second pressure range, corresponding to hard press) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("trackpad_force")
        elif dev == "right":
            return self.get_right("trackpad_force")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_trackpad_touched(self, dev):
        """
        Returns the trackpad touch value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected trackpad is touched.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("trackpad_touched")
        elif dev == "right":
            return self.get_right("trackpad_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_trackpad_clicked(self, dev):
        """
        Returns the trackpad click value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected trackpad is clicked.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("trackpad_clicked")
        elif dev == "right":
            return self.get_right("trackpad_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get slider data ----------------
    def get_slider_value(self, dev):  # Location in Y-axis
        """
        Returns the slider positional value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: LED slider position, alongside its Y-axis (vertical), for the selected controller.
                Range: 0-126. If not touched, the slider value is 126.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("slider_value")
        elif dev == "right":
            return self.get_right("slider_value")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_slider_touched(self, dev):  # Touch
        """
        Returns the slider touch value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected LED light is touched.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("slider_touched")
        elif dev == "right":
            return self.get_right("slider_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_slider_up_button(self, dev):  # Slider Up/Down Button
        """
        Returns the slider UP button value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the upper part of selected LED is touched.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("slider_up_touched")
        elif dev == "right":
            return self.get_right("slider_up_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_slider_down_button(self, dev):
        """
        Returns the slider DOWN button value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the lower part of selected LED is touched.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("slider_down_touched")
        elif dev == "right":
            return self.get_right("slider_down_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get grip gesture data ----------------
    def get_grip_pull(self, dev):
        """
        Returns the grip gesture's pull pressure value for the selected controller.
        If the gesture is not performed, the pull value will be 0.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Grip gesture's pull pressure (i.e. first pressure range, corresponding to light touch) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("grip_pull")
        elif dev == "right":
            return self.get_right("grip_pull")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_grip_force(self, dev):
        """
        Returns the grip gesture's force pressure value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Grip gesture's force pressure (i.e. second pressure range, corresponding to squeeze levels) for the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("grip_force")
        elif dev == "right":
            return self.get_right("grip_force")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_grip_touched(self, dev):
        """
        Returns the grip gesture's touch value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the grip gesture reaches touch level in the selected controller.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("grip_touched")
        elif dev == "right":
            return self.get_right("grip_touched")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_grip_clicked(self, dev):
        """
        Returns the grip gesture's click value for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the grip gesture reaches click level in the selected controller.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("grip_clicked")
        elif dev == "right":
            return self.get_right("grip_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get standard pinch (using trackpad) gesture data ----------------
    def get_pinch_trackpad_pull(self, dev):
        """
        Returns the pull pressure value for the pinch with trackpad gesture in the selected controller.
        If the gesture is not performed, the pull value will be 0.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Pull pressure for the pinch gesture (trackpad variation) in the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("pinch_trackpad_pull")
        elif dev == "right":
            return self.get_right("pinch_trackpad_pull")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_pinch_trackpad_clicked(self, dev):
        """
        Returns the click value for the pinch with trackpad gesture in the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the pinch gesture (trackpad variation) reaches click level in the selected controller.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("pinch_trackpad_clicked")
        elif dev == "right":
            return self.get_right("pinch_trackpad_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get alternative pinch (using thumb finger) gesture data ----------------
    def get_pinch_thumbfinger_pull(self, dev):
        """
        Returns the pull pressure value for the pinch with thumb finger gesture in the selected controller.
        If the gesture is not performed, the pull value will be 0.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Pull pressure for the pinch gesture (thumb finger variation) in the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("pinch_thumbfinger_pull")
        elif dev == "right":
            return self.get_right("pinch_thumbfinger_pull")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_pinch_thumbfinger_clicked(self, dev):
        """
        Returns the click value for the pinch with thumb finger gesture in the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the pinch gesture (thumb finger variation) reaches click level in the selected controller.
                Range: 0-126. Base value: 0.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("pinch_thumbfinger_clicked")
        elif dev == "right":
            return self.get_right("pinch_thumbfinger_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get independent point (trackpad can be used) gesture data ----------------
    def get_point_independent_clicked(self, dev):
        """
        This is the main point gesture used in VR and XBOX-controller based games.

        Returns the click value for the independent point (trackpad can be touched) gesture in the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the independent point gesture variation is detected in the selected controller. In this variation, the trackpad can be used alongside the point gesture.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("point_independent_clicked")
        elif dev == "right":
            return self.get_right("point_independent_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get exclude-trackpad point (trackpad must not be touched) gesture data ----------------
    def get_point_excl_tp_clicked(self, dev):
        """
        This is the alternative point gesture.

        Returns the click value for the exclude-trackpad point (trackpad must not be touched) gesture in the selected controller.
        In this variation, if the user touches the trackpad while doing the point gesture, the gesture will be cancelled.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the exclude-trackpad point gesture variation (i.e. where the trackpad is not touched) is detected in the selected controller.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("point_exclude_trackpad_clicked")
        elif dev == "right":
            return self.get_right("point_exclude_trackpad_clicked")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get IMU and quaternions ----------------
    def get_quaternion(self, dev):
        """
        Returns the quaternion for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Rotation quaternion for the selected controller.
        :rtype: list[int]
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self._quaternion_left
        elif dev == "right":
            return self._quaternion_right
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_euler(self, dev):
        """
        Returns the euler angles for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Euler angles (roll, pitch, yaw) for the selected controller.
        :rtype: list[int]
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self._euler_left
        elif dev == "right":
            return self._euler_right
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_accel(self, dev):
        """
        Returns the accelerometer values for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Acceleration vector for the selected controller.
        :rtype: list[int]
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left" or "right":
            accel = [self.get_data(dev, "accel_x"), self.get_data(dev, "accel_y"), self.get_data(dev, "accel_z")]
            if None in accel:
                return None
            else:
                return accel
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_gyro(self, dev):
        """
        Returns the gyroscope values for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Angular acceleration vector for the selected controller.
        :rtype: list[int]
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left" or "right":
            gyro = [self.get_data(dev, "gyro_x"), self.get_data(dev, "gyro_y"), self.get_data(dev, "gyro_z")]
            if None in gyro:
                return None
            else:
                return gyro
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_mag(self, dev):
        """
        Returns the magnetometer values for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Magnetic flux density vector for the selected controller.
        :rtype: list[int]
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left" or "right":
            mag = [self.get_data(dev, "mag_x"), self.get_data(dev, "mag_y"), self.get_data(dev, "mag_z")]
            if None in mag:
                return None
            else:
                return mag
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get battery data ----------------
    def get_battery_level(self, dev):
        """
        Returns the battery level for the selected controller.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: Battery fuel gauge level for the selected controller.
                Range: 0-100.
        :rtype: int
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("battery_level")
        elif dev == "right":
            return self.get_right("battery_level")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_charging_in_progress_status(self, dev):
        """
        Checks if the selected controller is charging.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected battery is charging.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("battery_charging")
        elif dev == "right":
            return self.get_right("battery_charging")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    def get_charging_complete_status(self, dev):
        """
        Checks if the selected controller has finished charging (battery level is 100%).

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected battery charging has been completed.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("battery_charging_complete")
        elif dev == "right":
            return self.get_right("battery_charging_complete")
        else:
            raise ValueError("Input must be: 'left' or 'right'")

    # ---------------- Get system/power button data ----------------
    def get_system_button_pressed(self, dev):
        """
        Checks if the system button is pressed.

        :param str dev: Selected device hand. Possible values: "left", "right".
        :return: True if the selected system button is pressed.
        :rtype: bool
        :raises ValueError: if the dev input is not "left" or "right"
        """
        if dev == "left":
            return self.get_left("system_button")
        elif dev == "right":
            return self.get_right("system_button")
        else:
            raise ValueError("Input must be: 'left' or 'right'")
