#!/usr/bin/python2
# coding: utf-8

import time
import string
import re
import serial
import influxdb
from energomera import *

db = influxdb.InfluxDBClient(host="localhost",
                             port=8086,
                             username="homer",
                             password="asshole",
                             database="home")
# db = influxdb.InfluxDBClient(host="192.168.3.124",
#                              port=8086,
#                              database="test")


# Send command to the counter and return decoded data
def get_data(cmd):
    buf = ''
    uart.write(data_encode({'head': 'R1', 'body': cmd}))
    time.sleep(0.5)
    while uart.inWaiting():
        buf += uart.readline()
    return data_decode(buf)


def init_session():
    read_flag = 1
    uart.write("/?!\r\n")
    ident = uart.readline()
    uart.write('\x060' + ident[4] + str(read_flag) + '\r\n')
    message = data_decode(uart.readline())
    message.clear()
    return


def finish_session():
    uart.write(data_encode({'head': 'B0', 'body': ''}))
    return


port = "/dev/ttyAMA0"
baudrate = 9600
bytesize = serial.SEVENBITS
parity = serial.PARITY_EVEN
stopbits = serial.STOPBITS_ONE
rtscts = False
xonxoff = False

uart = serial.Serial(port,
                     baudrate,
                     bytesize=bytesize,
                     parity=parity,
                     stopbits=stopbits,
                     rtscts=rtscts,
                     xonxoff=xonxoff,
                     timeout=0.3)

if uart.isOpen():
    init_session()

    # Current values by tariff
    message = get_data('ET0PE()')
    parts = string.split(message['body'], '\r\n')
    tarif0 = float(re.match(r"ET0PE\((.*)\)", parts[0]).group(1))
    tarif1 = float(re.match(r"ET0PE\((.*)\)", parts[1]).group(1))
    tarif2 = float(re.match(r"ET0PE\((.*)\)", parts[2]).group(1))

    # Current values
    message = get_data('VOLTA()')
    parts = string.split(message['body'], '\r\n')
    phase1v = float(re.match(r"VOLTA\((.*)\)", parts[0]).group(1))
    phase2v = float(re.match(r"VOLTA\((.*)\)", parts[1]).group(1))
    phase3v = float(re.match(r"VOLTA\((.*)\)", parts[2]).group(1))

    message = get_data('CURRE()')
    parts = string.split(message['body'], '\r\n')
    phase1a = float(re.match(r"CURRE\((.*)\)", parts[0]).group(1))
    phase2a = float(re.match(r"CURRE\((.*)\)", parts[1]).group(1))
    phase3a = float(re.match(r"CURRE\((.*)\)", parts[2]).group(1))

    message = get_data('FREQU()')
    parts = string.split(message['body'], '\r\n')
    freq = float(re.match(r"FREQU\((.*)\)", parts[0]).group(1))

    message = get_data('POWEP()')
    parts = string.split(message['body'], '\r\n')
    power = float(re.match(r"POWEP\((.*)\)", parts[0]).group(1))

    message = get_data('POWPP()')
    parts = string.split(message['body'], '\r\n')
    phase1p = float(re.match(r"POWPP\((.*)\)", parts[0]).group(1))
    phase2p = float(re.match(r"POWPP\((.*)\)", parts[1]).group(1))
    phase3p = float(re.match(r"POWPP\((.*)\)", parts[2]).group(1))

    json_body = [{
        "measurement": "electricity",
        "fields": {
            "tarif0": tarif0,
            "tarif1": tarif1,
            "tarif2": tarif2,
            "phase1v": phase1v,
            "phase2v": phase2v,
            "phase3v": phase3v,
            "phase1a": phase1a,
            "phase2a": phase2a,
            "phase3a": phase3a,
            "phase1p": phase1p,
            "phase2p": phase2p,
            "phase3p": phase3p,
            "power": power,
            "freq": freq,
        }
    }
    ]
    db.write_points(json_body)

    finish_session()
