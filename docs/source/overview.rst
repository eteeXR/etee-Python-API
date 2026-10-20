###########
1. Overview
###########

.. contents:: On this page
   :local:

---------------------------------------------------

1.1. Hardware
=============
**etee hardware consists of** one eteeDongle and two eteeControllers (left and right hand). Optionally, etee trackers can be attached to eteeControllers for VR use.

An eteeDongle connects to a computer through a serial port, while the eteeControllers connect to an eteeDongle through BLE communication.

The eteeControllers use **TG0's sensing technology** to provide tactile data. This tactile data tracks the movement and pressure from all five fingers, and provides additional inputs such as trackpad XY positional data.
In-built IMU sensors also allow for the detection of the eteeController translation and rotation. These tactile and IMU data are included into a data packet, which is sent by the eteeControllers
to the eteeDongle. This packet can then be accessed through serial communication with the eteeDongle. Data packets from each eteeController are streamed at a rate of approximately 100 packets/second.

---------------------------------------------------

1.2. Sensor Data
================

1.2.1. Tactile Data
-------------------

**Tactile sensors** can be found in the eteeControllers's main body, trackpad, and LED slider. If an etee tracker is attached, an additional proximity button can be accessed.

.. image:: /images/etee_controller_sensors.jpg
   :width: 100%
   :alt: eteeController tactile sensors
   :align: center

The finger tracking sensors are located in the eteeController's main body. For each finger, the eteeController detects two different levels of pressure, as well as touch and clicks.
At the top of the device, there is a tactile trackpad. The eteeController estimates the XY position of a thumb on the trackpad and can also measure pressure and detect touch and click events.
At the front of the main body, there is a LED light which also acts as a tactile sensor.
If a tracker is connected to the eteeController, an additional proximity sensor can be used, located in the area around the tracker button.
You can also retrieve the state of the system button (i.e. power button) located at the bottom of the device.

.. image:: /images/etee-gestures.jpg
   :width: 100%
   :alt: Gestures detected by the eteeController
   :align: center

**Multi-finger gesture detection** is also provided by the device as grip, pinch and point gestures.

For more information on the retrievable values for each sensor or gesture, see :ref:`PacketTactileData` or :ref:`PacketGestures`.

For more information on how to retrieve these values, see :ref:`DataGetters`.


1.2.2. Inertial Measuring Units (IMU) Data
------------------------------------------
The IMU data consists of **acceleration, angular acceleration and magnetic flux density** data from the eteeControllers.
This data is used by the library to estimate the spatial orientation of the eteeControllers through the calculation of **quaternions** and **Euler angles**.

For more information on the retrievable values from the IMU sensors, see :ref:`PacketIMU`.

For more information on how to retrieve these values, see :ref:`IMUguide`.


1.2.3. Device and Battery State Data
------------------------------------
Device state data includes information such as eteeController **handedness** (i.e. right or left) and **battery data**.

For more information on the retrievable values from the IMU sensors, see :ref:`PacketDeviceState` or :ref:`PacketBattery`.
