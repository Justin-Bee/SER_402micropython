###########################################################################
#
# boot.py
# Author: Justin Bee
# Date: 1/24/2020
#
# This script will run at startup and will initialize the bluetooth module
# also sets the bluetooth to advertise
#
###########################################################################

import ubluetooth
from ubluetooth import BLE

from micropython import const
import struct

# Advertising payloads are repeated packets of the following form:
#   1 byte data length (N + 1)
#   1 byte type (see constants below)
#   N bytes type-specific data

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_UUID16_MORE = const(0x2)
_ADV_TYPE_UUID32_MORE = const(0x4)
_ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)


# create BLE variable
bt= BLE()

# set active to True initializing the bluetooth module
bt.active(1)

# Generate a payload to be passed to gap_advertise(adv_data=...).
def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack('BB', len(value) + 1, adv_type) + value

    _append(_ADV_TYPE_FLAGS, struct.pack('B', (0x01 if limited_disc else 0x02) + (0x00 if br_edr else 0x04)))

    if name:
        _append(_ADV_TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)

    # See org.bluetooth.characteristic.gap.appearance.xml
    _append(_ADV_TYPE_APPEARANCE, struct.pack('<h', appearance))

    return payload

payload = advertising_payload(name='MicroTrynkit', services=[ubluetooth.UUID(0x181A), ubluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')])

print(payload)
# set gap_advertise(interval, adv_data?)
bt.gap_advertise(100000, 'MicroTrynkit') #need to figure out why its not displaying

# building now with ESP-IDF 3.3.1 has support for BLE and WiFi
# this could be a better option going forward incase BLE does not work out with the upload time
