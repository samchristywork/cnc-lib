#!/usr/bin/env python3

import serial
import time

def connect_to_cnc(port='/dev/ttyUSB0', baudrate=115200, timeout=2):
    try:
        connection = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )
        time.sleep(0.5)
        if connection.is_open:
            return True, connection
        else:
            return False, None
    except:
        return False, None
