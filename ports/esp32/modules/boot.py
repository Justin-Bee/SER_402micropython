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


def adv_encode(adv_type, value):
    return bytes((len(value) + 1, adv_type,)) + value


def adv_encode_name(name):
    return adv_encode(const(0x09), name.encode())


# sest the UUID for our device
#0x1825 is the SIG service for Object Transfer Service
#_adv_service = ubluetooth.UUID(0x1825)

#start the gatt service
#bt.gatts_register_services(_adv_service, ubluetooth.FLAG_WRITE)

#cannot advertise until after registering services
# set gap_advertise(interval, adv_data?)
bt.gap_advertise(100000, adv_encode_name('MicroTrynkit'))  #works correctly

#gatt s_registerservice()

#ubluetooth.UUID() 16 bit or 128 bit

# building now with ESP-IDF 3.3.1 has support for BLE and WiFi
# this could be a better option going forward incase BLE does not work out with the upload time
