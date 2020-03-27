#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, sys
import pygame

logEnabled = True
pidFile = "/media/usb/jukidbox/song.pid"

if logEnabled:
	import logging
	from logging.handlers import RotatingFileHandler
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler('/tmp/jukidbox.log', 'a', 1000000, 1)
	logger.addHandler(file_handler)
	file_handler.setFormatter(formatter)

def myLog(texte):
	global logEnabled
	if logEnabled:
		logger.warning(texte)

# Library to deal with database
import sqlite3
import RPi.GPIO as GPIO
import time

myLog("Loading %s" % os.path.dirname(os.path.abspath(__file__)) + '/jukidbox.sqlite')
conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + '/jukidbox.sqlite',  check_same_thread = False)

conn.text_factory = str
c = conn.cursor()


# This variable will be used to store the process of the mp3 player (and terminate it if needed)
ACTIVE_PROCESS = None
pinNextAlbum = 14
pinNextTrack = 18
pinPreviousTrack = 15

idCurrentTrack = None
idCurrentAlbum = None
screen = None
background = None

GPIO.setmode(GPIO.BCM)

GPIO.setup(pinNextAlbum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinNextTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinPreviousTrack, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def stop_song():
	global ACTIVE_PROCESS
	if ACTIVE_PROCESS.poll() == None:
		# We terminate the process only if it is still active
		ACTIVE_PROCESS.terminate()

# play a song based on the id
def play_song(song_id):
	global idCurrentTrack
	global idCurrentAlbum
	myLog("play_song : %s / %s" % (idCurrentAlbum, idCurrentTrack))
	myLog("We are moving to %s" % song_id)

	# On va stocker les infos sur la chanson en cours
	global pidFile
	file = open(pidFile, "w")
	file.write("%s,%s" % (idCurrentTrack, idCurrentAlbum))
	file.close()
	myLog("PID file updated")

	song_id = int(song_id)
	myLog("We are moving to #%s#" % song_id)
	global ACTIVE_PROCESS
	
	# We first need to stop the current player before reloading it
	c.execute('SELECT album.directory, track.filename, track.number FROM track, album WHERE track.id_album = album.id and track.id=?', (song_id,))
	result = c.fetchone()

	track = os.path.join(result[0], result[1])
	trackNumber = result[2]
	
	if ACTIVE_PROCESS:
		# On arrête la chanson en cours avant de lancer la suivante
		stop_song()

	ACTIVE_PROCESS = subprocess.Popen(["mpg321", "%s" % track])
	updateSongDescription(trackNumber, track)
	pass

def updateSongDescription(number, title):
	global screen, background
	global screen_w, screen_h

	try:

		# We hide the previous data
		pygame.draw.rect(background, pygame.Color(255, 255, 255), pygame.Rect(0, screen_w, screen_w, screen_h))

		# Display some text
		font = pygame.font.Font(None, 128)
		text = font.render(str(number), 1, (0, 0, 0))
		textpos = text.get_rect()
		textpos.centerx = background.get_rect().centerx
		textpos.centery = screen_w + 64

		background.blit(text, textpos)

		font = pygame.font.Font(None, 36)
		rect = pygame.Rect(0, screen_w + 160, screen_w, screen_h)

		drawText(background, os.path.basename(title), (0, 0, 0), rect , font)
		myLog("TITLE : %s" % title)

		# Blit everything to the screen
		screen.blit(background, (0, 0))
		pygame.display.flip()	
	except Exception, e:
		myLog("Erreur drawtext")
		myLog(e)
		raise
	return
# We need to update the cover that is displaying
def updateCover():
	global screen, background
	global screen_w, screen_h

	c.execute('SELECT directory, cover from album where id = ?', (idCurrentAlbum, ))
	result = c.fetchone()
	if result[1] is not None:
		# We clean the previous cover
		pygame.draw.rect(background, pygame.Color(255, 255, 255), pygame.Rect(0, 0, screen_w, screen_w))
		coverPath = os.path.join(*result)
		img=pygame.image.load(coverPath)
		img_size = img.get_size()
		myLog("Taille image originale : %s x %s" % (img_size[0], img_size[1]))
		img_resize = pygame.transform.scale(img, (screen_w, (screen_w * img_size[1] / img_size[0])))
		img_size = img_resize.get_size()
		myLog("Taille image resize : %s x %s" % (img_size[0], img_size[1]))
		
		background.blit(img_resize, (0,0)) 
		screen.blit(background,(0,0))
		pygame.display.flip() # update the display
	pass

def drawText(surface, text, color, rect, font, aa=False, bkg=None):
	rect = pygame.Rect(rect)
	y = rect.top
	lineSpacing = -2
 
	# get the height of the font
	fontHeight = font.size("Tg")[1]
 
	while text:
		i = 1
 
		# determine if the row of text will be outside our area
		if y + fontHeight > rect.bottom:
			break
 
		# determine maximum width of line
		while font.size(text[:i])[0] < rect.width and i < len(text):
			i += 1
 
		# if we've wrapped the text, then adjust the wrap to the last word	  
		if i < len(text): 
			i = text.rfind(" ", 0, i) + 1
 
		# render the line and blit it to the surface
		if bkg:
			image = font.render(text[:i], 1, color, bkg)
			image.set_colorkey(bkg)
		else:
			image = font.render(text[:i], aa, color)
 
		surface.blit(image, (rect.left, y))
		y += fontHeight + lineSpacing
 
		# remove the text we just blitted
		text = text[i:]

	return text

# We skip to next album, the returned value is the one of the first track of next album
def getNextAlbum(order = 1):
	global idCurrentAlbum, idCurrentTrack
	myLog("get Next album from %s " % idCurrentAlbum)
	try:
		myLog("SQL : SELECT min(id), id_album from track where id_album > %s order by id'" % idCurrentAlbum)
		c.execute('SELECT min(id), id_album from track where id_album > ? order by id', (idCurrentAlbum, ))
		myLog("SQL END")
	except:
		myLog("ERRRRRRRRRRRRRR")
	result = c.fetchone()
	myLog("SQL fetchone ok")
	idCurrentAlbum = result[1]

	if idCurrentAlbum is None:
		myLog("GNA, idCurrentAlbum is null")
		# If the query returns an empty value it means we have reached the last album, we need to start back
		idCurrentAlbum = None
		idCurrentTrack = None
		idCurrentTrack = getNextTrack()
		myLog("GNA, getNextTrack : %s" % idCurrentTrack)
		return idCurrentTrack
	myLog("Begin update cover")
	updateCover()
	myLog("END of GNA")
	return result[0]
	pass

# get the next song to play. By default the next one, if order is set to -1, the previous one
def getNextTrack(order = True):
	global idCurrentAlbum, idCurrentTrack
	myLog("")
	myLog("GNT from %s" % idCurrentTrack)

	if idCurrentTrack is None:
		c.execute('SELECT min(id), id_album from track order by id')
		result = c.fetchone()
		print result
		if result[1] != idCurrentAlbum:
			idCurrentAlbum = result[1]
			updateCover()
		return result[0]
	else:
		if order == True:
			rowcount = c.execute('SELECT min(id), id_album from track where id > ? order by id', (idCurrentTrack, ))
			myLog("Rowcount : %s" % rowcount)
		elif order == False:
			rowcount = c.execute('SELECT max(id), id_album from track where id < ? order by id', (idCurrentTrack, ))
		
		result = c.fetchone()
		myLog("Rowcount next track : %s [%s]" % (len(result), result[1]))

		# We manage the last track of the last album
		if result[1] is None:
			myLog("END OF LIST")
			if order == True:
				idCurrentTrack = None
				return getNextTrack()
			else:
				c.execute('select max(id), id_album from track')
				result = c.fetchone()
				

		if result[1] != idCurrentAlbum:
			idCurrentAlbum = result[1]
			updateCover()
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
	global idCurrentTrack, idCurrentAlbum, screen, background
	global screen_w, screen_h
	global pidFile

	pygame.init()

	os.environ['SDL_VIDEODRIVER']="directfb"
	pygame.mouse.set_visible(False)
	infoObject = pygame.display.Info()
	screen_w = infoObject.current_w
	screen_h = infoObject.current_h

	screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	background = pygame.Surface(screen.get_size())
	background.fill((255,200,0))
	
	# We are going to have a look at the pid file
	myLog("Opening PID File")
	with open(pidFile, 'r') as content_file:
		content = content_file.read().strip()
		if content:
			contentTab = content.split(",")
			idCurrentTrack = contentTab[0]
			idCurrentAlbum = contentTab[1]
			updateCover()
	
	if idCurrentTrack is None:
		myLog("Id current track empty")
		idCurrentTrack = getNextTrack()
	else:
		myLog("Id current Track : %s" % idCurrentTrack)

	infoObject = pygame.display.Info()
	pygame.display.set_mode((infoObject.current_w, infoObject.current_h))

	play_song(idCurrentTrack)
	
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
