"""
Example code:
-------------
This script starts a liveplot of the selected eteeController's Euler angles.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import time
from etee import EteeController
from math import pi
rad2deg_factor = 180/pi


# Ask user to select between left or right controller
def select_hand():
    # Prompt for user to select the hand to print values from
    print("Please, enter what controller hand you would like to print the values from. Valid options: right, left.")
    valid_controllers = ["right", "left"]
    controller_selected = input("--> Enter controller hand: ")
    while controller_selected not in valid_controllers:
        print("Input not valid! Please enter a valid input: right, left.")
        controller_selected = input("--> Enter controller hand: ")
    print("Your selected controller hand: ", controller_selected)
    return controller_selected


# This function is called periodically from FuncAnimation
def animate(i, y_1, y_2, y_3):
    # Retrieve euler angles
    euler_angles_rad = etee.get_euler(device)

    # Get euler angles
    if euler_angles_rad is not None:
        euler_angles_deg = [euler_angles_rad[0] * rad2deg_factor + 180,
                            euler_angles_rad[1] * rad2deg_factor + 180,
                            euler_angles_rad[2] * rad2deg_factor + 180]
    else:
        euler_angles_deg = [0, 0, 0]

    roll = round(euler_angles_deg[0], 3)
    pitch = round(euler_angles_deg[1], 3)
    yaw = round(euler_angles_deg[2], 3)

    # Add y to list
    y_1.append(roll)
    y_2.append(pitch)
    y_3.append(yaw)

    # Limit y list to set number of items
    y_1 = y_1[-x_len:]
    y_2 = y_2[-x_len:]
    y_3 = y_3[-x_len:]

    # Update line with new Y values
    line_1.set_ydata(y_1)
    line_2.set_ydata(y_2)
    line_3.set_ydata(y_3)

    return line_1, line_2, line_3,


if __name__ == "__main__":
    # ------------ Initialise etee ------------
    # Initialise the etee driver and find dongle
    etee = EteeController()
    num_dongles_available = etee.get_number_available_etee_ports()
    if num_dongles_available > 0:
        etee.connect()  # Attempt connection to etee dongle
        time.sleep(1)
        etee.start_data()  # Attempt to send a command to etee controllers to start data stream
        etee.run()  # Start data loop
    else:
        print("No dongle found. Please, insert an etee dongle and re-run the application.")
        sys.exit("Exiting application...")

    # Ask user for the hand data to plot
    device = select_hand()

    # Turn absolute IMU off
    etee.absolute_imu_enabled(False)

    # ------------ Initialise graph ------------
    # Parameters
    x_len = 200  # Number of points to display
    y_range = [0, 360]  # Range of possible Y values to display

    # Create figure for plotting
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    xs = list(range(0, 200))
    ys_1 = [0] * x_len
    ys_2 = [0] * x_len
    ys_3 = [0] * x_len

    ax.set_ylim(y_range)

    # Create a blank line. We will update the line in animate
    line_1, = ax.plot(xs, ys_1)
    line_2, = ax.plot(xs, ys_2)
    line_3, = ax.plot(xs, ys_3)

    # Add labels
    plt.title('Live Plot of Euler angles')
    plt.xlabel('Samples')
    plt.ylabel('Euler angles (degrees)')
    plt.legend([line_1, line_2, line_3], ['Roll', 'Pitch', 'Yaw'])

    # ------------ Plot live values ------------
    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(ys_1, ys_2, ys_3,), interval=50, blit=True)
    plt.show()
