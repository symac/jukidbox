#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, sys
import pygame
from screenControl 	import screenControl
from databaseControl 	import databaseControl
from logger import logger
import RPi.GPIO as GPIO
import time

logEnabled = False

MP3_FOLDER = "/media/usb/jukidbox"

class jukidbox:
	logger = None
	sc = None
	db = None

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


	def prepareGpio(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pinNextAlbum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.pinNextTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.pinPreviousTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	def start(self):
		self.logger.msg("Démarrage")
		self.updateCover()
		self.play_song()

	# get the next song to play. By default the next one, if order is set to -1, the previous one

	def updateCover(self):
		self.logger.msg("Loading album %s" % self.getIdCurrentAlbum())
		coverPath = self.db.getCoverPath()
		self.sc.updateCoverWithFile(coverPath)			

	# play a song based on the id
	def play_song(self):
		self.logger("play_song : %s / %s" % (self.getIdCurrentAlbum(), self.idCurrentTrack))

		self.updatePidFile()
		# On va stocker les infos sur la chanson en cours

		# We first need to stop the current player before reloading it
		self.cursor.execute('SELECT album.directory, track.filename, track.number FROM track, album WHERE track.id_album = album.id and track.id=?', (self.idCurrentTrack,))
		result = self.cursor.fetchone()

		track = os.path.join(result[0], result[1])
		trackNumber = result[2]

		if self.ACTIVE_PROCESS:
			# On arrête la chanson en cours avant de lancer la suivante
			self.stop_song()

		self.ACTIVE_PROCESS = subprocess.Popen(["mpg321", "%s" % track])
		self.sc.updateSongDescription(trackNumber, track)
		pass

	def updatePidFile(self):
		file = open(pidFile, "w")
		file.write("%s,%s" % (self.idCurrentTrack, self.getIdCurrentAlbum()))
		file.close()
		self.logger("PID file updated")

	def getIdCurrentAlbum(self):
		return self.db.getIdCurrentAlbum()


jk = jukidbox()
jk.start()

sys.exit()


def stop_song():
	global ACTIVE_PROCESS
	if ACTIVE_PROCESS.poll() == None:
		# We terminate the process only if it is still active
		ACTIVE_PROCESS.terminate()


# We skip to next album, the returned value is the one of the first track of next album
def getNextAlbum(order = 1):
	global getIdCurrentAlbum, idCurrentTrack
	myLog("get Next album from %s " % getIdCurrentAlbum())
	try:
		myLog("SQL : SELECT min(id), id_album from track where id_album > %s order by id'" % getIdCurrentAlbum())
		c.execute('SELECT min(id), id_album from track where id_album > ? order by id', (getIdCurrentAlbum(), ))
		myLog("SQL END")
	except:
		myLog("ERRRRRRRRRRRRRR")
	result = c.fetchone()
	myLog("SQL fetchone ok")
	getIdCurrentAlbum = result[1]

	if getIdCurrentAlbum() is None:
		myLog("GNA, getIdCurrentAlbum() is null")
		# If the query returns an empty value it means we have reached the last album, we need to start back
		getIdCurrentAlbum = None
		idCurrentTrack = None
		idCurrentTrack = getNextTrack()
		myLog("GNA, getNextTrack : %s" % idCurrentTrack)
		return idCurrentTrack
	myLog("Begin update cover")
	updateCover()
	myLog("END of GNA")
	return result[0]
	pass


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
