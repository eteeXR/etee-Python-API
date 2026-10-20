########
2. Setup
########

.. contents:: On this page
   :local:

---------------------------------------------------

2.1. Hardware Setup
===================

If this is your first time using the eteeControllers, please visit the `etee XR guide page <https://eteexr.com/pages/guides>`__ for more information
on hardware setup. To interface with the etee Python API library, you will need a minimum of one `eteeDongle <https://eteexr.com/products/new-dongle-page>`__ and one `eteeController <https://eteexr.com/products/new-eteecontrollers>`__.

.. tip::
   It is also recommended to download the `official etee Connect application <https://store.steampowered.com/app/1590110/eteeConnect/>`__, available in the Steam store. This application
   allows the user to visualize real-time sensor data from the eteeControllers, as well as update the devices' firmware or pair them, among many other features.

2.1.1. Controllers and eteeDongle Connection
--------------------------------------------

Before getting started with the etee Python API, check the connection between your eteeControllers and eteeDongle.

First, **plug your eteeDongle** to your laptop or PC; when connected correctly, the LED indicator in the eteeDongle should consistently blink blue. If not, try re-plugging
the eteeDongle.

Afterwards, **turn on your eteeController(s)**. Now, the eteeDongle should blink pink once if there is one eteeController connected to the eteeDongle, or twice if there are two
eteeControllers connected. If the eteeDongle shows no connection with the eteeControllers, try pairing the devices again through the official *etee Connect* app, with the ':menuselection:`Settings --> Pair Devices`' feature. You
should also check that the eteeControllers and eteeDongle have compatible firmware versions.

2.1.2. Firmware Versions
------------------------

The device firmware versions required for this API are:

* **eteeDongle Firmware**: 1.1.7 or higher.
* **eteeController(s) Firmware**: 1.3.2 or higher.

Firmware for etee devices can be updated through the official *etee Connect* app, under the ':menuselection:`Settings --> Firmware`' Section.

---------------------------------------------------

2.2. Python Package Setup
=========================

The etee Python API requires Python 3.8 or higher. We highly recommend setting a virtual environment for your project, and installing this package within the environment.

.. tip::
   **Note:** You will need the pip package to run the installation. If you do not have Python or pip installed, follow the `Python guide on package installation <https://packaging.python.org/en/latest/tutorials/installing-packages/>`__.

2.2.1. Install from Github
--------------------------
If you wish to install the API package, see our `step-by-step guides <https://github.com/eteeXR/etee-Python-API>`__ to install this package using the Github repository.
