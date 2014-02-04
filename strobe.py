#!/usr/bin/python

import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)

for x in xrange(1,10):
	GPIO.output(7,GPIO.HIGH)
	sleep(.1)
	GPIO.output(7,GPIO.LOW)
	sleep(.1)

GPIO.cleanup()
