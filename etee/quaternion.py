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
Class and methods for quaternion arithmetics and euler angle estimations.

"""

import numbers
import numpy as np
import math


class Quaternion:
    """
    Class implementing basic quaternion arithmetics and euler angle estimations.
    """
    def __init__(self, w_or_q, x=None, y=None, z=None):
        """
        Initializes a Quaternion object.

        :param float w_or_q: A scalar representing the real part of the quaternion, another Quaternion object or a
                    four-element array containing the quaternion values.
        :param float x: The first imaginary part if w_or_q is a scalar.
        :param float y: The second imaginary part if w_or_q is a scalar.
        :param float z: The third imaginary part if w_or_q is a scalar.
        """
        self._q = np.array([1, 0, 0, 0])

        if x is not None and y is not None and z is not None:
            w = w_or_q
            q = np.array([w, x, y, z])
        elif isinstance(w_or_q, Quaternion):
            q = np.array(w_or_q.q)
        else:
            q = np.array(w_or_q)
            if len(q) != 4:
                raise ValueError("Expecting a 4-element array or w x y z as parameters")

        self._set_q(q)

    # ---------------- Quaternion specific interfaces ----------------
    def conj(self):
        """
        Returns the conjugate of the quaternion

        :return: conjugate of the quaternion
        """
        return Quaternion(self._q[0], -self._q[1], -self._q[2], -self._q[3])

    def to_angle_axis(self):
        """
        Returns the quaternion's 3D rotation in an axis-angle representation.

        If the quaternion is the identity quaternion (1, 0, 0, 0), a rotation along the x-axis with angle 0 is returned.

        :return: rad, x, y, z --> where rad is the magnitude of rotation around the rotation axis, and x,y,z represent
                the rotation axis' direction vector.
        """
        if self[0] == 1 and self[1] == 0 and self[2] == 0 and self[3] == 0:
            return 0, 1, 0, 0
        rad = np.arccos(self[0]) * 2
        imaginary_factor = np.sin(rad / 2)
        if abs(imaginary_factor) < 1e-8:
            return 0, 1, 0, 0
        x = self._q[1] / imaginary_factor
        y = self._q[2] / imaginary_factor
        z = self._q[3] / imaginary_factor
        return rad, x, y, z

    @staticmethod
    def from_angle_axis(rad, x, y, z):
        """
        Returns the quaternion given the axis-angle representation.

        :param float rad: Magnitude of rotation about the rotation axis, in radians.
        :param float x: x-component of the rotation axis' direction vector.
        :param float y: y-component of the rotation axis' direction vector.
        :param float z: z-component of the rotation axis' direction vector.
        :return: quaternion
        """
        s = np.sin(rad / 2)
        return Quaternion(np.cos(rad / 2), x*s, y*s, z*s)

    def to_euler(self):
        """
        Convert the quaternion into euler angles (roll, pitch, yaw).

        Roll is rotation around x in radians (counterclockwise),
        pitch is rotation around y in radians (counterclockwise), and
        yaw is rotation around z in radians (counterclockwise)

        :return: roll, pitch, yaw
        """
        w, x, y, z = self._q[0], self._q[1], self._q[2], self._q[3]

        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)

        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2) * 2

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)

        return roll_x, pitch_y, yaw_z  # in radians

    # ---------------- Quaternion operations ----------------
    def __mul__(self, other):
        """
        Multiply the given quaternion with another quaternion or a scalar

        :param other: Quaternion object or number.
        :return: Resultant Quaternion from the operation.
        """
        if isinstance(other, Quaternion):
            w = self._q[0]*other._q[0] - self._q[1]*other._q[1] - self._q[2]*other._q[2] - self._q[3]*other._q[3]
            x = self._q[0]*other._q[1] + self._q[1]*other._q[0] + self._q[2]*other._q[3] - self._q[3]*other._q[2]
            y = self._q[0]*other._q[2] - self._q[1]*other._q[3] + self._q[2]*other._q[0] + self._q[3]*other._q[1]
            z = self._q[0]*other._q[3] + self._q[1]*other._q[2] - self._q[2]*other._q[1] + self._q[3]*other._q[0]

            return Quaternion(w, x, y, z)
        elif isinstance(other, numbers.Number):
            q = self._q * other
            return Quaternion(q)

    def __add__(self, other):
        """
        Add two quaternions element-wise or add a scalar to each element of the quaternion.

        :param other: Quaternion object or number.
        :return: Resultant Quaternion from the operation.
        """
        if not isinstance(other, Quaternion):
            if len(other) != 4:
                raise TypeError("Quaternions must be added to other quaternions or a 4-element array")
            q = self.q + other
        else:
            q = self.q + other.q

        return Quaternion(q)

    # ---------------- Implementing other interfaces to ease working with the class ----------------
    def _set_q(self, q):
        """
        Set quaternion values.

        :param q: New quaternion value, in ndarray format.
        """
        self._q = q

    def _get_q(self):
        """
        Return the current quaternion

        :return: current quaternion
        """
        return self._q

    q = property(_get_q, _set_q)

    def __getitem__(self, item):
        """
        Return specified quaternion component.

        :param item: key for quaternion item to be retrieved
        :return: quaternion item value
        """
        return self._q[item]

    def __array__(self):
        """
        Return a copy of the quaternion ndarray.

        :return: quaternion
        """
        return self._q

    def tolist(self):
        """
        Convert and return quaternion as a list.

        :return: quaternion as list
        """
        return self._q.tolist()

