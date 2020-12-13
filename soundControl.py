#!/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain

import time, os
import RPi.GPIO as GPIO
import alsaaudio
import logging, sys
import math
from configLoader import config

logging.basicConfig(level=logging.INFO)



class soundController:
	# Default settings
	config = config()
	SPICLK = config.param('potentiometer', 'SPICLK')
	SPIMISO = config.param('potentiometer', 'SPIMISO')
	SPIMOSI = config.param('potentiometer', 'SPIMOSI')
	SPICS = config.param('potentiometer', 'SPICS')

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(SPIMOSI, GPIO.OUT)
	GPIO.setup(SPIMISO, GPIO.IN)
	GPIO.setup(SPICLK, GPIO.OUT)
	GPIO.setup(SPICS, GPIO.OUT)

	maxVolume = config.param('volume', 'max')

	m = None

	potentiometer_adc = 0 # 10k trim pot connected to adc #0

	last_read = 0       # this keeps track of the last potentiometer value

	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		self.m = alsaaudio.Mixer("Speaker", cardindex=0)

		GPIO.setup(self.SPIMOSI, GPIO.OUT)
		GPIO.setup(self.SPIMISO, GPIO.IN)
		GPIO.setup(self.SPICLK, GPIO.OUT)
		GPIO.setup(self.SPICS, GPIO.OUT)

	# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
	def readadc(self, adcnum, clockpin, mosipin, misopin, cspin):
		if ((adcnum > 7) or (adcnum < 0)):
			return -1
		GPIO.output(cspin, True)

		GPIO.output(clockpin, False) # start clock low
		GPIO.output(cspin, False)   # bring CS low

		commandout = adcnum
		commandout |= 0x18 # start bit + single-ended bit
		commandout <<= 3  # we only need to send 5 bits here
		for i in range(5):
			if (commandout & 0x80):
				GPIO.output(mosipin, True)
			else:
				GPIO.output(mosipin, False)
			commandout <<= 1
			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)

		adcout = 0
		# read in one empty bit, one null bit and 10 ADC bits
		for i in range(12):
			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)
			adcout <<= 1
			if (GPIO.input(misopin)):
				adcout |= 0x1

		GPIO.output(cspin, True)

		adcout >>= 1	# first bit is 'null' so drop it
		return adcout

	def getAbsoluteVolume(self, pct_volume):
		return (pct_volume * self.maxVolume / 100)

	def checkForUpdate(self):
		trim_pot_changed = False
		tolerance = 10       # to keep from being jittery we'll only volume when the pot has moved more than 5 'counts'

		# read the analog pin
		trim_pot = self.readadc(self.potentiometer_adc, self.SPICLK, self.SPIMOSI, self.SPIMISO, self.SPICS)
		# how much has it changed since the last read?
		pot_adjust = abs(trim_pot - self.last_read)

		if ( pot_adjust > tolerance ):
			trim_pot_changed = True

		if ( trim_pot_changed ):
			set_volume = trim_pot / 10.24           # convert 10bit adc0 (0-1024) trim pot read into 0-100 volume level
			set_volume = round(set_volume)          # round out decimal value
			set_volume_pct = int(set_volume)            # cast volume as integer

			set_volume_absolute = self.getAbsoluteVolume(set_volume_pct)
			self.m.setvolume(set_volume_absolute)
			logging.info("Volume passe a %s" % set_volume_absolute);
			# save the potentiometer reading for the next loop
			self.last_read = trim_pot

		# hang out and do nothing for a half second
		time.sleep(0.5)

	def stop(self):
		GPIO.cleanup()
		# We should remove detectHandler as soon as we use them
		return

s = soundController()
try:
	while True:
		s.checkForUpdate()
finally:
	s.stop()