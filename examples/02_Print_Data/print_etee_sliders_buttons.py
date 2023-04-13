"""
Example code:
-------------
This script prints the slider UP/DOWN button values from both eteeControllers, using getter functions.
"""

import time
import sys
import keyboard
from datetime import datetime
from etee import EteeController
# -*- coding: utf-8 -*-


def process_left_slider_buttons():
    """
    Retrieve the left slider button values from the etee driver.

    :return: Array containing the left controller's slider button values: up and down button states.
    :rtype: list[bool]
    """
    left_slider = [etee.get_slider_up_button('left'), etee.get_slider_down_button('left')]
    return left_slider


def process_right_slider_buttons():
    """
    Retrieve the right slider button values from the etee driver.

    :return: Array containing the right controller's slider button values: up and down button states.
    :rtype: list[bool]
    """
    right_slider = [etee.get_slider_up_button('right'), etee.get_slider_down_button('right')]
    return right_slider


def print_title():
    """
    Print CLI graphics for the application title.
    """
    print("======================================================")
    print(r"        __               ___    ____  ____")
    print(r"  ___  / /____  ___     /   |  / __ \/  _/")
    print(r" / _ \/ __/ _ \/ _ \   / /| | / /_/ // /  ")
    print(r"/  __/ /_/  __/  __/  / ___ |/ ____// /   ")
    print(r"\___/\__/\___/\___/  /_/  |_/_/   /___/   ")
    print(" ")
    print("Welcome to this etee CLI application.\nYou can print both controller's slider UP/DOWN data here.")
    print("======================================================")


def check_controller_connection(left_data, right_data):
    """
    Check that both controllers are connected. If not, attempt re-connection.

    :param str left_data: Left controller button values from the etee driver. If a controller disconnects, the values in the buffer will reset to None.
    :param str right_data: Right controller button values from the etee driver. If a controller disconnects, the values in the buffer will reset to None.
    :return: True if both controllers are still connected; False if otherwise
    :rtype: bool
    """
    connection = True
    if left_data[0] == None and right_data[0] == None:
        print("---")
        print(current_time, f"The left and right etee controllers were not detected. Please reconnect controller.")
        etee.start_data()  # If a controller has reconnected with the dongle, it will start etee controller data stream
        time.sleep(0.05)
        connection = False
    elif left_data[0] == None:
        print("---")
        print(current_time, f"The left etee controller was not detected. Please reconnect controller.")
        etee.start_data()  # If a controller has reconnected with the dongle, it will start etee controller data stream
        time.sleep(0.05)
        connection = False
    elif right_data[0] == None:
        print("---")
        print(current_time, f"The right etee controller was not detected. Please reconnect controller.")
        etee.start_data()  # If a controller has reconnected with the dongle, it will start etee controller data stream
        time.sleep(0.05)
        connection = False
    return connection


if __name__ == "__main__":
    # Initialise the etee driver and find dongle
    etee = EteeController()
    num_dongles_available = etee.get_number_available_etee_ports()
    if num_dongles_available > 0:
        etee.connect()     # Attempt connection to etee dongle
        time.sleep(1)
        etee.start_data()  # Attempt to send a command to etee controllers to start data stream
        etee.run()         # Start data loop
    else:
        print("No dongle found. Please, insert an etee dongle and re-run the application.")
        sys.exit("Exiting application...")

    print_title()

    # If dongle is connected, print index values
    while True:
        # If 'Esc' key is pressed while printing data, stop controller data stream, data loop and exit application
        if keyboard.is_pressed('Esc'):
            print("\n'Esc' key was pressed. Exiting application...")

            etee.stop_data()  # Stop controller data stream
            print("Controller data stream stopped.")
            etee.stop()  # Stop data loop
            print("Data loop stopped.")

            time.sleep(0.05)
            sys.exit(0)  # Exit driver

        # Else continue printing controller data
        else:
            current_time = datetime.now().strftime("%H:%M:%S.%f")
            num_dongles_available = etee.get_number_available_etee_ports()

            if num_dongles_available > 0:
                left_buttons = process_left_slider_buttons()
                right_buttons = process_right_slider_buttons()
                controllers_connected = check_controller_connection(left_buttons, right_buttons)
                if controllers_connected:
                    print(current_time, f"| Left slider - Up {'●' if left_buttons[0] else '○'} "
                                        f", Down {'●' if left_buttons[1] else '○'}  "
                                        f"|  Right slider - Up {'●' if right_buttons[0] else '○'} "
                                        f", Down {'●' if right_buttons[1] else '○'}")
                    time.sleep(0.05)
                else:
                    print("Please, connect both controllers.")

            else:
                print("---")
                print(current_time, "Dongle disconnected. Please, re-insert the dongle and re-run the application.")

                etee.stop_data()  # Stop controller data stream
                print("Controller data stream stopped.")
                etee.stop()  # Stop data loop
                print("Data loop stopped.")

                time.sleep(0.05)
                sys.exit("Exiting application...")
