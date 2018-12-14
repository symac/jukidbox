import logging

class logger:
    lg = None
    def __init__(self):
        #logging.basicConfig(filename='example.log', level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
        self.lg = logging.getLogger(__name__)

    def __call__(self, msg):
        self.msg(msg)

    def msg(self, msg):
        self.lg.debug(msg)
