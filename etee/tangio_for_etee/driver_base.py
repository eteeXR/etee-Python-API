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
Main file for subpackage: tangio_for_etee.
Methods for low-level TG0 device communication.

"""

from builtins import object
import threading
from bitstring import BitArray
import atexit
import serial
import warnings
import yaml
import os
import time

from . import serial_ports

yaml.warnings({'YAMLLoadWarning': False})
warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

DEFAULT_READLINE_TIMEOUT = 1
DEFAULT_READ_DATA_TIMEOUT = 1
DEFAULT_READ_SERIAL_TIMEOUT = 1
DEFAULT_READ_RESPONSE_TIMEOUT = 1


class SerialReader(object):
    """
    This class is in charge of connecting to the hardware device through serial communication, and start reading and
    parsing the data it receives to the defined data structure.
    """

    def __init__(self, config_file=None, *, baud_rate=115200, data_bytes=None, end_bytes=None, widgets=None):
        """
        Initializes SerialReader class with the given parameters.

        :param str config_file: path to the file which contains the data structure definition.
        :param int baud_rate: serial connection baud_rate.
        :param int data_bytes: byte length of data to be received from the device.
        :param int end_bytes: length of data packet delimiter characters (\xff).
        :param dict widgets: dictionary defining the data structure.
        """
        super().__init__()
        self.serial = None
        self.baud_rate = baud_rate
        self.serial_lock = threading.Lock()
        self.port = None

        if config_file is not None or widgets is not None:
            self.data_bytes = None
            self.end_bytes = None
            self.widgets = None
            self.configure(config_file, data_bytes=data_bytes, end_bytes=end_bytes, widgets=widgets)

    def connect(self, port=None):
        """
        Opens a connection through a serial reader instance through a specified port or the first available TG0 port.

        :param str port: string representation the port of connection.
                        If None is passed, the driver will connect to the first available TG0 port.
        """
        available_ports = serial_ports()
        if not available_ports:
            raise Exception("No TG0 device is found!")
        if port is None:
            for i in range(len(available_ports)):
                port = available_ports[i][0]
                try:
                    self.serial = serial.Serial(port, self.baud_rate, timeout=0.1, write_timeout=0.1)
                    print("Connected to port {}".format(port))
                    self.port = port
                    break
                except:
                    print("Failed to connect to port {}, try other port...".format(port))
        elif port in [i[0] for i in available_ports]:
            try:
                self.serial = serial.Serial(port, self.baud_rate, timeout=1, write_timeout=1)
                print("connected to port {}".format(port))
                self.port = port
            except:
                print("Failed to connect to port {}, try other port...".format(port))
        else:
            raise Exception("No TG0 device found at port {}!".format(port))

    def close_connection(self):
        """
        Closes the connection to hardware through the serial port maintained by the serial reader instance.
        """
        if self.serial is not None:
            self.serial.close()
            if self.serial_lock.locked():
                self.serial_lock.release()
        self.port = None
        print("Connection closed")

    def reset_input(self):
        """
        Empty the driver input buffer, which stores the device transmitted data.
        """
        self.serial.reset_input_buffer()

    def readline(self, delim=b"\r\n", num=None, timeout=DEFAULT_READ_DATA_TIMEOUT):
        """
        Reads bytes from the serial until a delimiter.

        :param bytes delim: delimiter until to which bytes are read.
        :param int num: maximum number of characters to be read.
        :param float timeout: timeout duration in seconds.
        :return: read byte string.
        """
        line = b""
        elapsed = 0
        time_start = time.time()
        self.serial_lock.acquire()
        while elapsed < timeout:
            try:
                char = self.serial.read()
                line = line + char
            except serial.SerialException as e:
                self.serial_lock.release()
                raise e
            if isinstance(delim, list):
                delim_found = False
                for item in delim:
                    if line[-len(item):] == item:
                        delim_found = True
                        break
                if delim_found:
                    break
            else:
                if line[-len(delim):] == delim:
                   break
            if len(line) == num:
                break
            elapsed = time.time() - time_start
        self.serial_lock.release()
        return line

    def write(self, message):
        """
        Writes a message to the serial, but does not read the device's response.

        :param bytes message: message written to the serial.
        """
        self.serial.write(message)

    def send_command(self, message, response_start=b"OK", response_end=b"END", response_keys=None, timeout=DEFAULT_READ_RESPONSE_TIMEOUT, verbose=False):
        """
        Writes a message to the serial, and reads response.

        :param bytes message: message written to the serial.
        :param bytes response_start: a delimiter starting from which the response is read.
        :param bytes response_end: a delimiter until which the response is read.
        :param bytes response_keys: the commands leaves as soon as all these keys are read.
        :param float timeout: read timeout duration in seconds.
        :param bool verbose: enable or disable verbose mode, which prints messages sent and received through serial.
        :return: read response
        """
        if verbose:
            print("write: ", message)
        self.serial.write(message)
        previous_timeout = self.serial.timeout
        self.serial.timeout = 1
        response = b""
        response_started = (response_start is None)
        if response_keys is not None:
            keys_received = [False] * len(response_keys)
        elapsed = 0
        time_start = time.time()
        while elapsed < timeout:
            elapsed = time.time() - time_start
            line = self.readline(delim=b"\r\n")
            if verbose:
                print("readline: ", line)
            if line == b'':
                continue
            elif b"\r\n" not in line:
                print("Line was not read.")
                continue
            elif (response_start + b"\r\n") in line:
                response += (response_start + b"\r\n")
                response_started = True
            else:
                if response_started:
                    response += line
            if response_end is not None:
                if (response_end + b"\r\n") in line:
                    break
            if response_keys is not None:
                for i, key in enumerate(response_keys):
                    if key in line:
                        keys_received[i] = True
                        if all(keys_received):
                            break
        if response_keys is not None:
            response_dict = dict()
            for key in response_keys:
                if key in response:
                    response_dict[key] = response.split(key)[1].split(b"\r\n")[0]
                else:
                    response_dict[key] = None
                print(key, response_dict[key])
            response = response_dict

        self.serial.timeout = previous_timeout

        return response

    def configure(self, config_file=None, *, data_bytes=None, end_bytes=None, widgets=None):
        """
        Update the information on data structure configuration.
        This provides information on data packet structures, and byte-bit location of specific device parameters,
        allowing for their retrieval during device communication.

        :param str config_file: path to the file which contains the data structure definition.
        :param int data_bytes: byte length of data to be received from the device.
        :param int end_bytes: length of data packet delimiter characters (\xff).
        :param dict widgets: dictionary defining the data structure.
        """
        if config_file is not None:
            with open(config_file, 'r') as fstream:
                conf_dict = yaml.safe_load(fstream)
            self.data_bytes = conf_dict["total_bytes"]["data_bytes"]
            self.end_bytes = conf_dict["total_bytes"]["end_bytes"]
            self.widgets = conf_dict["widgets"]
        else:
            if data_bytes is not None and end_bytes is not None and widgets is not None:
                self.data_bytes = data_bytes
                self.end_bytes = end_bytes
                self.widgets = widgets
            else:
                raise Exception("Since config_file is None, data_bytes, end_bytes and widgets are required arguments.")

    def raw2data(self, raw):
        """
        Parses raw data to the specified data structure.

        :param bytes raw: raw binary data from the serial port.
        :return: data structure parsed from the raw data following the data structure specification.
        """
        events = {}
        for name, properties in self.widgets.items():
            if "byte" in properties:
                indices = properties["byte"]
                is_signed = "signed" in properties
                if isinstance(indices, list):
                    if any([x > len(raw) for x in indices]):
                        raise Exception("Widget index our of range")
                    if "single_value" in properties:
                        event = int.from_bytes(b"".join([raw[x:x + 1] for x in indices]), byteorder='little', signed=is_signed)
                    else:
                        event = [int.from_bytes(raw[x:x + 1], byteorder='big', signed=is_signed) for x in indices]
                else:
                    if indices > len(raw):
                        raise Exception("Widget index our of range")
                    if 'bit' not in properties:
                        event = int.from_bytes(raw[indices:indices + 1], byteorder='big', signed=is_signed)
                    else:
                        event = BitArray(hex="0x" + raw[indices:indices + 1].hex()).bin[::-1]
                        event = int(event[properties['bit']])
            elif "bit" in properties:
                indices = properties["bit"]
                if any([x > len(raw) * 8 for x in indices]):
                    raise Exception("Widget index our of range")
                bit_array = BitArray(hex="0x" + raw[::-1].hex()).bin[::-1]
                event = int("".join([bit_array[i] for i in indices]), 2)

            events[name] = event
        return events

    def read_widgets_and_text(self, timeout=DEFAULT_READ_SERIAL_TIMEOUT):
        """
        Reads binary data from the serial port and calls raw2data to parse it.

        :param float timeout: time after which the method will stop trying to read the widget value, in seconds.
        :return: data structure instance parsed using the raw2data method from a serial port raw data reading.
        """
        events = None
        start_time = time.time()
        while time.time() - start_time < timeout:
            data = self.readline(delim=[b"\xff\xff", b"\r\n"])
            if b"\xff\xff" == data[-self.end_bytes:] and len(data) == self.data_bytes + self.end_bytes:
                data = data[0:-self.end_bytes]
                events = self.raw2data(data)
                break
            if b"\r\n" == data[-2:]:
                events = data
                break
        return events


class TG0Driver:
    """
    This driver connects to TG0 devices through serial communication and retrieves data in a loop. It then stores this
    data in a separate container for each device, overwriting them periodically as new data is fetched from the hardware.
    This class is usually used for inheritance from a child class specific to the hardware device that it's been used for.
    """
    def __init__(self, config_file=None, *, data_bytes=None, end_bytes=None, widgets=None, keep_alive_period=5):
        """
        Initializes the TG0Driver class with the given parameters.

        :param str config_file: path to the file which contains the data structure definition.
        :param int data_bytes: byte length of data to be received from the device.
        :param int end_bytes: length of data packet delimiter characters (\xff).
        :param dict widgets: dictionary defining the data structure.
        :param float keep_alive_period: duration of time to keep the connection alive even when no data is transmitted.
        """
        self.baud_rate = 115200
        self.serial_reader = None
        self.port = None
        self.thread = None
        self.keep_alive_period = keep_alive_period
        self.last_alive_time = 0
        self.config_file = config_file
        self.data_bytes = data_bytes
        self.end_bytes = end_bytes
        self.widgets = widgets
        self.run_mode = False
        self.sleep_mode = False
        self.callbacks = list()
        self.print_callbacks = list()
        self.rest_callbacks = list()
        self.serial_exception_callbacks = list()
        self.connection_callbacks = list()
        self.current_data = None
        self.frameno = -1
        self.read_text = False
        self.loop_is_running = False

    def connect(self, port=None, close_at_exit=True):
        """
        Attempts to open a connection between the driver and the hardware device.

        :param str port: string representation of the hardware port to be used to establish the connection to hardware.
                    This is an optional parameter. connect2hardware can be invoked with None port, and it will choose the
                    first available COM port.
        :param bool close_at_exit: boolean to define whether the connection to the device will be closed at exit.
        :return: success flag; true if the connection was successful, false otherwise.
        """
        try:
            self.serial_reader = SerialReader(self.config_file, baud_rate=self.baud_rate, data_bytes=self.data_bytes,
                                              end_bytes=self.end_bytes,  widgets=self.widgets)
            self.serial_reader.connect(port=port)
            if close_at_exit:
                self.close_connection_at_exit()
            self.last_alive_time = time.time()
            self.connection_handler(state=1)
            self.port = self.serial_reader.port
            return True
        except:
            self.connection_handler(state=2)
            raise Exception("Could not connect to hardware!")

    def disconnect(self):
        """
        Commands the SerialReader instance to close the connection to hardware.

        :return: true if the connection to hardware was closed correctly, false otherwise.
        """
        self.stop()
        try:
            self.serial_reader.close_connection()
            self.connection_handler(state=0)
            return True
        except:
            return False

    def configure(self, config_file=None, data_bytes=None, end_bytes=None, widgets=None):
        """
        Update the information on data structure definition for specific data retrieval during device communication.

        :param str config_file: path to the file which contains the data structure definition.
        :param int data_bytes: byte length of data to be received from the device.
        :param int end_bytes: length of data packet delimiter characters (\xff).
        :param dict widgets: dictionary defining the data structure.
        """
        self.serial_reader.configure(config_file, data_bytes=data_bytes, end_bytes=end_bytes, widgets=widgets)

    def run(self):
        """
        Launches a separate thread that reads data from the serial connection cyclically, and makes it available
        through the getter methods.
        """
        self.read_text = True
        self.run_mode = True
        self.thread = threading.Thread(target=self.loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """
        Stops the data thread.
        """
        self.run_mode = False

    def sleep(self, timeout=3):
        """
        Suspends the data thread. During sleep, no data is read from serial.

        :param timeout: duration of the driver sleep.
        :return: false is the driver loop is running.
        """
        self.sleep_mode = True
        start_time = time.time()
        while (time.time() - start_time < timeout):
            if not self.loop_is_running:
                break
            time.sleep(0.01)
        return not self.loop_is_running

    def clear_callbacks(self):
        """
        Clear all active callbacks.
        """
        self.callbacks.clear()

    def add_callback(self, cb):
        """
        Adds a specific callback for handling data messages received from the dongle. Note: Data messages contain sensor
        information from the controller, and can be identified by their '\\\\xff\\\\xff' end flag.

        :param cb: callback.
        """
        self.callbacks.append(cb)

    def add_print_callback(self, cb):
        """
        Adds a specific callback for handling print messages received from the dongle, which are not data packets.
        Note: Print messages contain information such as connection status or commands, and can be identified by
        their '\\\\r\\\\n' end flag.

        :param cb: callback.
        """
        self.print_callbacks.append(cb)

    def add_connection_callback(self, cb):
        """
        Adds a specific callback for driver to device connection events.

        :param cb: callback.
        """
        self.connection_callbacks.append(cb)

    def add_serial_exception_callbacks(self, cb):
        """
        Adds a specific callback for raising exceptions errors.

        :param cb: callback.
        """
        self.serial_exception_callbacks.append(cb)

    def add_rest_callback(self, cb):
        """
        Adds any other callback that is not a data, print, connection or exception callback.

        :param cb: callback.
        """
        self.rest_callbacks.append(cb)

    def data_handler(self, frameno, data):
        """
        Handles the active callbacks for data parsing. Data received from the devices can be classified in data and
        print messages. Data messages contain sensor information from the controller, and can be identified by their
        b'\\\\xff\\\\xff' end flag.

        :param int frameno: Frame number.
        :param bytes data: Data message received from the device.
        """
        for cb in self.callbacks:
            cb(frameno, data)

    def print_handler(self, reading):
        """
        Handles the active callbacks for device status and command prints. Data received from the devices can be
        classified in data and print messages. Print messages contain information such as connection status or
        commands, and can be identified by their b'\r\n' end flag.

        :param int frameno: Frame number.
        :param bytes data: Print message received from the device.
        """
        for cb in self.print_callbacks:
            cb(reading)

    def connection_handler(self, state):
        """
        Handles the active connection callbacks.

        :param int state:
        state 0: not connected,
        state 1: connected,
        state 2: failed building connection,
        state 3: waiting/trying to rebuild previously connected COM.
        """
        for cb in self.connection_callbacks:
            cb(state)

    def serial_exception_handler(self):
        """
        Handles the active callbacks for exception errors.
        """
        for cb in self.serial_exception_callbacks:
            cb()

    def rest_handler(self, reading):
        """
        Handles any other active callbacks that are not data, print, connection or exception callbacks.

        :param bytes reading: Message received.
        """
        for cb in self.rest_callbacks:
            cb(reading)

    def next(self):
        """
        Reads widget data from the data as specified by the data structure and stores it in a data holder.
        """
        try:
            reading = self.serial_reader.read_widgets_and_text()
        except serial.SerialException:
            self.serial_exception_handler()
            return

        if reading is not None:
            self.last_alive_time = time.time()

        if isinstance(reading, dict):
            self.current_data = reading
            self.frameno += 1
            self.data_handler(self.frameno, reading)
        elif isinstance(reading, bytes):
            self.print_handler(reading)
        else:
            self.rest_handler(reading)

    def loop(self):
        """
        Method that loops infinitely parsing data read from the serial connection and storing it.
        """
        while self.run_mode:
            if not self.sleep_mode:
                self.next()
                self.loop_is_running = True
            else:
                self.loop_is_running = False
                time.sleep(0.01)

    def write(self, message):
        """
        Send the message to the hardware device. This is usually an instruction or command to be executed.

        :param bytes message: message to be passed.
        """
        self.serial_reader.write(message)

    def send_command(self, command, sleep=True, *args, **kargs):
        """
        Suspends reading data from the device. Sends command and reads response.

        :param bytes command: Command to be sent.
        :param bool sleep: Boolean to toggle a sleep routine before the command is sent. True by default.
        :return: Read response or None if the command failed.
        """
        if sleep and self.run_mode:
            self.sleep()
        try:
            if self.serial_reader is None or self.serial_reader.serial is None:
                print("Error: Serial connection is not established.")
                return None
            response = self.serial_reader.send_command(command, *args, **kargs)
        except Exception as e:
            self.sleep_mode = False
            print(f"Sending command failed: {str(e)}")
            return None
        finally:
            self.sleep_mode = False
        return response

    def close_connection_at_exit(self):
        """
        Register a callback to close the connection to hardware when the program is about to exit.
        """
        atexit.register(self.disconnect)

    def set_alive_period(self, period):
        """
        Set a different value for the duration of time to keep the connection alive even when no data is transmitted.

        :param float period: duration of alive period, in seconds.
        """
        self.keep_alive_period = period

    def is_alive(self):
        """
        Returns if the device connection is alive.

        :return: false if data hs not been received for a time longer than the alive period time.
        """
        return (time.time() - self.last_alive_time) < self.keep_alive_period

    def last_alive(self):
        """
        Returns the last time when hardware device data was received.

        :return: how long ago the data was last read, in seconds.
        """
        return time.time() - self.last_alive_time


class _TG0DataQueue:
    """
    This class handles the queue for data received from the hardware device.
    """
    def __init__(self, queue):
        """
        Initialise the class.
        """
        self.queue = queue

    def put_frame(self, frameno, data):
        """
        Put items into the queue.

        :param int frameno: frame number
        :param bytes data: data passed
        """
        self.queue.put((frameno, data))
