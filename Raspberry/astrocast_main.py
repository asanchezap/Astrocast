"""

File:               astrocasat_main.py
Author:             Amelia Sánchez
E-mail:             asanchez.beca@hispasat.es

Created on:         15.07.2022
Python Version:     3.8
Supported Hardware: Astronode S/S+/DevKit
Microprocessor:     Raspberry Pi 3

"""

# !/usr/bin/env python3
import binascii
import codecs
import crcmod
import serial
from binascii import hexlify
from random import *

import RPi.GPIO as GPIO
import time

from datetime import datetime
from datetime import timedelta

TimeReference = datetime(2018, 1, 1, 0, 0, 0)


# --------------------------------------------------------------------------------
# Initializations
# --------------------------------------------------------------------------------
# To match with your local serial port
#SerialPort = 'COMx'
SerialPort = '/dev/ttyUSB0';

ser = serial.Serial(
    port=SerialPort,
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=3,
    inter_byte_timeout=0.001
)

crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xffff, xorOut=0x0000)


# --------------------------------------------------------------------------------
# Operation codes
# --------------------------------------------------------------------------------
PLD_ER = "25"     # Enqueue payload
PLD_DR = "26"     # Dequeue payload
PLD_FR = "27"     # Free payloads of queue
GEO_WR = "35"     # Geolocalization write
CFG_WR = "05"     # Configuration write (in RAM)
WIF_WR = "06"     # WiFi configuration write (in RAM)
CFG_RR = "15"     # Configuration read
EVT_RR = "65"     # Read the event register
SAK_RR = "45"     # Read satellite ACK
SAK_CR = "46"     # Clear satellite ACK
RTC_RR = "17"	  # Real time clock read

PLD_EA = "A5"      # Enqueue payload
PLD_DA = "A6"      # Dequeue payload
PLD_FA = "A7"      # Free payloads of queue
GEO_WA = "B5"      # Geolocalization write
CFG_WA = "85"      # Configuration write (in RAM)
WIF_WA = "86"      # WiFi configuration write (in RAM)
CFG_RA = "95"      # Configuration read
EVT_RA = "E5"      # Read the event register
SAK_RA = "C5"      # Read satellite ACK
SAK_CA = "C6"      # Clear satellite ACK
RTC_RA = "97"	   # Real time clock read

ERROR  = "FF"     # Error


# --------------------------------------------------------------------------------
# Payload, Geolocation and Wi-Fi configuration
# Here you can declare you data.
# --------------------------------------------------------------------------------

payload = b"Msg automatico cada 2 min, Rasp inicia automaticamente, modulo WiFi"
latitude = 46.534363896181624
longitude = 6.578710272772917

ssid = b"MiFibra-DA72"
password = b"a3rSfZJQ"
#ssid = b"DIGIFIBRA-AS3x"
#password = b"95uUaTGsDX"
token = b"Zxi2MlfeW0TWHvVMBHaREFL3SV3wMI4OVNG0D35alT7qcDR6NJzwL1UtUok0qSAo4fb2X3iGL8FUHu1od6RciIc22ngpTfTC"

configuration_wifi = binascii.hexlify(ssid).ljust(66, b'0') + \
                     binascii.hexlify(password).ljust(128, b'0') + binascii.hexlify(token).ljust(194, b'0')
configuration_wifi = configuration_wifi.decode("utf-8")


# --------------------------------------------------------------------------------
# ´Decodification functions
# --------------------------------------------------------------------------------
def opCode(op):
    if op==PLD_ER: return "PLD_ER: Enqueue payload"
    elif op==PLD_DR: return "PLD_DR: Dequeue payload"
    elif op==PLD_FR: return "PLD_FR: Free payloads of queue"
    elif op==GEO_WR: return "GEO_WR: Geolocalization write"
    elif op==CFG_WR: return "CFG_WR: Configuration write (in RAM)"
    elif op==WIF_WR: return "WIF_WR: WiFi configuration write (in RAM)"
    elif op==CFG_RR: return "CFG_RR: Configuration read"
    elif op==EVT_RR: return "EVT_RR: Read the event register"
    elif op==SAK_RR: return "SAK_RR: Read satellite ACK"
    elif op==SAK_CR: return "SAK_CR: Clear satellite ACK"
    elif op==RTC_RR: return "RTC_RR: Real time clock read"

    elif op==PLD_EA: return "PLD_EA: Enqueue payload [ANSWER]"
    elif op==PLD_DA: return "PLD_DA: Dequeue payload [ANSWER]"
    elif op==PLD_FA: return "PLD_FA: Free payloads of queue [ANSWER]"
    elif op==GEO_WA: return "GEO_WA: Geolocalization write [ANSWER]"
    elif op==CFG_WA: return "CFG_WA: Configuration write (in RAM) [ANSWER]"
    elif op==WIF_WA: return "WIF_WA: WiFi configuration write (in RAM)  [ANSWER]"
    elif op==CFG_RA: return "CFG_RA: Configuration read [ANSWER]"
    elif op==EVT_RA: return "EVT_RA: Read the event register [ANSWER]"
    elif op==SAK_RA: return "SAK_RA: Read satellite ACK [ANSWER]"
    elif op==SAK_CA: return "SAK_CA: Clear satellite ACK  [ANSWER]"
    elif op==RTC_RA: return "RTC_RA: Real time clock read [ANSWER]"

    elif op==ERROR: return "ERROR"

    else: return "Operation code not known"

def decode(m):
    mm = ""
    i = 0
    while (i < len(m)):
        if m[i] == '3':
             mm += m[i+1]
        elif m[i] == '4' or m[i] == '6':
            if m[i+1] == '1': mm += 'A'
            elif m[i+1] == '2': mm += 'B'
            elif m[i+1] == '3': mm += 'C'
            elif m[i+1] == '4': mm += 'D'
            elif m[i+1] == '5': mm += 'E'
            elif m[i+1] == '6': mm += 'F'
        i += 3
    return mm

def big_endian(m):
    mm = ""
    i = 0
    while (i < len(m)):
        mm += m[-i-2]
        mm += m[-i-1]
        i += 2
    return mm

def hex_to_decimal(m):
    if len(m)>0:
        return str(int("0x"+m, 16))
    else:
        return ""

def dec_to_bin(decimal):
    if decimal <= 0:
        return "0"
    # Aquí almacenamos el resultado
    binario = ""
    # Mientras se pueda dividir...
    while decimal > 0:
        # Saber si es 1 o 0
        residuo = int(decimal % 2)
        # E ir dividiendo el decimal
        decimal = int(decimal / 2)
        # Ir agregando el número (1 o 0) a la izquierda del resultado
        binario = str(residuo) + binario
    return binario

def getInfo(m, op):
    mm = ""
    if op==RTC_RA:
        mm += "RTC Time: " + str(TimeReference + timedelta(seconds=int(hex_to_decimal(m))))
    elif op==EVT_RA:
        bin = str(dec_to_bin(int(hex_to_decimal(m))))
        mm += "EVENT: " + bin + " --> "
        if len(bin)>0 and bin[-1]=='1':      mm += "satellite payload acknowledgement + "
        if len(bin)>1 and bin[-2]=='1':      mm += "module has reset + "
        if len(bin)>2 and bin[-3]=='1':      mm += "command is available + "
        if len(bin)>3 and bin[-4]=='1':      mm += "uplink message is present in the message queue + "
        mm += ")"
    elif op==SAK_RA:
        mm += "ACK FROM PAYLOAD ID: " + hex_to_decimal(m)
    elif op==PLD_ER:
        mm += "ID: 0x" + m[-4] + m[-3] + m[-2] + m[-1]
    elif op==PLD_EA:
        mm += "PAYLOAD ID: 0x" + m
    return mm

def hasACK(msg):
    linea = " ".join(["{:02x}".format(x) for x in msg]) + "\n"
    op = linea[3:8]
    msg = linea[9:-16]
    bin = str(dec_to_bin(int(hex_to_decimal(big_endian(decode(msg))))))

    if (op==EVT_RA) and len(bin)>0 and bin[-1]=='1':
        return True

    return False

def printDecodedLog(msg):
    f = open('/home/muny/Desktop/Astrocast/Raspberry/log.txt', 'a')
    linea = " ".join(["{:02x}".format(x) for x in msg]) + "\n"
    op = linea[3:8]
    msg = linea[9:-16]
    msg_hex = big_endian(decode(msg))
    f.write(opCode(decode(op)) + "            " + getInfo(msg_hex, decode(op)) + "\n")
    f.close()

    print(opCode(decode(op)) + "            " + getInfo(msg_hex, decode(op)) + "\n")

# --------------------------------------------------------------------------------
# Function definitions
# --------------------------------------------------------------------------------

def generate_geolocation(lat, lng):
    lat_tmp = '{:08x}'.format(int(lat * 1e7) & (2**32-1))
    lng_tmp = '{:08x}'.format(int(lng * 1e7) & (2**32-1))
    geolocation = lat_tmp[6]
    geolocation += lat_tmp[7]
    geolocation += lat_tmp[4]
    geolocation += lat_tmp[5]
    geolocation += lat_tmp[2]
    geolocation += lat_tmp[3]
    geolocation += lat_tmp[0]
    geolocation += lat_tmp[1]
    geolocation += lng_tmp[6]
    geolocation += lng_tmp[7]
    geolocation += lng_tmp[4]
    geolocation += lng_tmp[5]
    geolocation += lng_tmp[2]
    geolocation += lng_tmp[3]
    geolocation += lng_tmp[0]
    geolocation += lng_tmp[1]
    return geolocation


def generate_crc(data):
    crc_tmp = '{:04x}'.format(crc16(codecs.decode(data, 'hex')))
    crc = crc_tmp[2]
    crc += crc_tmp[3]
    crc += crc_tmp[0]
    crc += crc_tmp[1]
    return crc


def send(opcode, data):
    msg = opcode
    msg += data
    crc = generate_crc(msg)
    msg += crc
    msg = hexlify(msg.encode())
    msg = "02" + msg.decode()
    msg += "03"
    msg = bytearray.fromhex(msg)
    ser.write(msg)

    printDecodedLog(msg)
    receive()


def receive():
    output = ser.read(160)
    printDecodedLog(output)


def text_to_hex(text):
    return binascii.hexlify(text).decode('ascii')


def generate_message(payload):
    return str(randint(0, 9999)) + text_to_hex(payload)

def check_ACK():
    msg = EVT_RR
    crc = generate_crc(msg)
    msg += crc
    msg = hexlify(msg.encode())
    msg = "02" + msg.decode()
    msg += "03"
    msg = bytearray.fromhex(msg)
    ser.write(msg)

    output = ser.read(160)
    printDecodedLog(output)

    if (hasACK(output)):
        send(EVT_RR, "")
        send(RTC_RR, "")
        send(SAK_RR, "")
        send(SAK_CR, "")

        check_ACK()


# --------------------------------------------------------------------------------
# Send and receive on UART
#
# Here you can call the send function with the command and data you want.
# Use the send(OPCODE, SUB-OPCODE, DATA) function.
# OPCODE is one of the terminal<->asset protocol command (PLD_WR, CFG_RD...) or
# it can be DEBUG to send command like setting the RTC date and time.
# SUB-OPCODE is needed only for the DEBUG operation code.
# DATA is the data related to the operation code and sub-operation code you use.
# --------------------------------------------------------------------------------


# If using the Astronode S DevKit Wi-Fi (comment if using Satellite board)
# send(WIF_WR, configuration_wifi)

# If you want to specify geolocation (comment if not)
# send(GEO_WR, generate_geolocation(latitude, longitude))

# send(PLD_ER, generate_message(payload))

GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN)

while True:
	if GPIO.input(3):
		payload = b"Msg auto cada 1,5h, Raspberry inicia auto, SensorLuz: 1 Noche"
	else:
		payload = b"Msg auto cada 1,5h, Raspberry inicia auto, SensorLuz: 0 Dia"

	send(WIF_WR, configuration_wifi)
	send(PLD_ER, generate_message(payload))

    for(i in 1:5):
	   time.sleep(1*1*60)
       check_ACK();
