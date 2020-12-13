#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from iniparse import INIConfig

class config:
	configFile = None

	def loadIniFile(self, path):
		print "Chargement ini file %s" % path
		self.configFile = INIConfig(file(path))
	

	def __init__(self):
		# On regarde s'il y a un fichier de config sur la clé USB
		if os.path.isfile("/media/usb/jukidbox.ini"):
			self.loadIniFile("/media/usb/jukidbox.ini")
		elif os.path.isfile("/home/rpi/jukidbox.ini"):
			self.loadIniFile("/home/rpi/jukidbox.ini")
		elif os.path.isfile("/root/jukidbox/jukidbox.ini"):
			self.loadIniFile("/root/jukidbox/jukidbox.ini")
		else:
			# Pas de fichier de paramètre, on va en créer un par défaut
			print "########## PAS DE FICHIER PARAM"
			return

	def param(self, group, attribute):
		value = self.configFile[group][attribute]
		# Pour le moment on ne stocke que des numéros de PIN dans le 
		# fichier de config, on les cast au moment de les renvoyer
		return int(value)