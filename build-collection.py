#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Library to deal with database
import sqlite3, sys
# Library to iterate through folders
import os

import logging
logging.basicConfig(level=logging.INFO)

class collectionBuilder:
	# Variables need to be set
	MP3_FOLDER = "/media/usb/jukidbox"
	DATABASE = '%s/jukidbox.sqlite' % MP3_FOLDER
	conn = None
	c = None

	def __init__(self):
		self.setDatabaseConnection()

	def setDatabaseConnection(self):
		self.conn = sqlite3.connect(self.DATABASE)
		# Needed to store UTF8 filename
		self.conn.text_factory = str
		self.c = self.conn.cursor()

	def createTableAlbum(self):
		logging.info("Create Album table")
		self.c.execute('CREATE TABLE IF NOT EXISTS "album" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "directory" VARCHAR, "cover" VARCHAR)')

	def createTableTrack(self):
		logging.info("Create Track table")
		self.c.execute('CREATE TABLE IF NOT EXISTS "track" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "id_album" INTEGER NOT NULL , "filename" VARCHAR NOT NULL , "number" INTEGER)')

	def resetDatabase(self):
		self.createTableAlbum()
		self.createTableTrack()

		# We need to remove any information regarding the music DB
		self.c.execute("delete from album")
		self.c.execute("delete from track")
		self.conn.commit()

	def updateLibrary(self):
		self.resetDatabase()

		# We are going to iterate through all subdirectories of MP3_FOLDER
		subdirs = [x[0] for x in os.walk(self.MP3_FOLDER)]
		for subdir in subdirs:
			logging.info("# %s #" % subdir)

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
				self.c.execute("insert into album (`directory`, `cover`) values (?, ?)",  (subdir, cover))
				id_album = self.c.lastrowid
				logging.info("Ajout album %s" % id_album)

				trackNumber = 1
				for track in tracks:
					self.c.execute("insert into track (`id_album`, `filename`, `number`) values (?, ?, ?)", (id_album, track, trackNumber))
					logging.info("%s [%s %s]" % (track[0:30], trackNumber, self.c.lastrowid))
					trackNumber += 1
				# We commit this album
		self.conn.commit()
		self.conn.close()
		logging.info("Closing connection, update finished")

builder = collectionBuilder()
builder.updateLibrary()
