"""
License:
--------
Copyright 2022 Tangi0 Ltd. (trading as TG0)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


File description:
-----------------
Class and methods for the Attitude and Heading Reference System (AHRS) calculations.
Includes methods to set the IMU sensor offsets, update the AHRS or calculate the device quaternions.

"""

import math
from queue import Queue
import time
import warnings

import numpy as np
from numpy.linalg import norm
from etee import Quaternion


class Ahrs:
    """
    Class implementing Attitude and Heading Reference System (AHRS) calculations.
    """
    beta = 0.0315
    accel_sensitivity = 4.0 / 32768.0
    gyro_sensitivity = (2000.0 / 32768.0) * (math.pi/180)
    mag_sensitivity = [0.38, 0.38, 0.61]

    @staticmethod
    def _current_seconds_time():
        """
        Get current time.

        :return: current time as float
        """
        return time.time()

    def __init__(self, sampleperiod=None, quaternion=None, beta=None):
        """
        Initialize the class with the given parameters.

        :param float sampleperiod: the sample period
        :param list[float] quaternion: initial quaternion
        :param float beta: algorithm gain beta
        """
        if sampleperiod is not None:
            self.samplePeriod = sampleperiod
        if quaternion is not None:
            self.quaternion = quaternion
        if beta is not None:
            self.beta = beta

        self.samplePeriod = 1/97
        self.quaternion = Quaternion(1, 0, 0, 0)
        self.euler = [0, 0, 0]
        self.dynamicFrequencyQueue = Queue(100)

        self.gyro_offset = [0, 0, 0]
        self.mag_offset = [0, 0, 0]

    def set_gyro_offset(self, value):
        """
        Set gyroscope offsets to given values.

        :param list[float] value: New gyroscope offset values
        """
        self.gyro_offset = value

    def set_mag_offset(self, value):
        """
        Set magnetometer offsets to given values.

        :param list[float] value: New magnetometer offset values
        """
        self.mag_offset = value

    def update(self, gyroscope, accelerometer, magnetometer):
        """
        Perform one update step with data from a AHRS sensor array.

        :param list[float] gyroscope: A three-element array containing the gyroscope data in radians per second.
        :param list[float] accelerometer: A three-element array containing the accelerometer data.
                                        Can be any unit since a normalized value is used.
        :param list[float] magnetometer: A three-element array containing the magnetometer data.
                                        Can be any unit since a normalized value is used.
        """
        q = self.quaternion

        gyroscope = np.array(gyroscope, dtype=float).flatten()
        accelerometer = np.array(accelerometer, dtype=float).flatten()
        magnetometer = np.array(magnetometer, dtype=float).flatten()

        # Normalise accelerometer measurement
        if norm(accelerometer) == 0:
            warnings.warn("accelerometer is zero")
            return
        accelerometer /= norm(accelerometer)

        # Normalise magnetometer measurement
        if norm(magnetometer) == 0:
            warnings.warn("magnetometer is zero")
            return
        magnetometer /= norm(magnetometer)

        h = q * (Quaternion(0, magnetometer[0], magnetometer[1], magnetometer[2]) * q.conj())
        b = np.array([0, norm(h[1:3]), 0, h[3]])

        # Gradient descent algorithm corrective step
        f = np.array([
            2*(q[1]*q[3] - q[0]*q[2]) - accelerometer[0],
            2*(q[0]*q[1] + q[2]*q[3]) - accelerometer[1],
            2*(0.5 - q[1]**2 - q[2]**2) - accelerometer[2],
            2*b[1]*(0.5 - q[2]**2 - q[3]**2) + 2*b[3]*(q[1]*q[3] - q[0]*q[2]) - magnetometer[0],
            2*b[1]*(q[1]*q[2] - q[0]*q[3]) + 2*b[3]*(q[0]*q[1] + q[2]*q[3]) - magnetometer[1],
            2*b[1]*(q[0]*q[2] + q[1]*q[3]) + 2*b[3]*(0.5 - q[1]**2 - q[2]**2) - magnetometer[2]
        ])
        j = np.array([
            [-2*q[2],                  2*q[3],                  -2*q[0],                  2*q[1]],
            [2*q[1],                   2*q[0],                  2*q[3],                   2*q[2]],
            [0,                        -4*q[1],                 -4*q[2],                  0],
            [-2*b[3]*q[2],             2*b[3]*q[3],             -4*b[1]*q[2]-2*b[3]*q[0], -4*b[1]*q[3]+2*b[3]*q[1]],
            [-2*b[1]*q[3]+2*b[3]*q[1], 2*b[1]*q[2]+2*b[3]*q[0], 2*b[1]*q[1]+2*b[3]*q[3],  -2*b[1]*q[0]+2*b[3]*q[2]],
            [2*b[1]*q[2],              2*b[1]*q[3]-4*b[3]*q[1], 2*b[1]*q[0]-4*b[3]*q[2],  2*b[1]*q[1]]
        ])
        step = j.T.dot(f)
        step /= norm(step)  # normalise step magnitude

        # Compute rate of change of quaternion
        qdot = (q * Quaternion(0, gyroscope[0], gyroscope[1], gyroscope[2])) * 0.5 - self.beta * step.T

        # Integrate to yield quaternion
        q += qdot * self.samplePeriod
        self.quaternion = Quaternion(q / norm(q))  # normalise quaternion

    def update_imu(self, gyroscope, accelerometer):
        """
        Perform one update step with data from an IMU sensor array.

        :param list[float] gyroscope: A three-element array containing the gyroscope data in radians per second.
        :param list[float] accelerometer: A three-element array containing the accelerometer data.
                                        Can be any unit since a normalized value is used.
        """
        q = self.quaternion

        gyroscope = np.array(gyroscope, dtype=float).flatten()
        accelerometer = np.array(accelerometer, dtype=float).flatten()

        # Normalise accelerometer measurement
        if norm(accelerometer) == 0:
            return
        accelerometer /= norm(accelerometer)

        # Gradient descent algorithm corrective step
        f = np.array([
            2*(q[1]*q[3] - q[0]*q[2]) - accelerometer[0],
            2*(q[0]*q[1] + q[2]*q[3]) - accelerometer[1],
            2*(0.5 - q[1]**2 - q[2]**2) - accelerometer[2]
        ])
        j = np.array([
            [-2*q[2], 2*q[3], -2*q[0], 2*q[1]],
            [2*q[1], 2*q[0], 2*q[3], 2*q[2]],
            [0, -4*q[1], -4*q[2], 0]
        ])
        step = j.T.dot(f)
        step /= norm(step)  # normalise step magnitude

        # Compute rate of change of quaternion
        qdot = (q * Quaternion(0, gyroscope[0], gyroscope[1], gyroscope[2])) * 0.5 - self.beta * step.T

        # Integrate to yield quaternion
        q += qdot * self.samplePeriod
        self.quaternion = Quaternion(q / norm(q))  # normalise quaternion

    def get_quaternion(self, gyroscope, accelerometer, magnetometer=None):
        """
        Calculate and return the quaternion values given the IMU sensors values.

        :param list[float] gyroscope: A three-element array containing the gyroscope data in radians per second.
        :param list[float] accelerometer: A three-element array containing the accelerometer data.
                                        Can be any unit since a normalized value is used.
        :param list[float] magnetometer: A three-element array containing the magnetometer data.
                                        Can be any unit since a normalized value is used.
        :return: Quaternion calculated from the given data.
        """
        if self.dynamicFrequencyQueue.full():
            start_time = self.dynamicFrequencyQueue.get()
            current_time = self._current_seconds_time()
            self.dynamicFrequencyQueue.put(current_time)
            self.samplePeriod = (current_time - start_time)/100
        else:
            self.dynamicFrequencyQueue.put(self._current_seconds_time())

        gyroscope = np.array(gyroscope) - np.array(self.gyro_offset)
        gyroscope = gyroscope * self.gyro_sensitivity
        accelerometer = np.array(accelerometer) * self.accel_sensitivity

        if magnetometer is None:
            self.update_imu(gyroscope, accelerometer)
        else:
            magnetometer = np.array(magnetometer) - np.array(self.mag_offset)
            magnetometer = magnetometer * np.array(self.mag_sensitivity)
            self.update(gyroscope, accelerometer, magnetometer)
        return self.quaternion

    def get_euler(self, gyroscope, accelerometer, magnetometer=None):
        """
        Estimate and return the euler angles for the given IMU sensor values.

        :param list[float] gyroscope: A three-element array containing the gyroscope data in radians per second.
        :param list[float] accelerometer: A three-element array containing the accelerometer data.
                                        Can be any unit since a normalized value is used.
        :param list[float] magnetometer: A three-element array containing the magnetometer data.
                                        Can be any unit since a normalized value is used.
        :return: Euler angles estimated from the given data.
        """
        self.get_quaternion(gyroscope, accelerometer, magnetometer)
        self.euler = self.quaternion.to_euler()
        return self.euler
