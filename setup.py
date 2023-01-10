"""
Script to automate the etee_api package installation.
To use this file, navigate to the directory where setup.py is located and use the command:.
   ----------------
   $ pip install .
   ----------------
This will automatically install the package in your environment.
"""

from setuptools import setup, find_packages
from etee import __version__

setup(
    name="etee-api",
    version=__version__,
    python_requires='>=3.8, <4',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.22.3',
        'bitstring>=3.1.9',
        'pyserial>=3.5',
        'PyYAML>=3.12',
    ],
    package_data={'etee': ['config/*.yaml']},
    author="Dimitri Chikhladze, Pilar Zhang Qiu",
    author_email="pilar@tg0.co.uk",
    description="Official Python API for the eteeController devices. "
                "This API enables easy device data reading and communication. "
                "To learn more about the controllers, visit: eteexr.com .",
    url='https://github.com/eteexr',
    license='Apache-2.0',
    license_files='LICENSE.txt'
)
