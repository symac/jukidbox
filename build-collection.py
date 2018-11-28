#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Library to deal with database
import sqlite3, sys
# Library to iterate through folders
import os

import logging

# Variables need to be set
MP3_FOLDER = "/media/usb/jukidbox"
DATABASE = '%s/jukidbox.sqlite' % MP3_FOLDER
#MP3_FOLDER = "/home/pi/mp3test"

conn = sqlite3.connect(DATABASE)

# Needed to store UTF8 filename
conn.text_factory = str
c = conn.cursor()

# We need to build the database if it does not exist
def is_table(c, table_name):
    """ This method seems to be working now"""
    query = "SELECT name from sqlite_sequence WHERE name='" + table_name + "';"
    cursor = c.execute(query)
    result = cursor.fetchone()
    if result == None:
        return False
    else:
        return True

def createTableAlbum(c):
	logging.info("Create Album table")
	c.execute('CREATE TABLE IF NOT EXISTS "album" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "directory" VARCHAR, "cover" VARCHAR)')

def createTableTrack(c):
	logging.info("Create Track table")
	c.execute('CREATE TABLE IF NOT EXISTS "track" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "id_album" INTEGER NOT NULL , "filename" VARCHAR NOT NULL , "number" INTEGER)')

createTableAlbum(c)
createTableTrack(c)

# We need to remove any information regarding the music DB
c.execute("delete from album")
c.execute("delete from track")

conn.commit()

# We are going to iterate through all subdirectories of MP3_FOLDER
subdirs = [x[0] for x in os.walk(MP3_FOLDER)]
for subdir in subdirs:
	print "# %s #" % subdir

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
		c.execute("insert into album (`directory`, `cover`) values (?, ?)",  (subdir, cover))
		id_album = c.lastrowid
		print "Ajout album %s" % id_album

		trackNumber = 1
		for track in tracks:
			c.execute("insert into track (`id_album`, `filename`, `number`) values (?, ?, ?)", (id_album, track, trackNumber))
			print "%s [%s %s]" % (track[0:30], trackNumber, c.lastrowid)
			trackNumber += 1
		# We commit this album
conn.commit()
conn.close()
print "Closing"
