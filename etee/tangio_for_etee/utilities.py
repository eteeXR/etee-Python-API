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
Utility methods to retrieve COM port data and perform parsing/decoding.

"""

from serial.tools import list_ports


# ------------------------- COM Ports -------------------------
def get_ports(predicate=None):
    """
    Returns list available COM ports and their information.

    :param function predicate: predicate filtering criteria for ports.
    :return: list of available COM ports meeting the filtering criteria
    """
    if predicate is None:
        predicate = lambda x: True
    infos = list(filter(predicate, list_ports.comports()))
    ports = [(info.device, info.vid) for info in infos]
    return ports


def _get_port_info_predicate(vid, pid):
    """
    Filter available COM ports by VID and/or PID

    :param int vid: device VID to filter.
    :param int pid: device PID to filter.

    :return: true if a port fits the VID and/or PID criteria.
    """
    if isinstance(vid, list):
        return lambda port_info: port_info.vid in vid
    elif isinstance(pid, list):
        return lambda port_info: port_info.pid in pid
    elif vid is not None and pid is not None:
        return lambda port_info: port_info.vid == vid and port_info.pid == pid
    elif vid is not None:
        return lambda port_info: port_info.vid == vid
    elif pid is not None:
        return lambda port_info: port_info == pid
    else:
        return None


def serial_ports(vid=None, pid=None):
    """
    Returns the available serial ports.
    If VID and/or PID values are passed, the method will filter out COM ports that do not meet the VID and/or PID criteria.

    :param int vid: Device VID to filter. By default, it is None.
    :param int pid: Device PID to filter. By default, it is None.
    :return: List of available COM ports after VID/PID filtering.
    """
    return get_ports(_get_port_info_predicate(vid, pid))


# ------------------------- Parse Bytestring -------------------------
def parse_utf8(bytestring):
    """
    Decodes and parses a given bytestring.

    :param byte bytestring: bytestring to be parsed
    :return: parsed data as string
    """
    parsed = b""
    for i, byta in enumerate(bytestring):
        if byta < 0x80:
            parsed += bytestring[i:i + 1]
    return parsed.decode()
