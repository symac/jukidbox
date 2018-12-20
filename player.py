#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

class player:
	active_process = None

	def __init__(self):
		return

	def play_song(self, songPath):
		if self.active_process:
			# On arrête la chanson en cours avant de lancer la suivante
			self.stop_song()

		self.active_process = subprocess.Popen(["mpg321", "%s" % songPath])

	def stop_song(self):
		if self.active_process.poll() == None:
			# We terminate the process only if it is still active
			self.active_process.terminate()
