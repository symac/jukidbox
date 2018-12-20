#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, sys
import pygame
from screenControl 	import screenControl
from databaseControl 	import databaseControl
from player import player
from logger import logger
import RPi.GPIO as GPIO
import time

logEnabled = False

MP3_FOLDER = "/media/usb/jukidbox"

class jukidbox:
	logger = None
	sc = None
	db = None
	player = None

	pinNextAlbum = 14
	pinNextTrack = 18
	pinPreviousTrack = 15


	ACTIVE_PROCESS = None

	def __init__(self):
		self.logger = logger()
		self.logger.msg("Init")

		self.db = databaseControl(self.logger, MP3_FOLDER)

		self.prepareGpio()

		self.sc = screenControl(self.logger)
		# self.sc.setActive(True)
		self.sc.prepareScreen()

		self.player = player()


	def prepareGpio(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pinNextAlbum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.pinNextTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.pinPreviousTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	def start(self):
		self.logger.msg("Démarrage")
		self.updateCover()
		self.playSong()

		running = True
		counter = 0
		# try:
		while (running):
			if self.sc.checkQuit():
				running = False

			time.sleep(0.1)

			if counter == 10:
				counter = 0
				self.logger("Counter vaut 10, on controle l'ACTIVEPROCESS")
				if not self.player.isPlaying():
					self.logger("Player not playing, on va changer de chanson")
					self.skipToNextTrack()
			counter += 1
		# except Exception, e:
		# 	self.logger("ERREUR found : %s" % e)
		# 	self.player.stopSong()
		# 	pygame.quit()

	def updateCover(self):
		self.logger.msg("Loading album %s" % self.db.getIdCurrentAlbum())
		coverPath = self.db.getCoverPath()
		self.sc.updateCoverWithFile(coverPath)

	def playSong(self):
		self.player.playSong(self.db.getCurrentSongPath())
		self.sc.updateSongDescription(self.db.currentTrackNumber, self.db.currentTrackTitle)
		self.db.updatePidFile()

	def skipToNextAlbum(self, channel = None):
		self.logger("FNC playNextAlbum")
		self.db.getNextAlbum()
		self.playSong()

	def skipToNextTrack(self, order = True):
		self.logger("FNC playNextTrack")
		self.db.getNextTrack(order)
		self.playSong()

jk = jukidbox()
jk.start()

sys.exit()

# We skip to next album, the returned value is the one of the first track of next album

#GPIO.add_event_detect(pinNextAlbum, GPIO.RISING, callback=playNextAlbum, bouncetime=700)
#GPIO.add_event_detect(pinNextTrack, GPIO.RISING, callback=playNextTrack, bouncetime=700)

def isKeyPressed(pinNumber):
	input_state = GPIO.input(pinNumber)
	if input_state == False:
		return True
	return False


# def main():
# 	We need to init the display
#
# 	We are going to have a look at the pid file
#
# 			We need to check that esc had not been pressed
# 			isPressedNextAlbum = isKeyPressed(pinNextAlbum)
# 			isPressedNextTrack = isKeyPressed(pinNextTrack)
# 			isPressedPreviousTrack = isKeyPressed(pinPreviousTrack)
# 			if isPressedNextTrack:
# 				playNextTrack()
# 			elif isPressedNextAlbum:
# 				playNextAlbum()
# 			elif isPressedPreviousTrack:
# 				playNextTrack(False)
#
#
#






if __name__ == '__main__':
    main()
