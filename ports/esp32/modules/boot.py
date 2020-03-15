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
import machine
import time
import os

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

# These are constants for the BLE IRQ
_IRQ_ALL = const(0xffff)
_IRQ_CENTRAL_CONNECT                 = const(1 << 0)
_IRQ_CENTRAL_DISCONNECT              = const(1 << 1)
_IRQ_GATTS_WRITE                     = const(1 << 2)
_IRQ_GATTS_READ_REQUEST              = const(1 << 3)
_IRQ_SCAN_RESULT                     = const(1 << 4)
_IRQ_SCAN_COMPLETE                   = const(1 << 5)
_IRQ_PERIPHERAL_CONNECT              = const(1 << 6)
_IRQ_PERIPHERAL_DISCONNECT           = const(1 << 7)
_IRQ_GATTC_SERVICE_RESULT            = const(1 << 8)
_IRQ_GATTC_CHARACTERISTIC_RESULT     = const(1 << 9)
_IRQ_GATTC_DESCRIPTOR_RESULT         = const(1 << 10)
_IRQ_GATTC_READ_RESULT               = const(1 << 11)
_IRQ_GATTC_WRITE_STATUS              = const(1 << 12)
_IRQ_GATTC_NOTIFY                    = const(1 << 13)
_IRQ_GATTC_INDICATE                  = const(1 << 14)

#Global functions for the timer
time_after = time.time()
time_before = time.time()
timeCheck = False

# create BLE variable
bt= BLE()

# set active to True initializing the bluetooth module
bt.active(1)

#define the bt_irq
def bt_irq(event, data):
    global timeCheck
    if event == _IRQ_CENTRAL_CONNECT:
        print("IRQ_CENTRAL_CONNECT")
    elif event == _IRQ_CENTRAL_DISCONNECT:
        print("IRQ_CENTRAL_DISCONNECT")
        stop_timer()
        timeCheck = False
        #for testing purposes I had to remove the reset to connect with nrfConnect sniffer app
       # machine.reset()
    elif event == _IRQ_GATTS_WRITE:
        print("IRQ_GATTS_WRITE")
        timer()
        x = bt.gatts_read(rx_handle)
        temp = x.decode('utf-8')
        if(temp == 'erase'):
            os.remove('main.py')
        else:
            # add newline char to end of the line that was sent
            x = x + '\n'
            # create a new file or append to existing
            f = open('main.py', 'a')
            #write to the file
            f.write(x)
            #close the file
            f.close()
        tx_handle = 'Upload finished'
    elif event == _IRQ_GATTS_READ_REQUEST:
        print("IRQ_GATTS_READ_REQUEST")
        tx_handle = "Test"


bt.irq(bt_irq)

# timer() - this function gets the time at the beginning of the upload
def timer():
    global time_before
    global timeCheck
    if(timeCheck == False):
        timeCheck = True
        time_before = time.time()

# stop_timer() - this function gets the time at the end of the upload
def stop_timer():
    global time_before
    global time_after
    time_after = time.time()
    print("Upload completed in " +str(time_after - time_before)+ " seconds.")


#encode the advertise type and the value passed.
def adv_encode(adv_type, value):
    return bytes((len(value) + 1, adv_type,)) + value

#helper function to encode the advertising name passed
def adv_encode_name(name):
    return adv_encode(_ADV_TYPE_NAME, name.encode())

# set the UUID for the GATT Service
_adv_service = ubluetooth.UUID(0x1825)

#UUID for the TX characteristic - 30ff6dae-fbfe-453b-8a99-9688fea23832
#UUID created by https://www.uuidgenerator.net/version4
#set the ubluetooth flag for read
_adv_TX_service = (ubluetooth.UUID('30ff6dae-fbfe-453b-8a99-9688fea23832'), ubluetooth.FLAG_READ,)

#UUID for the RX characteristic - fbdf3e86-c18c-4e5b-aace-e7cc03257f7c
#UUID created by https://www.uuidgenerator.net/version4
#set the ubluetooth flag for write
_adv_RX_service = (ubluetooth.UUID('fbdf3e86-c18c-4e5b-aace-e7cc03257f7c'), ubluetooth.FLAG_WRITE,)

# MicroTrynkit Service
#including the TX and RX characteristics created above.
_my_service = ((_adv_service, (_adv_TX_service, _adv_RX_service,),),)

#start the gatt service
# tx_handle is for the TX service to be used for the reads
((tx_handle, rx_handle),)= bt.gatts_register_services(_my_service)

#new service for the serial communication
# User Data service 0x181C
_serial_service = ubluetooth.UUID(0x181C)
_serial_TX_service = (ubluetooth.UUID('f05d9919-02e3-4414-9cbc-5485e0af77d2'), ubluetooth.FLAG_READ,)
_serial_RX_service = (ubluetooth.UUID('72f235e0-fb1c-4772-96f1-d55a445d5c89'), ubluetooth.FLAG_WRITE,)

_my_serial_service = ((_serial_service,(_serial_TX_service, _serial_RX_service,),),)
((tx_handle, rx_handle),)= bt.gatts_register_services(_my_serial_service)

# increase the size of the buffer, default is 20 bytes
#need to ensure we pick something that is big enough for file transfers
bt.gatts_write(rx_handle, bytes(1024))

#gap_advertise()
#params: interval, adv_data
bt.gap_advertise(100000, adv_encode_name('MicroTrynkit'))


#this function sends to data from esp32 to be read from connected device. Just for testing purposes now.
bt.gatts_write(tx_handle, str.encode("hopefully this works"))

#ubluetooth.UUID() 16 bit or 128 bit

# building now with ESP-IDF 3.3.1 has support for BLE and WiFi
# this could be a better option going forward incase BLE does not work out with the upload time

#END OF FILE
########################################################################################################################

