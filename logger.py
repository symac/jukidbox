import logging

class logger:
	lg = None
	def __init__(self):
		root_logger= logging.getLogger()
		root_logger.setLevel(logging.DEBUG) # or whatever
		handler = logging.FileHandler('/home/rpi/debug.log', 'w', 'utf-8') # or whatever
		handler.setFormatter(logging.Formatter('%(asctime)s %(message)s')) # or whatever
		root_logger.addHandler(handler)
		self.lg = root_logger

	def __call__(self, msg):
		self.msg(msg)

	def msg(self, msg):
		self.lg.debug(msg)
