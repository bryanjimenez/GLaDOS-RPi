#!/usr/bin/python

import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)


GPIO.output(7,GPIO.HIGH)
sleep(.25)
GPIO.output(7,GPIO.LOW)


GPIO.cleanup()
