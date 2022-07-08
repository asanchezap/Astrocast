"""

File:               decodificador.py
Author:             Amelia Sánchez

Inputs:             Fichero "log_ack.txt" una cadena de bytes en hexadecimal por línea
Output:             Fichero "output.txt" con la decodificación de cada cadena
"""

# !/usr/bin/env python3
from datetime import datetime
from datetime import timedelta

TimeReference = datetime(2018, 1, 1, 0, 0, 0)


# --------------------------------------------------------------------------------
# Operation codes
# --------------------------------------------------------------------------------

# main family
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
# Funciones
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




# --------------------------------------------------------------------------------
# Programa principal
# --------------------------------------------------------------------------------

input = open('log.txt', 'r')
output = open('output_extended.txt', 'w')
output2 = open('output.txt', 'w')

try:
    for linea in input:
        op = linea[3:8]
        msg = linea[9:-16]
        msg_hex = big_endian(decode(msg))

        output.write(linea)
        output.write(op + " > " + decode(op) + " > " + opCode(decode(op)) + "\n")
        output.write(msg + " > " + decode(msg) + " > 0x" + msg_hex + " or dec" + hex_to_decimal(msg_hex) + " > " + getInfo(msg_hex, decode(op)) + "\n\n")

        output2.write(opCode(decode(op)) + "            " + getInfo(msg_hex, decode(op)) + "\n")
finally:
    input.close()
    output.close()
    output2.close()
