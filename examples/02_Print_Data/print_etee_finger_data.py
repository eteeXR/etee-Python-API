"""
Example code:
-------------
This script prints the finger values (pressure: pull and force, touch, click) from the selected finger in an
eteeController, using getter functions.
"""

import time
import sys
from pynput import keyboard
from datetime import datetime
from etee import EteeController

def on_press(key):
    if key == keyboard.Key.esc:
        return False  # Stop listener

def process_finger(dev, finger):
    """
    Retrieve the selected device's finger values from the etee driver.

    :param str dev: Selected device hand. Possible values: "left", "right".
    :param str finger: Selected finger. Possible values: "thumb", "index", "middle", "ring", "pinky".
    :return: Array containing the selected controller's index finger values: pull pressure, force pressure,
    touch and click.
    :rtype: list[Any]
    """
    finger_pull = finger + "_pull"
    finger_force = finger + "_force"
    finger_touch = finger + "_touched"
    finger_click = finger + "_clicked"

    finger_data = [etee.get_data(dev, finger_pull), etee.get_data(dev, finger_force),
                   etee.get_data(dev, finger_touch), etee.get_data(dev, finger_click)]
    return finger_data


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
    print("Welcome to this etee CLI application.\nYou can print an individual finger data here.")
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

    # Prompt for user to select the finger to print values from
    print("---")
    print("Please, enter a finger name. Valid options: thumb, index, middle, ring, pinky.")
    valid_fingers = ["thumb", "index", "middle", "ring", "pinky"]
    finger_selected = input("Enter finger name: ")
    while finger_selected not in valid_fingers:
        print("Input not valid! Please enter a valid input: thumb, index, middle, ring, pinky.")
        finger_selected = input("--> Enter finger name: ")
    print("Your selected finger: ", finger_selected)
    print("Press 'Esc' key to exit the application.")

    # Create a keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    # If dongle is connected, print index values
    try:
        while listener.running:
            current_time = datetime.now().strftime("%H:%M:%S.%f")
            num_dongles_available = etee.get_number_available_etee_ports()

            if num_dongles_available > 0:
                selected_finger = process_finger(controller_selected, finger_selected)
                if selected_finger[0] == None:
                    print("---")
                    print(current_time, f"The {controller_selected} etee controller was not detected. Please reconnect controller.")
                    etee.start_data()   # If a controller has reconnected with the dongle, it will start etee controller data stream
                    time.sleep(0.05)
                else:
                    print(current_time, f"Selected: {controller_selected} {finger_selected} --> "
                                        f"Pressure (pull: {selected_finger[0]:<3}, force: {selected_finger[1]:<3}) | "
                                        f"Touch: {'True' if selected_finger[2] else 'False':<5} | "
                                        f"Click: {'True' if selected_finger[3] else 'False':<5}")
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