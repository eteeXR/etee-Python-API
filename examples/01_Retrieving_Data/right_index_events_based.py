"""
Example code:
-------------
This script shows how to use event-based methods to retrieve controller data.
In this case, the process_right_index() callback function is connected to the right_hand_received event.
This will cause the callback function (which prints controller data) to be called every time that data from the
right controller is received by the dongle, and subsequently transmitted to the driver.
"""

import time
import sys
import keyboard
from datetime import datetime
from etee import EteeController


def process_right_index():
    right_index_pull = etee.get_index_pull('right')
    right_index_force = etee.get_index_force('right')
    current_time = datetime.now().strftime("%H:%M:%S.%f")
    print(current_time, f"The right index pressure is: pull = {right_index_pull:>3}  |  force = {right_index_force:>3}")


if __name__ == "__main__":
    # Initialise the etee driver
    etee = EteeController()
    num_dongles_available = etee.get_number_available_etee_ports()
    if num_dongles_available > 0:
        etee.right_hand_received.connect(process_right_index)   # Add the process_right_index() function
                                                                # as callbacks when right controller data is received
        etee.connect()      # Attempt connection to etee dongle
        time.sleep(1)
        etee.start_data()   # Attempt to send a command to etee controllers to start data stream
        etee.run()          # Start data loop
    else:
        print("---")
        print("No dongle found. Please, insert an etee dongle and re-run the application.")
        sys.exit("Exiting application...")

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
            # If no data received from controller, retry controller connection
            # If no dongle is connected, exit application
            num_dongles_available = etee.get_number_available_etee_ports()
            if num_dongles_available == 0:
                print("---")
                print("Dongle disconnected. Please, re-insert the dongle and re-run the application.")

                etee.stop_data()  # Stop controller data stream
                print("Controller data stream stopped.")
                etee.stop()  # Stop data loop
                print("Data loop stopped.")

                time.sleep(0.05)
                sys.exit("Exiting application...")