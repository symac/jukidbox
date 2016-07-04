#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Library to deal with database
import sqlite3, sys
# Library to iterate through folders
import os

# Variables need to be set
MP3_FOLDER = "/media/usb/jukidbox"

#conn = sqlite3.connect('%s/jukidbox.sqlite' % MP3_FOLDER)
conn = sqlite3.connect('jukidbox.sqlite', isolation_level=None)

# Needed to store UTF8 filename
conn.text_factory = str
c = conn.cursor()

# We need to remove any information regarding the music DB
c.execute("delete from album")
c.execute("delete from track")
c.execute("delete from params where label='LAST_PLAYED'")

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
conn.close()
print "Closing"
