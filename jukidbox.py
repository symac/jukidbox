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
		self.play_song()


	def updateCover(self):
		self.logger.msg("Loading album %s" % self.db.getIdCurrentAlbum())
		coverPath = self.db.getCoverPath()
		self.sc.updateCoverWithFile(coverPath)

	# play a song based on the id
	def play_song(self):
		self.logger("play_song : %s / %s" % (self.db.getIdCurrentAlbum(), self.db.getIdCurrentTrack()))
		self.db.updatePidFile()

		self.player.play_song(self.db.getCurrentSongPath())


		self.sc.updateSongDescription(trackNumber, track)
		pass

jk = jukidbox()
jk.start()

sys.exit()

# We skip to next album, the returned value is the one of the first track of next album

def playNextAlbum(channel = None):
	myLog("FNC playNextAlbum")
	global idCurrentTrack
	idCurrentTrack = getNextAlbum()
	play_song(idCurrentTrack)

def playNextTrack(order = True):
	myLog("FNC playNextTrack")
	global idCurrentTrack
	idCurrentTrack = getNextTrack(order)
	play_song(idCurrentTrack)

#GPIO.add_event_detect(pinNextAlbum, GPIO.RISING, callback=playNextAlbum, bouncetime=700)
#GPIO.add_event_detect(pinNextTrack, GPIO.RISING, callback=playNextTrack, bouncetime=700)

def isKeyPressed(pinNumber):
	input_state = GPIO.input(pinNumber)
	if input_state == False:
		return True
	return False


def main():
	# We need to init the display

	# We are going to have a look at the pid file

	running = True
	counter = 0
	try:
		while (running):
			# We need to check that esc had not been pressed
			isPressedNextAlbum = isKeyPressed(pinNextAlbum)
			isPressedNextTrack = isKeyPressed(pinNextTrack)
			isPressedPreviousTrack = isKeyPressed(pinPreviousTrack)
			if isPressedNextTrack:
				playNextTrack()
			elif isPressedNextAlbum:
				playNextAlbum()
			elif isPressedPreviousTrack:
				playNextTrack(False)


			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					running = False
				elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
					running = False

			time.sleep(0.1)

			if counter == 10:
				counter = 0
				myLog("Counter vaut 10, on controle l'ACTIVEPROCESS")
				if ACTIVE_PROCESS.poll() != None:
					myLog("ACTIVE PROCESS vaut autre chose que None, mpg321 s'est donc terminé, on va changer de chanson")
					playNextTrack()
			counter += 1
	except Exception, e:
		myLog("ERREUR found : %s" % e)
	stop_song()
	pygame.quit()


if __name__ == '__main__':
    main()
