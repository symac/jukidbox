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

	pinNextAlbum = 26
	pinPreviousAlbum = 6
	pinNextTrack = 19
	pinPreviousTrack = 13

	idCurrentAlbumDisplayed = None

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
		GPIO.setup(self.pinPreviousAlbum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.pinNextTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.pinPreviousTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		GPIO.add_event_detect(self.pinNextAlbum, GPIO.RISING, callback=self.manageButtons, bouncetime=700)
		GPIO.add_event_detect(self.pinPreviousAlbum, GPIO.RISING, callback=self.manageButtons, bouncetime=700)
		GPIO.add_event_detect(self.pinNextTrack, GPIO.RISING, callback=self.manageButtons, bouncetime=700)
		GPIO.add_event_detect(self.pinPreviousTrack, GPIO.RISING, callback=self.manageButtons, bouncetime=700)

	def start(self):
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
				if not self.player.isPlaying():
					self.db.getNextTrack()
					self.playSong()
			counter += 1
		# except Exception, e:
		# 	self.logger("ERREUR found : %s" % e)
		# 	self.player.stopSong()
		# 	pygame.quit()

	def updateCover(self):
		if self.idCurrentAlbumDisplayed != self.db.getIdCurrentAlbum():
			self.logger.msg("Loading album %s" % self.db.getIdCurrentAlbum())
			coverPath = self.db.getCoverPath()
			self.sc.updateCoverWithFile(coverPath)
			self.idCurrentAlbumDisplayed = self.db.getIdCurrentAlbum()

	def playSong(self):
		self.player.playSong(self.db.getCurrentSongPath())
		self.sc.updateSongDescription(self.db.currentTrackNumber, self.db.currentTrackTitle)
		self.db.updatePidFile()

	def manageButtons(self, pinNumber):
		if pinNumber == self.pinNextAlbum:
			self.db.getNextAlbum()
			self.playSong()
		elif pinNumber == self.pinPreviousAlbum:
			self.db.getNextAlbum(False)
			self.playSong()
		elif pinNumber == self.pinNextTrack:
			self.db.getNextTrack()
			self.playSong()
		elif pinNumber == self.pinPreviousTrack:
			print "PREVIOUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUs"
			self.db.getNextTrack(False)
			self.playSong()

		self.updateCover()

jk = jukidbox()
jk.start()

if __name__ == '__main__':
    main()
