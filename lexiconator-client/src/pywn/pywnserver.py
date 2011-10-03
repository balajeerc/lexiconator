#! /usr/bin/env python

from socket import *
from stdwn import impl
from StringIO import *
import thread
import cPickle

stayalive = 1
port = 3334

def acceptConnections(arg):
	s = socket(AF_INET, SOCK_STREAM)
	s.bind(('', port))
	s.listen(1)
	print "pwynserver listening on port", port
	print "<return> to stop"
	while stayalive:
		conn = s.accept()
		print 'connection opened('+conn[1][0]+':'+`conn[1][1]`+')'
		thread.start_new_thread(handleRequests, (conn,))
	s.shutdown(2)

kstr = impl.getSynsetKeyFromString

def processCommand(cmd):
	if cmd[0] == 'ss':
		func = impl.grabSynset
	elif cmd[0] == 'key':
		func = impl.grabKeys
	else:
		return None
	return func(cmd[1])

def handleRequests(arg):
	sock = arg[0]
	sockfile = sock.makefile('r+')
	host = arg[1][0]
	port = `arg[1][1]`
	while 1:
		try:
			cmd = cPickle.load(sockfile)
			print host+":"+port, cmd[0], cmd[1]
		except error:
			break
		except EOFError:
			break
		except cPickle.UnpicklingError:
			break
		if not cmd:
			break
		cPickle.dump(processCommand(cmd), sockfile)
	sockfile.close()
	sock.shutdown(2)
	print 'connection closed('+host+':'+port+')'

	
def open():
	thread.start_new_thread(acceptConnections, (None,))

def close():
	stayalive = 0
	
if __name__ == '__main__':
	#default pywnserver port
	import sys
	port = int(sys.argv[1])
	open()
	sys.stdin.readline()
	close()
