#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3, os
import RPi.GPIO as GPIO
import sys
import re


class databaseControl:
	cursor = None
	conn = None
	logger = None

	idCurrentTrack = None
	idCurrentAlbum = None

	currentTrackNumber = None
	currentTrackTitle = None

	shufflePin = 15;

	pidFile = None
	md5File = None

	MP3_FOLDER = None

	def __init__(self, logger, mp3_folder):
		self.logger = logger
		self.MP3_FOLDER = mp3_folder

		database = '%s/jukidbox.sqlite' % mp3_folder
		self.pidFile = "%s/song.pid" % mp3_folder
		self.md5File = "%s/md5.txt" % mp3_folder

		self.connectToDatabase(database)

		print "Connexion a %s" % database
		self.updateDatabaseIfNeeded()
		self.getInfoFromPidFile()

	def connectToDatabase(self, database):
		self.logger.msg("Init DB")
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.shufflePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		print GPIO.input(self.shufflePin)
		self.conn = sqlite3.connect(database,  check_same_thread = False)

		self.conn.text_factory = str
		self.cursor = self.conn.cursor()
		self.logger.msg("Database loaded")

	def getInfoFromPidFile(self):
		if os.path.isfile(self.pidFile):
			with open(self.pidFile, 'r') as content_file:
				content = content_file.read().strip()
				if content != "":
					contentTab = content.split(",")
					self.idCurrentTrack = contentTab[0]
					self.idCurrentAlbum = contentTab[1]

		if self.idCurrentTrack is None:
			self.getNextTrack()

	def writeToPidFile(self, line = ''):
		file = open(self.pidFile, "w")
		file.write(line)
		file.close()

	def updatePidFile(self):
	    self.writeToPidFile("%s,%s" % (self.getIdCurrentTrack(), self.getIdCurrentAlbum()))

	def getIdCurrentAlbum(self):
		return self.idCurrentAlbum

	def getIdCurrentTrack(self):
		return self.idCurrentTrack

	def getNextAlbum(self, order = True):
		self.logger.msg("get Next album from %s " % self.getIdCurrentAlbum())
		try:
			if order:
				self.logger.msg("Ordre normal")
				self.cursor.execute('SELECT min(id), id_album from track where id_album > ?', (self.getIdCurrentAlbum(), ))
			else:
				self.logger.msg("ordre reverse")
				self.cursor.execute('SELECT id, id_album from track where id_album < ? order by id_album desc, id asc', (self.getIdCurrentAlbum(), ))
		except:
			self.logger.msg("ERRRRRRRRRRRRRR")

		result = self.cursor.fetchone()

		if result is None:
			# Premier album, rien avant
			self.logger.msg(">>> 1 RESULT NONE")
			self.cursor.execute('SELECT id, id_album from track order by id_album desc, id asc')
			result = self.cursor.fetchone()
		elif result[0] is None:
			# Dernier album, plus rien après
			self.cursor.execute('SELECT id, id_album from track order by id_album asc, id asc')
			result = self.cursor.fetchone()

		self.idCurrentAlbum = result[1]
		self.idCurrentTrack = result[0]

		self.logger.msg("Result : %s / %s" % (self.getIdCurrentAlbum(), self.getIdCurrentTrack()))

	def getNextTrack(self, order = True):
		self.logger.msg("DB::GNT:: Current :  %s [orrder : %s]" % (self.idCurrentTrack, order))
		if self.randomActivated():
			self.logger.msg("DB::GNT:: Random activated")

		if self.idCurrentTrack is None:
			self.logger.msg("DB::GNT:: idCurrentTrack None")
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
			self.logger.msg("DB::GNT:: idCurrentTrack OK")

			self.logger.msg("Check min : %s" % self.idCurrentTrack)
			self.logger.msg("Order : %s" % order)

			if self.randomActivated():
				self.cursor.execute('SELECT id, id_album from track order by random() limit 0,1')
			elif order == True:
				self.cursor.execute('SELECT min(id), id_album from track where id > ? order by id', (self.idCurrentTrack, ))
			elif order == False:
				self.cursor.execute('SELECT max(id), id_album from track where id < ? order by id', (self.idCurrentTrack, ))

			result = self.cursor.fetchone()
			self.idCurrentTrack = result[0]
			self.logger.msg("Rowcount next track : %s [%s / %s]" % (len(result), result[0], result[1]))

			# We manage the last track of the last album
			if result[1] is None:
				self.logger.msg("DB::GNT:: result1 NONE ")
				self.idCurrentTrack = None
				self.getNextTrack(order)
			elif result[1] != self.idCurrentAlbum:
				self.logger.msg("DB::GNT:: result1 diff de 1")
				self.idCurrentAlbum = result[1]

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

		# Cleaning the track title
		self.currentTrackTitle = re.sub("^\d*[^A-Za-z0-9]*", "", self.currentTrackTitle)
		self.currentTrackTitle = re.sub("\.mp3", "", self.currentTrackTitle)

		trackPath = os.path.join(result[0], result[1])
		return trackPath

	def getCoverPath(self):
		coverPath = None
		self.cursor.execute('SELECT directory, cover from album where id = ?', (self.getIdCurrentAlbum(), ))
		result = self.cursor.fetchone()
		if result[1] is not None:
			coverPath = os.path.join(*result)
		return coverPath

	def updateDatabaseIfNeeded(self):
		import subprocess

		mp3CurrentSize = subprocess.check_output(['du', '-s', self.MP3_FOLDER]).split()[0].decode('utf-8')
		mp3PreviousSize = 0

		if os.path.isfile(self.md5File):
			file = open(self.md5File, "r")
			mp3PreviousSize = file.read()
			file.close()

		if mp3CurrentSize != mp3PreviousSize:
			self.logger.msg("Need update")
			self.updateDatabase()
			file = open(self.md5File, "w")
			file.write("%s" % (mp3CurrentSize))
			file.close()
			self.writeToPidFile("")

	def updateDatabase(self):
		self.resetDatabase()

		# We are going to iterate through all subdirectories of MP3_FOLDER
		subdirs = [x[0] for x in os.walk(self.MP3_FOLDER)]
		for subdir in subdirs:
			self.logger.msg("# %s #" % subdir)

			tracks = []
			cover = ""

			files = os.walk(subdir).next()[2]
			if (len(files) > 0):
				for file in sorted(files):
					if file.upper().endswith("MP3") or file.upper().endswith("OGG"):
						tracks.append(file)
					elif file.upper().endswith("JPG"):
						cover = file

				# We start by creating an entry for the album
				self.cursor.execute("insert into album (`directory`, `cover`) values (?, ?)",  (subdir, cover))
				id_album = self.cursor.lastrowid
				self.logger.msg("Ajout album %s" % id_album)

				trackNumber = 1
				for track in tracks:
					self.cursor.execute("insert into track (`id_album`, `filename`, `number`) values (?, ?, ?)", (id_album, track, trackNumber))
					self.logger.msg("%s [%s %s]" % (track[0:30], trackNumber, self.cursor.lastrowid))
					trackNumber += 1
				# We commit this album
				self.conn.commit()

		self.logger.msg("Closing connection, update finished")

	def resetDatabase(self):
		self.createTableAlbum()
		self.createTableTrack()

		# We need to remove any information regarding the music DB
		self.cursor.execute("delete from album")
		self.cursor.execute("delete from track")

	def createTableAlbum(self):
		self.logger.msg("Create Album table")
		self.cursor.execute('CREATE TABLE IF NOT EXISTS "album" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "directory" VARCHAR, "cover" VARCHAR)')

	def createTableTrack(self):
		self.logger.msg("Create Track table")
		self.cursor.execute('CREATE TABLE IF NOT EXISTS "track" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "id_album" INTEGER NOT NULL , "filename" VARCHAR NOT NULL , "number" INTEGER)')
