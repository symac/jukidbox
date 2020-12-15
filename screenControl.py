#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
import os
import datetime

class screenControl:
	isActive = False
	screen = None
	screen_w = None
	screen_h = None
	background = None

	def __init__(self, logger):
		self.logger = logger

	def prepareScreen(self):
		if not self.isActive:
			self.logger("Écran non actif")
			return
		pygame.init()

		os.environ['SDL_VIDEODRIVER']="directfb"
		pygame.mouse.set_visible(False)
		infoObject = pygame.display.Info()
		self.screen_w = infoObject.current_w
		self.screen_h = infoObject.current_h

		self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
		self.background = pygame.Surface(self.screen.get_size())
		self.background.fill((255,200,0))

		infoObject = pygame.display.Info()
		pygame.display.set_mode((infoObject.current_w, infoObject.current_h))

		self.logger("SC::Ecran initial : W : %s / H : %s" % (self.screen_w, self.screen_h))

	def isVertical(self):
		if self.screen_w < self.screen_h:
			return True
		else:
			return False

	def setActive(self, value):
		self.isActive = value

	def updateCoverWithFile(self, id_album, cover_w, cover_h):
		# We clean the previous cover
		if self.isActive:
			with open("/home/rpi/covers/%s.txt" % id_album,'rb') as f:
				imgCoverFil = f.read()
				img = pygame.image.fromstring(imgCoverFil, (cover_w, cover_h), 'RGB')
				self.background.blit(img, (0,0))
				self.screen.blit(self.background,(0,0))
				# pygame.display.flip() # update the display
				return
		else:
			self.logger("SC::Cover not displayed, screen inactive")

	def updateSongDescription(self, number, title):
		if self.isActive:
			try:
				# We hide the previous data
				if self.isVertical():
					pygame.draw.rect(self.background, pygame.Color(255, 255, 255), pygame.Rect(0, self.screen_w, self.screen_w, self.screen_h))
				else:
					pygame.draw.rect(self.background, pygame.Color(255, 255, 255), pygame.Rect(0, self.screen_w, self.screen_w, self.screen_h))

				# Display some text
				font = pygame.font.Font(None, 128)
				text = font.render(str(number), 1, (0, 0, 0))
				textpos = text.get_rect()
				textpos.centerx = self.background.get_rect().centerx
				textpos.centery = self.screen_w + 64

				self.background.blit(text, textpos)

				font = pygame.font.Font(None, 36)
				rect = pygame.Rect(10, self.screen_w + 160, self.screen_w, self.screen_h)

				self.drawText(self.background, os.path.basename(title), (0, 0, 0), rect , font)

				# Blit everything to the screen
				self.screen.blit(self.background, (0, 0))
				
				pygame.display.flip()

			except Exception, e:
				self.logger("SC::Erreur drawtext")
				self.logger("SC::", e)
				raise
			return
		else:
			self.logger("SC::Song description not diplayed, screen inactive")

	def drawText(self, surface, text, color, rect, font, aa=False, bkg=None):
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

	def coverToString(self, path):
		img=pygame.image.load(path)
		img_size = img.get_size()
		if self.isVertical():
			img_resize = pygame.transform.scale(img, (self.screen_w, (self.screen_w * img_size[1] / img_size[0]))).convert()
		else:
			img_resize = pygame.transform.scale(img, (self.screen_h, (self.screen_h * img_size[1] / img_size[0]))).convert()
		imgString=pygame.image.tostring(img_resize, 'RGB')
		return imgString, img_resize.get_size()

	def checkQuit(self):
		if self.isActive:
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					return True
				elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
					return True

		return False
