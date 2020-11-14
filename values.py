#!/usr/bin/python
# coding: utf-8


import serial
import time
from energomera import *


# Send command to the counter and return decoded data
def get_data(cmd):
    buf = ''
    uart.write(data_encode({'head': 'R1', 'body': cmd}))
    time.sleep(0.5)
    while uart.inWaiting():
        buf += uart.readline()
    return data_decode(buf)


## Main

port = "/dev/ttyAMA0"
baudrate = 9600
bytesize = serial.SEVENBITS
parity = serial.PARITY_EVEN
stopbits = serial.STOPBITS_ONE
rtscts = False
xonxoff = False
read_flag = 1

uart = serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, rtscts=rtscts, xonxoff=xonxoff, timeout=1)

if uart.isOpen():
    uart.write("/?!\r\n")
    ident = uart.readline()
    print '>> ' + '\x060' + ident[4] + str(read_flag) + '\r\n'
    uart.write('\x060' + ident[4] + str(read_flag) + '\r\n')
    message = data_decode(uart.readline())
    print '>> INIT()\n' + message['body']
    message.clear()

    # Counter's identity
    message = get_data('IDENT()')
    print '>> IDENT()\n' + message['body']

    # The counter's model number CE30x
    message = get_data('MODEL()')
    print '>> MODEL()\n' + message['body']

    # Serial number
    message = get_data('SNUMB()')
    print '>> SNUMB()\n' + message['body']

    # Current date (wd.dd.mm.yy)
    message = get_data('DATE_()')
    print '>> DATE_()\n' + message['body']

    # Current time (HH:MM:SS)
    message = get_data('TIME_()')
    print '>> TIME_()\n' + message['body']

    # Summer time (0 - enabled, 1 - disabled)
    message = get_data('TRSUM()')
    print '>> TRSUM()\n' + message['body']

    # Relay status (0 -- relay is absent)
    message = get_data('STAT_()')
    print '>> STAT_()\n' + message['body']

    # Battery voltage,  V
    message = get_data('V_BAT()')
    print '>> V_BAT()\n' + message['body']

    # Current status of the Counter's Phases (??)
    message = get_data('CPHAS()')
    print '>> CPHAS()\n' + message['body']

    # Current phase deviation of voltages (0 - deviations is absent)
    message = get_data('COVER()')
    print '>> COVER()\n' + message['body']

    # Tariff start time tables
    message = get_data('GRF00()')
    print '>> GRF00()\n' + message['body']

    # Current counter's values by tariff
    message = get_data('ET0PE()')
    print '>> ET0PE()\n' + message['body']

    ### Values
    # Voltage, В (first – phase A; second – phase B; third – phase C)
    message = get_data('VOLTA()')
    print '>> VOLTA()\n' + message['body']

    # Current, A
    message = get_data('CURRE()')
    print '>> CURRE()\n' + message['body']

    # Frequency, Hz
    message = get_data('FREQU()')
    print '>> FREQU()\n' + message['body']

    # Total active power, kW
    message = get_data('POWEP()')
    print '>> POWEP()\n' + message['body']

    # Total active power per phase, kW
    message = get_data('POWPP()')
    print '>> POWPP()\n' + message['body']

    # Phases angle A&B, B&C, C&A, degrees
    message = get_data('CORUU()')
    print '>> CORUU()\n' + message['body']

    # Angle (current and voltage), degrees
    message = get_data('CORIU()')
    print '>> CORIU()\n' + message['body']

    uart.write(data_encode({'head':'B0', 'body':''}))
