#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3, os
import RPi.GPIO as GPIO

class databaseControl:
	cursor = None
	logger = None

	idCurrentTrack = None
	idCurrentAlbum = None

	currentTrackNumber = None
	currentTrackTitle = None

	shufflePin = 15;

	pidFile = None

	def __init__(self, logger, mp3_folder):
		database = '%s/jukidbox.sqlite' % mp3_folder
		self.pidFile = "%s/song.pid" % mp3_folder

		print "Loading %s" % database

		self.logger = logger
		self.connectToDatabase(database)
		self.getInfoFromPidFile()

	def connectToDatabase(self, database):
		self.logger.msg("Init DB")
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.shufflePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		print GPIO.input(self.shufflePin)
		conn = sqlite3.connect(database,  check_same_thread = False)

		conn.text_factory = str
		self.cursor = conn.cursor()
		self.logger.msg("Database loaded")

	def getInfoFromPidFile(self):
		with open(self.pidFile, 'r') as content_file:
			content = content_file.read().strip()
			if content != "":
				contentTab = content.split(",")
				self.idCurrentTrack = contentTab[0]
				self.idCurrentAlbum = contentTab[1]

		if self.idCurrentTrack is None:
			self.idCurrentTrack = self.getNextTrack()


	def updatePidFile(self):
		file = open(self.pidFile, "w")
		file.write("%s,%s" % (self.getIdCurrentTrack(), self.getIdCurrentAlbum()))
		file.close()
		self.logger("PID file updated")

	def getIdCurrentAlbum(self):
		return self.idCurrentAlbum

	def getIdCurrentTrack(self):
		return self.idCurrentTrack

	def getNextAlbum(self, order = True):
		self.logger("get Next album from %s " % self.getIdCurrentAlbum())
		try:
			if order:
				self.cursor.execute('SELECT min(id), id_album from track where id_album > ? order by id', (self.getIdCurrentAlbum(), ))
			else:
				self.cursor.execute('SELECT min(id), id_album from track where id_album < ? order by id', (self.getIdCurrentAlbum(), ))

		except:
			self.logger("ERRRRRRRRRRRRRR")
		result = self.cursor.fetchone()
		self.logger("SQL fetchone ok : %s / %s" % (result[0], result[1]))
		self.idCurrentAlbum = result[1]
		self.idCurrentTrack = result[0]

		if self.getIdCurrentAlbum() is None:
			self.logger("GNA, getIdCurrentAlbum() is null")
			# If the query returns an empty value it means we have reached the last album, we need to start back
			self.idCurrentTrack = None
			self.idCurrentTrack = self.getNextTrack(order)

			self.logger("GNA, getNextTrack : %s" % self.idCurrentTrack)
		self.logger("END of GNA")

	def getNextTrack(self, order = True):
		print "Current :  %s [orrder : %s]" % (self.idCurrentTrack, order)
		if self.randomActivated():
			self.logger("Random activated")
			
		if self.idCurrentTrack is None:
			if order:
				print "ORDER TRUE"
				self.cursor.execute('SELECT min(id), id_album from track order by id')
			else:
				print "ORDER FALSE"
				self.cursor.execute('SELECT max(id), id_album from track order by id')
			result = self.cursor.fetchone()
			if result[1] != self.idCurrentAlbum:
				self.idCurrentAlbum = result[1]
			self.idCurrentTrack = result[0]
		else:
			self.logger("Check min : %s" % self.idCurrentTrack)
			self.logger("Order : %s" % order)
			if order == True:
				rowcount = self.cursor.execute('SELECT min(id), id_album from track where id > ? order by id', (self.idCurrentTrack, ))
			elif order == False:
				rowcount = self.cursor.execute('SELECT max(id), id_album from track where id < ? order by id', (self.idCurrentTrack, ))

			result = self.cursor.fetchone()
			self.idCurrentTrack = result[0]
			self.logger("Rowcount next track : %s [%s / %s]" % (len(result), result[0], result[1]))

			# We manage the last track of the last album
			if result[1] is None:
				self.idCurrentTrack = None
				self.getNextTrack(order)
			elif result[1] != self.idCurrentAlbum:
				self.idCurrentAlbum = result[1]
		pass

	def randomActivated(self):
		if GPIO.input(self.shufflePin):
			return False
		else:
			return True

	def getCurrentSongPath(self):
		self.cursor.execute('SELECT album.directory, track.filename, track.number FROM track, album WHERE track.id_album = album.id and track.id=?', (self.getIdCurrentTrack(),))
		result = self.cursor.fetchone()


		self.currentTrackNumber = result[2]
		self.currentTrackTitle = result[1]

		trackPath = os.path.join(result[0], result[1])
		return trackPath

	def getCoverPath(self):
		coverPath = None
		self.cursor.execute('SELECT directory, cover from album where id = ?', (self.getIdCurrentAlbum(), ))
		result = self.cursor.fetchone()
		if result[1] is not None:
			coverPath = os.path.join(*result)
		return coverPath
