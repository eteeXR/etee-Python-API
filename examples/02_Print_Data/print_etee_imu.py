"""
Example code:
-------------
This script prints the IMU sensor values from the selected eteeController, using getter functions.
"""

import time
import sys
import keyboard

from datetime import datetime
from etee import EteeController


def print_title():
    print("======================================================")
    print(r"        __               ___    ____  ____")
    print(r"  ___  / /____  ___     /   |  / __ \/  _/")
    print(r" / _ \/ __/ _ \/ _ \   / /| | / /_/ // /  ")
    print(r"/  __/ /_/  __/  __/  / ___ |/ ____// /   ")
    print(r"\___/\__/\___/\___/  /_/  |_/_/   /___/   ")
    print(" ")
    print("Welcome to this etee CLI application.\nYou can print the IMU data from one controller here.")
    print("======================================================")


def adjust_imu(original_arr, offsets_arr):
    adj_arr = [0, 0, 0]
    if original_arr is None or offsets_arr is None:
        pass
    else:
        for i in range(3):
            adj_arr[i] = original_arr[i] - offsets_arr[i]
    return adj_arr


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

    # Prompt for user to select the hand to print values from
    print("Please, enter what controller hand you would like to print the values from. Valid options: right, left.")
    valid_controllers = ["right", "left"]
    controller_selected = input("--> Enter controller hand: ")
    while controller_selected not in valid_controllers:
        print("Input not valid! Please enter a valid input: right, left.")
        controller_selected = input("--> Enter controller hand: ")
    print("Your selected controller hand: ", controller_selected)

    # IMU offsets
    print("Don't move, calculating IMU offsets...")
    time.sleep(2)
    accel_offset = etee.get_accel(controller_selected)
    gyro_offset = etee.get_gyro(controller_selected)
    mag_offset = etee.get_mag(controller_selected)
    print("Offsets calculated and applied.")

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

            # If a dongle is connected, try to print finger pressure values
            if num_dongles_available > 0:
                accel = etee.get_accel(controller_selected)
                adj_accel = adjust_imu(accel, accel_offset)

                gyro = etee.get_gyro(controller_selected)
                adj_gyro = adjust_imu(gyro, gyro_offset)

                mag = etee.get_mag(controller_selected)
                adj_mag = adjust_imu(mag, mag_offset)

                if adj_accel is None:
                    print("---")
                    print(current_time, f"The {controller_selected} etee controller was not detected. Please reconnect controller.")
                    etee.start_data()   # If a controller has reconnected with the dongle,
                                        # it will start the etee controller data stream
                    time.sleep(0.1)
                else:
                    print(current_time, f"Controller: {controller_selected} --> "
                                        f"Accel: X({adj_accel[0]:>6}), Y({adj_accel[1]:>6}), Z({adj_accel[2]:>6}) "
                                        f"| Gyro: X({adj_gyro[0]:>6}), Y({adj_gyro[1]:>6}), Z({adj_gyro[2]:>6}) "
                                        f"| Magnetometer: X({adj_mag[0]:>6}), Y({adj_mag[1]:>6}), Z({adj_mag[2]:>6})")
                    time.sleep(0.05)
            else:
                print("---")
                print(current_time, "Dongle disconnected. Please, re-insert the dongle and re-run the application.")

                etee.stop_data()  # Stop controller data stream
                print("Controller data stream stopped.")
                etee.stop()  # Stop data loop
                print("Data loop stopped.")

                time.sleep(0.05)
                sys.exit("Exiting application...")
