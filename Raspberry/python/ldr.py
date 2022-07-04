#!/usr/bin/python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN)

while True:
	if GPIO.input(3):
		print("1: Noche")
	else:
		print("0: Dia")
	time.sleep(2)
