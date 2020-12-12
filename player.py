#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, os
import time
from subprocess import Popen, PIPE, STDOUT
import subprocess, signal

class player:
	active_process = None

	def __init__(self):
		return

	def playSong(self, songPath, force = False):
		# Killing all mpg123
		self.stopSong()

		DEVNULL = open(os.devnull, 'wb')
		self.active_process = subprocess.Popen(["mpg123", "%s" % songPath], stdout=DEVNULL, stderr=STDOUT)

	def stopSong(self):
		if self.active_process:
			if self.active_process.poll() == None:
				# We terminate the process only if it is still active
				self.active_process.terminate()

		self.cleaningMpg123()

	def cleaningMpg123(self):
		p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
		out, err = p.communicate()
		
		for line in out.splitlines():
			if 'mpg123' in line:
				pid = int(line.split(None, 1)[0])
				os.kill(pid, signal.SIGKILL)

	def isPlaying(self):
		return self.active_process.poll() == None
