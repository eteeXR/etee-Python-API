.. _EventClass:

###########
Event Class
###########

Here you can find the list of methods from the Event class, which allow callback functions to be connected or disconnected from
etee events, defined in the :class:`etee.driver_eteecontroller.EteeController` class.

.. autoclass:: etee.driver_eteecontroller.EteeControllerEvent

	.. automethod:: etee.driver_eteecontroller.EteeControllerEvent.connect(callback)

	.. automethod:: etee.driver_eteecontroller.EteeControllerEvent.disconnect(callback)

	.. automethod:: etee.driver_eteecontroller.EteeControllerEvent.emit()
