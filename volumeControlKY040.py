#KY040 Python Class
#Martin O'Hanlon
#stuffaboutcode.com

import RPi.GPIO as GPIO
from time import sleep
import alsaaudio

class KY040:

	CLOCKWISE = 0
	ANTICLOCKWISE = 1
	
	def __init__(self, clockPin, dataPin, switchPin, rotaryCallback, switchCallback):
		#persist values
		self.clockPin = clockPin
		self.dataPin = dataPin
		self.switchPin = switchPin
		self.rotaryCallback = rotaryCallback
		self.switchCallback = switchCallback

		#setup pins
		GPIO.setup(clockPin, GPIO.IN)
		GPIO.setup(dataPin, GPIO.IN)
		GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	def start(self):
		GPIO.add_event_detect(self.clockPin, GPIO.FALLING, callback=self._clockCallback, bouncetime=250)
		GPIO.add_event_detect(self.switchPin, GPIO.FALLING, callback=self._switchCallback, bouncetime=300)

	def stop(self):
		GPIO.remove_event_detect(self.clockPin)
		GPIO.remove_event_detect(self.switchPin)
	
	def _clockCallback(self, pin):
		if GPIO.input(self.clockPin) == 0:
			data = GPIO.input(self.dataPin)
			if data == 1:
				self.rotaryCallback(self.ANTICLOCKWISE)
			else:
				self.rotaryCallback(self.CLOCKWISE)

	def _switchCallback(self, pin):
		if GPIO.input(self.switchPin) == 0:
			self.switchCallback()

#test
if __name__ == "__main__":
	# Default settings
	volume = 60
	maxVolume = 95
	minVolume = 65
	stepVolume = 2

	CLOCKPIN = 18
	DATAPIN = 15
	SWITCHPIN = 14
	m = alsaaudio.Mixer("PCM")
	
	# We get the current volume
	volume = m.getvolume()[0]
	print "Volume at start : %s" % volume
	def rotaryChange(direction):
		global m, volume, minVolume, maxVolume
		print "turned - " + str(direction)
		if direction == 1:
			# On baisse le volume
			print "Decreasing sound"
			if volume <= minVolume:
				volume = minVolume
			else:
				volume = volume - stepVolume
		else:
			print "Increasing volume"
			if volume >= maxVolume:
				volume = maxVolume
			else:
				volume = volume + stepVolume

		print "Volume set to %s" % volume
		m.setvolume(volume)

	def switchPressed():
		print "button pressed"

	GPIO.setmode(GPIO.BCM)
	
	ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)

	ky040.start()

	try:
		while True:
			sleep(0.1)
	finally:
		ky040.stop()
		GPIO.cleanup()
