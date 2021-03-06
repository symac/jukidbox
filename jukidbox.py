#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, sys
import pygame
from screenControl 	import screenControl
from databaseControl 	import databaseControl
from configLoader import config

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

	config = None
	pinNextAlbum = None
	pinPreviousAlbum = None
	pinNextTrack = None
	pinPreviousTrack = None

	idCurrentAlbumDisplayed = None

	ACTIVE_PROCESS = None

	def __init__(self):
		self.logger = logger()
		self.logger.msg("Init")

		self.config = config()

		self.pinNextAlbum = self.config.param('button', 'NextAlbum')
		self.pinPreviousAlbum = self.config.param('button', 'PreviousAlbum')
		self.pinNextTrack = self.config.param('button', 'NextTrack')
		self.pinPreviousTrack = self.config.param('button', 'PreviousTrack')

		self.prepareGpio()

		self.sc = screenControl(self.logger)
		self.sc.setActive(True)
		self.sc.prepareScreen()

		self.db = databaseControl(self.logger, MP3_FOLDER, self.sc)

		self.player = player()


	def prepareGpio(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pinNextAlbum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.pinPreviousAlbum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.pinNextTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.pinPreviousTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		GPIO.add_event_detect(self.pinNextAlbum, GPIO.RISING, callback=self.manageButtons, bouncetime=500)
		GPIO.add_event_detect(self.pinPreviousAlbum, GPIO.RISING, callback=self.manageButtons, bouncetime=500)
		GPIO.add_event_detect(self.pinNextTrack, GPIO.RISING, callback=self.manageButtons, bouncetime=1000)
		GPIO.add_event_detect(self.pinPreviousTrack, GPIO.RISING, callback=self.manageButtons, bouncetime=1000)

	def start(self):
		self.playSong()

		running = True
		counter = 0
		# try:
		while (running):
			if self.sc.checkQuit():
				running = False
				self.player.stopSong()


			time.sleep(0.1)

			if counter == 10:
				counter = 0
				if self.buttonManager == 1:
					self.logger.msg("Currenly managing buttons")
				else:
					if not self.player.isPlaying():
						self.db.getNextTrack()
						self.playSong()
			counter += 1
		# except Exception, e:
		# 	self.logger("ERREUR found : %s" % e)
		# 	self.player.stopSong()
		# 	pygame.quit()

	def updateDisplayInformation(self):
		self.logger.msg("FN::UpdateCover %s - %s" % (self.idCurrentAlbumDisplayed, self.db.getIdCurrentAlbum()))
		if self.idCurrentAlbumDisplayed != self.db.getIdCurrentAlbum():
			self.logger.msg("Loading album %s" % self.db.getIdCurrentAlbum())
			coverInfo = self.db.getCoverInfo()
			self.sc.updateCoverWithFile(coverInfo[0], coverInfo[1], coverInfo[2])
			self.idCurrentAlbumDisplayed = self.db.getIdCurrentAlbum()
		self.sc.updateSongDescription(self.db.currentTrackNumber, self.db.currentTrackTitle)

	def playSong(self):
		self.player.playSong(self.db.getCurrentSongPath())
		self.updateDisplayInformation()
		self.db.updatePidFile()

	buttonManager = 0

	def manageButtons(self, pinNumber):
		self.logger.msg("MANAGE BUTTON :: %s" % pinNumber)
		if self.buttonManager == 1:
			self.logger.msg("Already managing buttons")
		else:
			self.buttonManager = 1
			if pinNumber == self.pinNextAlbum:
				self.db.getNextAlbum()
				self.playSong()
			elif pinNumber == self.pinPreviousAlbum:
				self.db.getNextAlbum(False)
				self.playSong()
			elif pinNumber == self.pinNextTrack:
				self.logger.msg("MB 1 %s" % self.buttonManager)
				self.db.getNextTrack()
				self.logger.msg("MB 2 %s" % self.buttonManager)
				self.playSong()
				self.logger.msg("MB 3 %s" % self.buttonManager)
			elif pinNumber == self.pinPreviousTrack:
				self.db.getNextTrack(False)
				self.playSong()
		self.buttonManager = 0

jk = jukidbox()
jk.start()