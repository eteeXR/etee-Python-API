################################
4. About the API Functionalities
################################

.. contents:: On this page
   :local:

---------------------------------------------------

4.1. Creating Connections and Streaming Data
============================================
Serial connection between the driver and the eteeDongle is established by calling the **connect()** function.
This function automatically detects the COM port numbers of available eteeDongles through a VID filtering system
and creates a connection to the first instance. Connection to specific ports can also be established by calling the **connect_port()** function instead; however, it is recommended to use the default connect() function.

The **start_data()** function sends a serial command instructing the eteeControllers to start streaming sensor data.

The **run()** functions starts a data loop in a separate thread. The data loop reads serial data, parses it and stores it in an internal buffer.
The data loop also listens to serial and data events and manages event callback functions.

.. code-block:: python
   :linenos:

   etee = EteeController()
   etee.connect()
   etee.start_data()
   etee.run()

To stop the etee driver, run the **stop()** function. To command the eteeControllers to stop streaming data, call the **stop_data()** function.
To close the connection between the eteeDongle and the eteeControllers, run the **disconnect()** function.

.. code-block:: python
   :linenos:

   etee.stop()
   etee.stop_data()
   etee.disconnect()

---------------------------------------------------

4.2. Retrieving Device Inputs
=============================

There are two ways to retrieve data from the eteeControllers, either using data getter functions or through event-based programming.

.. _DataGetters:

4.2.1. Data Getters Functions
-----------------------------

Once the eteeController data stream is opened and the data loop is running, etee data is accessible through two methods: data getters and event-based methods.

When called, **data getter** functions retrieve the last data available in the internal buffer.

There are general-use data getters and specific-use data getters. For the general-use getters, the keys for the data and/or device
to be retrieved need to be passed as arguments. In the case of the specific-use ones, these data getter functions retrieve specific tactile, gestures, IMU or device state values.

.. code-block:: python
   :linenos:

   # General-use data getters
   right_index_pull = etee.get_data("right", "index_pull")  # Option 1: get_data(dev, w)
   right_index_pull = etee.get_right("index_pull")          # Option 2: get_right(w) or get_left(w)

   # Specific-use data getters
   right_index_pull = etee.get_index_pull("right")

For the full list of input keys for the general-use getters, see :ref:`CrossReferenceLabel`.

For the full list of available data getters, particularly the specific-use getter functions,
see: :ref:`EteeControllerDataGetters`.

4.2.2. Event-Based Methods
--------------------------

The data getter functions can be specified as callbacks to be connected to specific events. For instance,
we can connect functions to process left finger data only when data packets corresponding to the left eteeController
are received. To learn more, see: :ref:`Events`.

---------------------------------------------------

.. _IMUguide:

4.3. How IMU Data Is Processed
==============================
The serial data includes raw IMU data which consist of accelerometer, gyroscope and magnetometer data. Data getter methods are available for IMU data retrieval, as defined in: :ref:`EteeControllerDataGetters`.
If the corresponding IMU data exists (i.e. is different from None), the data getters will return a list containing their x, y and z-axis values.

.. code-block:: python
   :linenos:

   # Data getter for accelerometer
   left_accel = etee.get_accel("left")
   left_accel_x = left_accel[0]

   # Data getters for gyroscope
   left_gyro = etee.get_gyro("left")
   left_gyro_y = left_gyro[1]

   # Data getters for magnetometer
   left_mag = etee.get_mag("left")
   left_mag_z = left_mag[2]

The API library also provides methods to retrieve orientation data in the form of quaternions. The quaternion is computed during each data loop.

.. code-block:: python
   :linenos:

   # Data getters for quaternions
   quaternion_left = etee.get_quaternion("left")
   quaternion_right = etee.get_quaternion("right")

Before using quaternions, **update_imu()** should be called. This function retrieves the IMU calibration data stored in the eteeControllers and uses it to compute the quaternions.
Without calling this function, the calculated quaternions will not use the latest IMU calibration data. The IMU can be re-calibrated using the eteeConnect software, which will modify the
internal IMU calibration parameters.

For orientation data, the user can also choose to use **absolute** or **relative orientation**. The former uses magnetometer data, while the latter does not.
By default, absolute orientation is enabled.

.. code-block:: python
   :linenos:

   # Absolute orientation is the default, but it can also be set as shown below
   # This will use the magnetometer data.
   etee.enable_absolute_imu(True)

   # To disable the absolute orientation and switch to relative orientation
   # This will NOT use the magnetometer data.
   etee.enable_absolute_imu(False)

---------------------------------------------------

.. _Events:

4.4. Event-Based Programming
============================
The etee API library supports event-based programming. Several serial and data events are defined. Each event can be connected to callback functions which will be triggered when the event is identified within the data loop.

A callback function can be connected to an event by calling the **connect()** method.

The data events **left_hand_received** and **right_hand_received** occur respectively when data packets from the left or the right eteeController are received. In the code sample below,
as long as the data loop is running, the processing functions will be called every time the corresponding hand data packet is received.

.. code-block:: python
   :linenos:

   # Processing functions
   def process_left_hand():
      left_fingers_pulls, left_fingers_forces = etee.get_device_finger_pressures("left")
      print(f"The pressure of the left pinky finger is: pull = {left_fingers_pulls[4]}, force = {left_fingers_forces[4]}.")

   def process_right_hand():
      right_fingers_pulls, right_fingers_forces = etee.get_device_finger_pressures("right")
      print(f"The pressure of the right thumb finger is: pull = {right_fingers_pulls[4]}, force = {right_fingers_forces[4]}.")

   # Connect the processing functions as callbacks for the events
   etee.left_hand_received.connect(process_left_hand)
   etee.right_hand_received.connect(process_right_hand)

Another example of data events are **left_hand_lost** and **right_hand_lost**. These events are triggered when the signal
is lost from the left and right eteeController, respectively. Signal loss is defined as no data having been received from the eteeControllers
in the last 0.5 seconds.

.. code-block:: python
   :linenos:

   # Functions to be invoked
   def on_left_hand_lost():
	   print(f"The left data was lost.")

   def on_right_hand_lost():
	  print(f"The right data was lost.")

   # Connect the functions as callbacks for the events
   etee.left_hand_lost.connect(on_left_hand_lost)
   etee.right_hand_lost.connect(on_right_hand_lost)

An example of a serial event is **dongle_disconnected**, which occurs when the serial connection to the eteeDongle is disrupted.

.. code-block:: python
   :linenos:

   # Function to be invoked
   def on_dongle_disconnect():
	   print(f"The eteeDongle has been disconnected.")

   # Connect the function as a callback for the event
   etee.dongle_disconnected.connect(on_dongle_disconnect)

For the full API library reference for data and serial events, see: :ref:`EteeControllerDataGetters`.

---------------------------------------------------

.. _ResetBaselineGuide:

4.6. Resetting Sensor Baselines
===============================
If the finger curl data or other sensor data seem wrong, the easiest way to fix this is by triggering a quick calibration.

Quick calibration resets the electrodes signal baseline. For instance, if your real index finger is fully open but your virtual one appears to be flexed (i.e. index_pull is 55, instead of 0),
a quick calibration will fix the issue (i.e. index_pull will be reset to 0).

**Steps for quick calibration:**

1. Please, ensure that your or the user's **fingers are fully stretched out**, as illustrated below.

   .. image:: /images/hand_calibration.png
      :width: 50%
      :alt: Hand position required when performing quick calibration.
      :align: center

2. **Trigger quick calibration** by using API commands or the physical button.

 - **API commands**: You can send a quick calibration command to both or a single eteeController by writing the commands through serial communication to the eteeDongle.

   .. code-block:: python
      :linenos:

      # Quick calibrate all devices connected to eteeDongle
      response = self.driver.send_command(b"BP+AB\r\n")

      # Quick calibrate the right eteeController if connected to eteeDongle
      response = self.driver.send_command(b"BR+AB\r\n")

      # The response returns 'OK' when the command is successfully sent
      print(response)

 - **Physical button**: You can also trigger quick calibration by double-clicking the system button of the eteeController that you wish to reset the baselines.

   .. image:: /images/double_click_system.png
      :width: 30%
      :alt: Double-clicking the system button (i.e. ON/OFF button) will trigger quick calibration.
      :align: center

3. This process is **instantaneous** and does not require any waiting time.

.. note::
   This is **not the same as the full/advanced calibration** that takes place in eteeConnect.

   We won't be providing any commands for this as it's a complicated step by step process. However, you should only need to run a full/advanced calibration if a different person is using the eteeControllers.
   In all other cases, a quick calibration will suffice.
