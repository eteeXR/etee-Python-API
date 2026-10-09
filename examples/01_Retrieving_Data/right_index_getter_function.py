"""
Example code:
-------------
This script shows how to use getter functions to retrieve controller data.
In this case, getter functions are called every loop. Getter functions pull data from the driver internal buffer, which
gets updated every time data is received from the controllers. If event-based methods are used, the frequency of data
received from the controllers can be irregular (e.g. 5ms, or 10ms). Unlike the event-based method, getter functions
allow the user to have better control in the timing of data retrieval.
"""

import time
import sys
from pynput import keyboard
from datetime import datetime
from etee import EteeController

def on_press(key):
    if key == keyboard.Key.esc:
        return False  # Stop listener
    
def process_right_index():
    """
    Retrieve the pressure data for the right index finger from the etee driver.

    :return: Index finger pull pressure and force pressure, from the right eteeController.
    :rtype: int, int
    """
    right_index_pull = etee.get_index_pull('right')
    right_index_force = etee.get_index_force('right')
    return right_index_pull, right_index_force

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
        print("---")
        print("No dongle found. Please, insert an etee dongle and re-run the application.")
        sys.exit("Exiting application...")
    print("Press 'Esc' key to exit the application.")

    # Create a keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    # If dongle is connected, print index values
    try:
        while listener.running:
            num_dongles_available = etee.get_number_available_etee_ports()
            current_time = datetime.now().strftime("%H:%M:%S.%f")

            if num_dongles_available > 0:
                right_index_pull, right_index_force = process_right_index()
                if right_index_pull is None:
                    print("---")
                    print(current_time, "Right etee controller not detected. Please reconnect controller.")
                    etee.start_data()   # Retry reconnection and data stream access in controllers
                    time.sleep(0.05)
                else:
                    print(current_time, f"The right index pressure is: pull = {right_index_pull:>3}  |  force = {right_index_force:>3}")
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
