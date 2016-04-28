#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, sys
import pygame

# Library to deal with database
import sqlite3
import RPi.GPIO as GPIO
import time

conn = sqlite3.connect('jukidbox.sqlite')
conn.text_factory = str
c = conn.cursor()

# This variable will be used to store the process of the mp3 player (and terminate it if needed)
ACTIVE_PROCESS = None
pinNextAlbum = 18
pinNextTrack = 23

pinNextAlbum = 18
pinNextTrack = 23

idCurrentTrack = None
idCurrentAlbum = None
screen = None
background = None

GPIO.setmode(GPIO.BCM)

GPIO.setup(pinNextAlbum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinNextTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def log(log_str):
	print log_str

def stop_song():
	global ACTIVE_PROCESS
	ACTIVE_PROCESS.terminate()
	ACTIVE_PROCESS = None

# play a song based on the id
def play_song(song_id):
	global ACTIVE_PROCESS
	
	# We first need to stop the current player before reloading it
	c.execute('SELECT album.directory, track.filename FROM track, album WHERE track.id_album = album.id and track.id=?', (song_id,))

	track = os.path.join(*c.fetchone())
	
	if ACTIVE_PROCESS:
		# On arrête la chanson en cours avant de lancer la suivante
		stop_song()

	ACTIVE_PROCESS = subprocess.Popen(["mpg321", "%s" % track])
	updateSongName(track)
	pass

def updateSongName(songTitle):
	WHITE = (255,255,255)
	# Display some text
	font_big = pygame.font.Font(None, 20)

	text_surface = font_big.render('%s' % songTitle, True, WHITE)
	rect = text_surface.get_rect(center=(180,780))
	screen.fill((255,200,0))
	screen.blit(text_surface, rect)
	updateCover()
	pygame.display.flip()

# We need to update the cover that is displaying
def updateCover():
	global screen, background
	c.execute('SELECT directory, cover from album where id = ?', (idCurrentAlbum, ))
	result = c.fetchone()
	if result[1] is not None:
		coverPath = os.path.join(*result)
		img=pygame.image.load(coverPath)
		img_size = img.get_size()
		background = pygame.transform.scale(img, (480, (480 * img_size[0] / img_size[1])))
		screen.blit(img,(0,0))
		pygame.display.flip() # update the display
	pass


# We skip to next album, the returned value is the one of the first track of next album
def getNextAlbum(order = 1):
	global idCurrentAlbum, idCurrentTrack
	c.execute('SELECT min(id), id_album from track where id_album > ? order by id', (idCurrentAlbum, ))

	result = c.fetchone()
	idCurrentAlbum = result[1]
	if idCurrentAlbum is None:
		# If the query returns an empty value it means we have reached the last album, we need to start back
		idCurrentAlbum = None
		idCurrentTrack = None
		return getNextTrack()
	updateCover()
	return result[0]
	pass

# get the next song to play. By default the next one, if order is set to -1, the previous one
def getNextTrack(order = 1):
	global idCurrentAlbum, idCurrentTrack

	if idCurrentTrack is None:
		c.execute('SELECT min(id), id_album from track order by id')
		result = c.fetchone()
		if result[1] != idCurrentAlbum:
			idCurrentAlbum = result[1]
			updateCover()
		return result[0]
	else:
		c.execute('SELECT min(id), id_album from track where id > ? order by id', (idCurrentTrack, ))
		result = c.fetchone()
		if result[1] != idCurrentAlbum:
			idCurrentAlbum = result[1]
			updateCover()
		return result[0]
	pass

def isKeyPressed(pinNumber):
	input_state = GPIO.input(pinNumber)
	if input_state == False:
		return True
	return False


def main():
	# We need to init the display
	global idCurrentTrack, idCurrentAlbum, screen

	pygame.init()
	os.environ['SDL_VIDEODRIVER']="directfb"
	pygame.mouse.set_visible(False)
	screen = pygame.display.set_mode((480, 800))
	screen.fill((255,200,0))
	
	# We start by loading the first track

	idCurrentTrack = getNextTrack()
	play_song(idCurrentTrack)


	try:
		running = True
		while (running):
			# We need to check that esc had not been pressed
			isPressedNextAlbum = isKeyPressed(pinNextAlbum)
			isPressedNextTrack = isKeyPressed(pinNextTrack)
			if isPressedNextTrack:
				idCurrentTrack = getNextTrack()
				play_song(idCurrentTrack)
			elif isPressedNextAlbum:
				idCurrentTrack = getNextAlbum()
				play_song(idCurrentTrack)

			for e in pygame.event.get():
				if e.type == QUIT:
					running = False
				elif e.type == KEYDOWN and e.key == K_ESCAPE:
					running = False

			time.sleep(0.1)	
		stop_song()
		print "FIN"
	except:
		stop_song()

if __name__ == '__main__':
    main()