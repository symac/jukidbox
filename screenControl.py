#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
import os

class screenControl:
	isActive = False
	screen = None
	screen_w = None
	screen_h = None
	background = None
	orientation = 1 # default is horizontal

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

		self.logger("SC::Ecran initialé : W : %s / H : %s" % (self.screen_w, self.screen_h))

	def setVertical(self):
		self.orientation = 0

	def isVertical(self):
		return self.orientation == 0

	def setActive(self, value):
		self.isActive = value

	def updateCoverWithFile(self, filename):
		self.logger("SC::Loading cover %s" % filename)
		# We clean the previous cover
		if self.isActive:
			pygame.draw.rect(self.background, pygame.Color(200, 200, 200), pygame.Rect(0, 0, self.screen_w, self.screen_w))
			img=pygame.image.load(filename)
			img_size = img.get_size()
			self.logger("Taille image originale : %s x %s" % (img_size[0], img_size[1]))
			if self.isVertical():
				img_resize = pygame.transform.scale(img, (self.screen_w, (self.screen_w * img_size[1] / img_size[0])))
			else:
				img_resize = pygame.transform.scale(img, (self.screen_h, (self.screen_h * img_size[1] / img_size[0])))

			img_size = img_resize.get_size()
			self.logger("Taille image resize : %s x %s" % (img_size[0], img_size[1]))

			self.background.blit(img_resize, (0,0))
			self.screen.blit(self.background,(0,0))
			pygame.display.flip() # update the display
		else:
			self.logger("SC::Cover not displayed, screen inactive")
	pass

	def updateSongDescription(self, number, title):
		if self.isActive:
			try:
				# We hide the previous data
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
				self.logger("SC::Title updated : %s" % title)

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

	def checkQuit(self):
		if self.isActive:
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					return True
				elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
					return True

		return False
