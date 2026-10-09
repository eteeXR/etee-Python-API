"""
Example code:
-------------
This script prints the trackpad values (location: x-position and y-position, pressure: pull and force, touch, click)
from the selected eteeController, using getter functions.
"""

import time
import sys
from pynput import keyboard
from datetime import datetime
from etee import EteeController

def on_press(key):
    if key == keyboard.Key.esc:
        return False  # Stop listener
    
def process_trackpad(dev):
    """
    Retrieve the selected device's trackpad values from the etee driver.

    :param str dev: Selected device hand. Possible values: "left", "right".
    :return: Two arrays containing the selected controller's trackpad values. One containing the location
    (X-axis position, Y-axis position), and another the pressure (pull pressure, force pressure, touch and click).
    :rtype: list[int], list[Any]
    """
    loc = [etee.get_data(dev, "trackpad_x"), etee.get_data(dev, "trackpad_y")]
    pressure = [etee.get_data(dev, "trackpad_pull"), etee.get_data(dev, "trackpad_force"),
                etee.get_data(dev, "trackpad_touched"), etee.get_data(dev, "trackpad_clicked")]
    return loc, pressure


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
    print("Welcome to this etee CLI application.\nYou can print trackpad data here.")
    print("======================================================")


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
    print("Press 'Esc' key to exit the application.")

    # Create a keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        while listener.running:
            current_time = datetime.now().strftime("%H:%M:%S.%f")
            num_dongles_available = etee.get_number_available_etee_ports()

            if num_dongles_available > 0:
                selected_loc, selected_pressure = process_trackpad(controller_selected)
                if selected_loc[0] == None:
                    print("---")
                    print(current_time, f"The {controller_selected} etee controller was not detected. Please reconnect controller.")
                    etee.start_data()   # If a controller has reconnected with the dongle, it will start etee controller data stream
                    time.sleep(0.05)
                else:
                    print(current_time, f"Selected Trackpad: {controller_selected} --> "
                                        f"X-Axis: {selected_loc[0]:<3}, Y-Axis: {selected_loc[1]:<3} |"
                                        f"Pressure (pull: {selected_pressure[0]:<3}, force: {selected_pressure[1]:<3}), "
                                        f"Touch: {'True' if selected_pressure[2] else 'False':<5}, "
                                        f"Click: {'True' if selected_pressure[3] else 'False':<5}")
                    time.sleep(0.05)
            else:
                print("---")
                print(current_time, "Dongle disconnected. Please, re-insert the dongle and re-run the application.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("\n'Esc' key was pressed or an error occurred. Exiting application...")
        etee.stop_data()  # Stop controller data stream
        print("Controller data stream stopped.")
        etee.stop()  # Stop data loop
        print("Data loop stopped.")
        time.sleep(0.05)
        listener.stop()
        sys.exit(0)  # Exit driver
