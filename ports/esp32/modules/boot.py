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

# create BLE variable
bt= BLE()

# set active to True initializing the bluetooth module
bt.active(1)

# set gap_advertise(interval, adv_data?)
bt.gap_advertise(100000, "MicroTrynkit") #need to figure out why its not displaying