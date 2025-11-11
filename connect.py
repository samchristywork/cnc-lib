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

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def keyboard_mode(connection):
    print("Keyboard control mode")
    print("WASD: X/Y movement, QE: Z movement, ESC to exit")

    connection.write(b'G21\n')
    connection.readline()
    connection.write(b'G91\n')
    connection.readline()

    key_map = {
        'w': 'G1 Y1 F2000',
        's': 'G1 Y-1 F2000',
        'a': 'G1 X-1 F2000',
        'd': 'G1 X1 F2000',
        'q': 'G1 Z1 F2000',
        'e': 'G1 Z-1 F2000',
    }

    while True:
        ch = getch()

        if ch == '\x1b':
            print("\nExiting keyboard mode")
            break
        elif ch in key_map:
            connection.write((key_map[ch] + '\n').encode())
            connection.readline()
            connection.reset_input_buffer()
            connection.write(b'?')
            time.sleep(0.1)
            while connection.in_waiting > 0:
                response = connection.readline().decode().strip()
                if response and response != 'ok':
                    print(response)
