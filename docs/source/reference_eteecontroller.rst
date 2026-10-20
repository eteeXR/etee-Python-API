.. _EteeControllerClass:

####################
EteeController Class
####################


.. contents:: On this page
   :local:

-------

Here you can find the list of methods from the EteeController class, which acts as a driver enabling communication between the eteeControllers and
a computer through an eteeDongle.

.. autoclass:: etee.driver_eteecontroller.EteeController

Connections
===========

The following methods manage the connection between the eteeDongle and the driver, and activate/deactivate the eteeControllers data streams.

	.. automethod:: etee.driver_eteecontroller.EteeController.connect()

	.. automethod:: etee.driver_eteecontroller.EteeController.connect_port(port=None)

	.. automethod:: etee.driver_eteecontroller.EteeController.disconnect()

	.. automethod:: etee.driver_eteecontroller.EteeController.run()

	.. automethod:: etee.driver_eteecontroller.EteeController.stop()

	.. automethod:: etee.driver_eteecontroller.EteeController.start_data()

	.. automethod:: etee.driver_eteecontroller.EteeController.stop_data()

	.. automethod:: etee.driver_eteecontroller.EteeController.get_available_etee_ports()

------

Events
======

A callback function can be connected to the following events through the :meth:`etee.driver_eteecontroller.EteeControllerEvent.connect()`
method in the :class:`etee.driver_eteecontroller.EteeControllerEvent` class.

	.. autoattribute:: etee.driver_eteecontroller.EteeController.left_hand_received()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.right_hand_received()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.hand_received()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.left_hand_lost()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.right_hand_lost()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.data_lost()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.left_connected()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.right_connected()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.left_disconnected()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.right_disconnected()

	.. autoattribute:: etee.driver_eteecontroller.EteeController.dongle_disconnected()

------

IMU Processing
==============
There are also several methods that can be used to process IMU data at the start of or during your application.

Enable Absolute / Relative Orientation
--------------------------------------

The orientation can also be set to absolute (i.e. magnetometer data used) or relative (i.e. no magnetometer data used) through
the following method:

	.. automethod:: etee.driver_eteecontroller.EteeController.absolute_imu_enabled(on)

Set Offsets
-----------

Gyroscope and magnetometer offsets can be easily set at any time using the following methods:

	.. automethod:: etee.driver_eteecontroller.EteeController.update_gyro_offset_left()

	.. automethod:: etee.driver_eteecontroller.EteeController.update_gyro_offset_right()

	.. automethod:: etee.driver_eteecontroller.EteeController.update_mag_offset_left()

	.. automethod:: etee.driver_eteecontroller.EteeController.update_mag_offset_right()

	.. automethod:: etee.driver_eteecontroller.EteeController.update_imu_offsets()

------

.. _EteeControllerDataGetters:

Data getters
============

When called, data getter functions allow for the retrieval of device data from the driver's internal buffer.
You can find the full list of data getter methods from the EteeController class below.

General-Use Data Getters
------------------------

The same general-use data getter can be used to retrieve a variety of eteeController values through a single method.
For these methods, the keys for the data and/or device to be retrieved need to be passed as arguments.

Possible keys: see :ref:`CrossReferenceLabel`.

	.. automethod:: etee.driver_eteecontroller.EteeController.get_left(w)

	.. automethod:: etee.driver_eteecontroller.EteeController.get_right(w)

	.. automethod:: etee.driver_eteecontroller.EteeController.get_data(dev,w)

------

Specific-Use Data Getters
-------------------------

Unlike the general-use getter methods, the specific-use methods retrieve specific tactile, gestures, IMU or device state values from a specified eteeController.
You can find the full list of them below.

Hand/Controller Connection Status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Whether the eteeController devices are detected as connected.

	.. automethod:: etee.driver_eteecontroller.EteeController.all_hands_on()
	.. automethod:: etee.driver_eteecontroller.EteeController.any_hand_on()
	.. automethod:: etee.driver_eteecontroller.EteeController.left_hand_on()
	.. automethod:: etee.driver_eteecontroller.EteeController.right_hand_on()

------

Firmware Versions
^^^^^^^^^^^^^^^^^

Returns the eteeDongle or devices firmware version.

	.. automethod:: etee.driver_eteecontroller.EteeController.get_dongle_version()
	.. automethod:: etee.driver_eteecontroller.EteeController.get_etee_versions()

------

Finger Data
^^^^^^^^^^^

Thumb Finger Data
~~~~~~~~~~~~~~~~~

	.. automethod:: etee.driver_eteecontroller.EteeController.get_thumb_pull(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_thumb_force(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_thumb_touched(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_thumb_clicked(dev)

Index Finger Data
~~~~~~~~~~~~~~~~~

	.. automethod:: etee.driver_eteecontroller.EteeController.get_index_pull(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_index_force(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_index_touched(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_index_clicked(dev)

Middle Finger Data
~~~~~~~~~~~~~~~~~~

	.. automethod:: etee.driver_eteecontroller.EteeController.get_middle_pull(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_middle_force(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_middle_touched(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_middle_clicked(dev)

Ring Finger Data
~~~~~~~~~~~~~~~~

	.. automethod:: etee.driver_eteecontroller.EteeController.get_ring_pull(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_ring_force(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_ring_touched(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_ring_clicked(dev)

Pinky Finger Data
~~~~~~~~~~~~~~~~~

	.. automethod:: etee.driver_eteecontroller.EteeController.get_pinky_pull(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_pinky_force(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_pinky_touched(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_pinky_clicked(dev)

Pressure from all fingers
~~~~~~~~~~~~~~~~~~~~~~~~~

	.. automethod:: etee.driver_eteecontroller.EteeController.get_device_finger_pressures(dev)

Trackers Connection Status
^^^^^^^^^^^^^^^^^^^^^^^^^^

	.. automethod:: etee.driver_eteecontroller.EteeController.get_tracker_connections()
	.. automethod:: etee.driver_eteecontroller.EteeController.get_tracker_connection(dev)

Trackers Data - Proximity Sensor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

	.. automethod:: etee.driver_eteecontroller.EteeController.get_proximity(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_proximity_touched(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_proximity_clicked(dev)

Trackpad Data
^^^^^^^^^^^^^

	.. automethod:: etee.driver_eteecontroller.EteeController.get_trackpad_x(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_trackpad_y(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_trackpad_xy(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_trackpad_pull(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_trackpad_force(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_trackpad_touched(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_trackpad_clicked(dev)

LED - Slider Data
^^^^^^^^^^^^^^^^^

	.. automethod:: etee.driver_eteecontroller.EteeController.get_slider_value(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_slider_touched(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_slider_up_button(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_slider_down_button(dev)

Gestures
^^^^^^^^

Grip Gesture
~~~~~~~~~~~~

	.. automethod:: etee.driver_eteecontroller.EteeController.get_grip_pull(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_grip_force(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_grip_touched(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_grip_clicked(dev)

Pinch Gesture - Trackpad Variation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pinch Variation:** The standard pinch gesture is triggered by pressing the trackpad and index finger

	.. automethod:: etee.driver_eteecontroller.EteeController.get_pinch_trackpad_pull(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_pinch_trackpad_clicked(dev)

Pinch Gesture - Thumb Finger Variation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Pinch Variation:** This alternative pinch gesture is triggered by pressing the thumb finger and index finger, instead of the trackpad as shown in the standard pinch.

	.. automethod:: etee.driver_eteecontroller.EteeController.get_pinch_thumbfinger_pull(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_pinch_thumbfinger_clicked(dev)

Point Gesture - Exclude Trackpad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Point Variation:** In the standard point gesture, the trackpad must not be touched.

	.. automethod:: etee.driver_eteecontroller.EteeController.get_point_excl_tp_clicked(dev)

Point Gesture - Independent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Point Variation:** In this alternative point gesture, the trackpad can be used alongside this point gesture.

	.. automethod:: etee.driver_eteecontroller.EteeController.get_point_independent_clicked(dev)

IMU and Quaternions
^^^^^^^^^^^^^^^^^^^

This API provides estimations of device three-dimensional orientation in the form of **quaternions** and **Euler angles**.

	.. automethod:: etee.driver_eteecontroller.EteeController.get_quaternion()
	.. automethod:: etee.driver_eteecontroller.EteeController.get_euler()

Raw data from the 9-axis IMU can also be retrieved using the following methods:

	.. automethod:: etee.driver_eteecontroller.EteeController.get_accel(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_gyro(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_mag(dev)

Battery
^^^^^^^

	.. automethod:: etee.driver_eteecontroller.EteeController.get_battery_level(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_charging_in_progress_status(dev)
	.. automethod:: etee.driver_eteecontroller.EteeController.get_charging_complete_status(dev)

System/Power Button
^^^^^^^^^^^^^^^^^^^

	.. automethod:: etee.driver_eteecontroller.EteeController.get_system_button_pressed(dev)
