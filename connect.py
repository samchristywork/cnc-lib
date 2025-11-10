#!/usr/bin/env python3

import serial
import sys
import time
import tty
import termios

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

def send_gcode_file(connection, filename):
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                connection.write((line + '\n').encode())
                response = connection.readline().decode().strip()
                print(f"{line} -> {response}")
                time.sleep(0.1)

def send_gcode_line(connection, gcode):
    connection.write((gcode + '\n').encode())
    time.sleep(0.1)
    while connection.in_waiting > 0:
        response = connection.readline().decode().strip()
        if response:
            print(response)
