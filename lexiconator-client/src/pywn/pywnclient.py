import pywn
import cPickle
from socket import *
from StringIO import *

BLOCK_SIZE = 1024 * 8

class WNImpl(pywn.WNImpl):
	def grabData(self, sock):
		data = sock.recv(BLOCK_SIZE)
		return data  
	def grabSynset(self, key):
		cmd = ('ss', key)
		cPickle.dump(cmd, self.sockfile)
		return cPickle.load(self.sockfile)
	def grabKeys(self, form):
		cmd = ('key', form)
		cPickle.dump(cmd, self.sockfile)
		return cPickle.load(self.sockfile)
	def open(self, host=None, port=None):
		import sys
		if not host:
			print "Enter pywnserver IP:",
			host = sys.stdin.readline()
		if ':' in host:
			[host, port] = host.split(':')
			port = int(port)
		if not port:
			port = 3334
		self.sock = socket(AF_INET, SOCK_STREAM)
		self.sock.connect((host, port))
		self.sockfile = self.sock.makefile('r+')

impl = WNImpl()

def open(host, port):
	impl.open(host, port)

def close():
	impl.sock.shutdown(2)
