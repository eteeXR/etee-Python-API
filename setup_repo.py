"""
Script to automate setting up of skeleton repository by setting up a virtual environment and installing requirements.
By default this is a python 3 virtual environment called venv. The script will install any missing dependencies.
"""

import os
import subprocess
import sys
import platform


# Check OS and use proper command
if platform.system() == "Windows":
    which_command = "where"
else:
    which_command = "which"

# Check that virtualenv is installed, and if not install it.
print("Looking for virtualenv...")
which_venv = subprocess.call([which_command, "virtualenv"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
if which_venv == 1:
    print("Virtualenv not installed, installing...")
    install_venv = subprocess.run(["pip", "install", "virtualenv"])
    if install_venv.returncode != 0:
        print("Virtualenv installation failed, please install manually and then run this script again")
        exit(1)
    else:
        print("Virtualenv installation successful")
elif which_venv == 0:
    which_venv = subprocess.check_output([which_command, "virtualenv"])
    print("Virtualenv found at {}".format(which_venv.decode('utf-8').rstrip()))
else:
    print("ERROR")
    exit(1)

# If it doesn't exist already, create the virtual environment
print("Looking for venv...")
if not os.path.isdir("venv/"):
    print("Not found, creating...")
    # System independent way of finding the python executable
    # Linux should return /usr/bin/python3
    python_source = "--python={}".format(str(sys.executable))
    create_venv = subprocess.run(["virtualenv", python_source, "venv"])
    if create_venv.returncode != 0:
        print("Virtual environment 'venv' creation failed, please create it manually and then run this script again")
        exit(1)
    else:
        print("Virtual environment 'venv' created successfully")
else:
    print("Virtual environment 'venv' already exists")

# Activate the virtual environment (so we're running using the python in venv rather than the global one)
print("Activating virtual environment venv")
if platform.system() == "Windows":
    exec(open("venv/Scripts/activate_this.py").read(), dict(__file__="venv/Scripts/activate_this.py"))
else:
    # Linux and MacOS (untested)
    exec(open("venv/bin/activate_this.py").read(), dict(__file__="venv/bin/activate_this.py"))

# Install the requirements from the file 'requirements.txt'
install_reqs = subprocess.run(["pip", "install", "-r", "requirements.txt"])
if install_reqs.returncode != 0:
    print("Failed to install some requirements, please install them manually and then run this script again")
    exit(1)
else:
    print("Requirements successfully installed")

