#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
class databaseControl:
	cursor = None
	logger = None

	idCurrentTrack = None
	idCurrentAlbum = None

	def __init__(self, logger, mp3_folder):
		database = '%s/jukidbox.sqlite' % mp3_folder
		pidFile = "%s/song.pid" % mp3_folder

		print "Loading %s" % database

		self.logger = logger
		self.connectToDatabase(database)
		self.getInfoFromPidFile(pidFile)

	def connectToDatabase(self, database):

		conn = sqlite3.connect(database,  check_same_thread = False)

		conn.text_factory = str
		self.cursor = conn.cursor()
		self.logger.msg("Database loaded")

	def getInfoFromPidFile(self, pidFile):
		with open(pidFile, 'r') as content_file:
			content = content_file.read().strip()
			if content != "":
				contentTab = content.split(",")
				self.idCurrentTrack = contentTab[0]
				self.idCurrentAlbum = contentTab[1]

		if self.idCurrentTrack is None:
			self.idCurrentTrack = self.getNextTrack()

	def getIdCurrentAlbum(self):
		return self.idCurrentAlbum

	def getNextTrack(self, order = True):
		if self.idCurrentTrack is None:
			self.cursor.execute('SELECT min(id), id_album from track order by id')
			result = self.cursor.fetchone()
			print result
			if result[1] != self.idCurrentAlbum:
				self.idCurrentAlbum = result[1]
				self.updateCover()
			return result[0]
		else:
			if order == True:
				rowcount = self.cursor.execute('SELECT min(id), id_album from track where id > ? order by id', (idCurrentTrack, ))
			elif order == False:
				rowcount = self.cursor.execute('SELECT max(id), id_album from track where id < ? order by id', (idCurrentTrack, ))

			result = self.cursor.fetchone()
			myLog("Rowcount next track : %s [%s]" % (len(result), result[1]))

			# We manage the last track of the last album
			if result[1] is None:
				idCurrentTrack = None
				return getNextTrack()

			if result[1] != idCurrentAlbum:
				idCurrentAlbum = result[1]
				updateCover()
			return result[0]
		pass

	def gertCoverPath():
		coverPath = None
		self.cursor.execute('SELECT directory, cover from album where id = ?', (self.getIdCurrentAlbum(), ))
		result = self.cursor.fetchone()
		if result[1] is not None:
			coverPath = os.path.join(*result)
		return coverPath
