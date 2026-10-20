########################
3. Using etee Python API
########################

3.1. Quickstart
===============

etee driver automatically detects an eteeDongle and connects to it through the EteeController class' **connect()** method. To start the eteeController
data stream, call the class **start_data()**, followed by the **run()** method to initiate the data loop. While the data loop is running,
the etee driver will read the eteeController serial data, parse it and store the results in its internal buffer.

.. code-block:: python
   :linenos:

   # Import the etee API library
   from etee import EteeController

   # Instantiate the driver class
   etee = EteeController()

   etee.connect()     # Connect the eteeDongle to the driver
   etee.start_data()  # Request eteeControllers to start data stream
   etee.run()         # Start data loop

Once the driver is running, **data getter** functions can be called to get etee data.

.. code-block:: python

   while True:
      # Data getter functions
      left_trackpad_x = etee.get_trackpad_x('left')
      left_trackpad_y = etee.get_trackpad_y('left')

      # Print the values
      print(f"Finger touch identified at position [{left_trackpad_x}, {left_trackpad_y}] in the left eteeController.")
      time.sleep(0.01)

For more information, see: :ref:`DataGetters`.

Alternatively, it may be preferable to retrieve data through an **event-based method**, where data processing functions can be added as callbacks to data events.

.. code-block:: python

   # Function to be added as callback
   def process_left_index_pressure():
      left_index_pull = etee.get_index_pull('left')
      left_index_force = etee.get_index_force('left')
      print(f"The pressure of the left index finger is: pull = {left_index_pull}, force = {left_index_force}.")

   # Connect callback to data reception events
   etee.left_hand_received.connect(process_left_index_pressure)

After this, when the driver starts running, the `process_left_index_pressure()` function will run every time a left-hand data packet is received by the driver.

The API library defines a few events, such as data receiving events and device connection/disconnection events, among others. A callback function can be
connected to any of these events. For more information, see: :ref:`Events`.

3.2. Methods and Class Constructors
===================================

You can find the full reference of available methods and classes under the :ref:`APIReference` section.
