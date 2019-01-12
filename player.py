#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, os
from subprocess import Popen, PIPE, STDOUT

class player:
	active_process = None

	def __init__(self):
		return

	def playSong(self, songPath):
		if self.active_process:
			# On arrête la chanson en cours avant de lancer la suivante
			self.stopSong()
		DEVNULL = open(os.devnull, 'wb')
		self.active_process = subprocess.Popen(["mpg321", "%s" % songPath], stdout=DEVNULL, stderr=STDOUT)

	def stopSong(self):
		if self.active_process.poll() == None:
			# We terminate the process only if it is still active
			self.active_process.terminate()

	def isPlaying(self):
		return self.active_process.poll() == None
