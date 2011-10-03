#! /usr/bin/env python

# pywn.py, version 0.7
#
# Author: John Asmuth, jasmuth@eden.rutgers.edu
# Source: This is the source file.
#
# Copyright (c) 2001 by John Asmuth
# 
# Subject to the GPL
#

"""Standalone implementation of wordnet

import and use stdwn.impl as your WNImpl.
To load in the index files ahead of time, call
stdwn.init()
When finished, call stdwn.close(), which closes
the open data files

"""
        
import pywn

pywn.Const.ANTONYM = '!'
pywn.Const.HYPERNYM = '@'
pywn.Const.HYPONYM = '~'
pywn.Const.MEMBER_HOLONYM = '#m'
pywn.Const.SUBSTANCE_HOLONYM = '#s'
pywn.Const.PART_HOLONYM = '#p'
pywn.Const.MEMBER_MERONYM = '%m'
pywn.Const.SUBSTANCE_MERONYM = '%s'
pywn.Const.PART_MERONYM = '%p'
pywn.Const.ATTRIBUTE = '='
pywn.Const.ENTAILMENT = '*'
pywn.Const.CAUSE = '>'
pywn.Const.SEE_ALSO = '^'
pywn.Const.VERB_GROUP = '$'
pywn.Const.SIMILAR_TO = '&'
pywn.Const.PARTICIPLE = '<'
pywn.Const.PERTAINYM = '\\'
pywn.Const.DERIVED_FROM = '\\'

nounBaseForms =  [('s', ''),
                  ('ses', 's'),
                  ('xes', 'x'),
                  ('zes', 'z'),
                  ('ches', 'ch'),
                  ('shes', 'sh'),
                  ('men', 'man'),
                  ('ies', 'y')]
verbBaseForms =  [('s', ''),
                  ('ies', 'y'),
                  ('es', 'e'),
                  ('es', ''),
                  ('ed', 'e'),
                  ('ed', ''),
                  ('ing', 'e'),
                  ('ing', '')]
adjBaseForms =   [('er', 'e'),
                  ('er', ''),
                  ('est', 'e'),
                  ('est', '')]
advBaseForms =   []

baseFormTable = [nounBaseForms, verbBaseForms, adjBaseForms, advBaseForms]

from os import environ

WNDICT = None

try:
	WNDICT = environ['WNHOME']+'/dict'
except KeyError:
	pass
try:
	WNDICT = environ['WNDICT']
except KeyError:
	pass
if not WNDICT:
	WNDICT = 'dict'
	print "No wordnet install detected, using local data"

indexFiles = [ open(WNDICT+'/index.noun'), \
               open(WNDICT+'/index.verb'), \
               open(WNDICT+'/index.adj'), \
               open(WNDICT+'/index.adv') ]
dataFiles = [ open(WNDICT+'/data.noun'), \
              open(WNDICT+'/data.verb'), \
              open(WNDICT+'/data.adj'), \
              open(WNDICT+'/data.adv') ]
baseFiles = [ open(WNDICT+'/noun.exc'), \
              open(WNDICT+'/verb.exc'), \
              open(WNDICT+'/adj.exc'), \
              open(WNDICT+'/adv.exc') ]

formToKeys = {}
keyToSynset = {}

#get the 8 character digits from the end of the line
def getOffsets(line):
	offsets = []
	try:
		while 1:
			offsets.append(int(line[-8:]))
			line = line[0:-9]
	except ValueError:
		pass
	return offsets
    
#take one line of an index file and put it into the table
def loadIndexLine(i, l):
	form = l[:l.index(' ')]
	offsets = getOffsets(l)
	if not form in formToKeys:
		formToKeys[form] = []
	for o in offsets:
		formToKeys[form].append((i, o))

#load the index files into memory
def loadIndexData():
	for i in range(4):
		file = indexFiles[i]
		lines = file.readlines()
		file.close()
		for l in lines:
			if l[0] == ' ':
				continue
			l = l.strip()
			loadIndexLine(i, l)

def posStrToInt(pos):
	if pos == 'n':
		return 0
	if pos == 'v':
		return 1
	if pos == 'a':
		return 2
	if pos == 'r':
		return 3
	return None

hexdigits = '0123456789abcdef'

#another newbish thing...hex('aa') doesn't work
def hexStrToInt(hex):
	if len(hex) == 1:
		return hexdigits.index(hex)
	v = hexdigits.index(hex[-1:])
	return v + len(hexdigits) * hexStrToInt(hex[:-1])

class WNImpl(pywn.WNImpl):
	def __init__(self):
		self.cache = False
	def open(self):
		pass
	def getSynsetKeyFromString(self, key):
		tok = key.split(':')
		return (int(tok[0]), int(tok[1]))
    #load a synset from the data files
	def grabSynset(self, key):
		if self.cache:
			if key in keyToSynset:
				return keyToSynset[key]
			
		dataFiles[key[0]].seek(key[1], 0)
		line = dataFiles[key[0]].readline().strip()

		ss = pywn.Synset()
		ss.impl = self
    
		ss.key = key

        #bypass synset_offset, lex_filenum fields
		tok = line.split(' ')
		tok.pop(0)
		tok.pop(0)

        #ss_type field
		ss.pos = tok.pop(0)
        
        #w_cnt field        
		ss.count = hexStrToInt(tok.pop(0))

		ss.synonyms = []

        #word, lex_id fields
		for sense in range(ss.count):
			ws = pywn.WordSense()
			ws.rels = []
			ws.form = tok.pop(0)
			ws.sense = hexStrToInt(tok.pop(0))
			ws.ss = ss
			ss.synonyms.append(ws)

        #p_cnt field
		p_cnt = int(tok.pop(0))

		ss.rels = []

	#pointers
		for pi in range(p_cnt):
			sym = tok.pop(0)
			offs = int(tok.pop(0))
			posStr = tok.pop(0)
			srctar = tok.pop(0)

			pos = posStrToInt(posStr)

			if srctar == '0000':
			#semantic relation
				ss.rels.append((sym, (pos, offs)))
			else:
		#lexical relation
				src = hexStrToInt(srctar[:2])
				tar = hexStrToInt(srctar[2:])
				ss.synonyms[src-1].rels.append((sym, ((pos, offs), tar)))

		#pull gloss off end
		ss.defn = line.split('|').pop().split(';')
		ss.gloss = ss.defn[0]
		ss.examples = ss.defn[1:]

		
		if self.cache:
			keyToSynset[ss.key] = ss

		return ss

	def findWordLine(self, form, file, min, max):
		if min == max:
			return None
		cur = (min+max)/2
		file.seek(cur)
		c = file.read(1)
		while c != '\n':
			cur-=1
			try:
				file.seek(cur)
			except IOError:
				return None
			c = file.read(1)
		file.seek(cur+1)
		offs = cur+1
		line = file.readline().strip()
		firstword = line[:line.index(' ')]

		if form == firstword:
			return line
		if form < firstword:
			return self.findWordLine(form, file, min, offs)
		if form > firstword:
			return self.findWordLine(form, file, file.tell(), max)

	def grabOffsetsFromFile(self, form, file):
		file.seek(0, 2)
		line = self.findWordLine(form, file, 0, file.tell())
		if line:
			return getOffsets(line)
		return []

	def grabBaseForms(self, inf):
		baseFormList = []
		for i in range(4):
			baseFiles[i].seek(0, 2)
			baseForms = self.findWordLine(inf, baseFiles[i], 0, baseFiles[i].tell())
			if baseForms:
				baseFormList += baseForms.split()
			for (iend, bend) in baseFormTable[i]:
				if inf[-len(iend):] == iend:
					baseFormList.append(inf[:-len(iend)]+bend)
		return baseFormList
			

	def grabKeys(self, form):
	#search through cached index for form
		if form in formToKeys:
			return formToKeys[form]

		try:
    		#go through index files
			keys = []
			for i in range(4):
				for o in self.grabOffsetsFromFile(form, indexFiles[i]):
					keys.append((i, o))
			formToKeys[form] = keys
			return keys
		except ValueError:
			return []

impl = WNImpl()

def init(cache=False):
	impl.cache = cache
	global formToKeys
	try:
		del formToKeys
	except UnboundLocalError:
		pass
	formToKeys = {}
	loadIndexData()
	for f in indexFiles:
		f.close()
		
	if cache:
		for keys in formToKeys.values():
			for key in keys:
				impl.grabSynset(key)
		
def close():
	for f in indexFiles:
		f.close()
	for f in dataFiles:
		f.close()
	for f in baseFiles:
		f.close()
	try:
		del formToKeys
	except UnboundLocalError:
		pass
	try:
		del keyToSynset
	except UnboundLocalError:
		pass

lsf = impl.lookupSynsetsByForm

def test():
	syns = impl.lookupSynsetsByForm('green')
	for ss in syns:
		print ss.gloss
		print ss.rels
		for ws in ss.synonyms:
		    print ws.form+":",ws.rels
		ssHyp = ss.hypernym()
		if ssHyp != None:
			print 'hypernym:',
			for ws in ssHyp.synonyms:
				print ws.form, '-',
				print ssHyp.gloss
		print '--------------------------------------------------------------------------------'


if __name__ == '__main__':
	print "loading wordnet"
	init(True)
	print "wordnet is in memory"
	#test()
	close()
