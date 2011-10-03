# pywn.py, version 0.7
#
# Author: John Asmuth, jasmuth@eden.rutgers.edu
# Source: This is the source file.
#
# Copyright (c) 2001 by John Asmuth
# 
# Subject to the GPL
#

"""Module pywn

Do not import this module to use pywn. Instead, import the
module that imports this module(ie stdwn).

"""

__author__ = 'John Asmuth'

#the implementing module defines these
class Const:
	"""Needs to have the following members defined:
	ANTONYM HYPERNYM HYPONYM MEMBER_HOLONYM SUBSTANCE_HOLONYM
	PART_HOLONYM MEMBER_MERONYM SUBSTANCE_MERONYM PART_MERONYM
	ATTRIBUTE ENTAILMENT CAUSE SEE_ALSO VERB_GROUP SIMILAR_TO
	PARTICIPLE PERTAINYM DERIVED_FROM
	These correspond to whatever is used to identify pointers
	of the specified type
	"""
	pass

class WNImpl:
	"""Subclass this class to write your own implementation
	Define the following methods:
		def grabSynset(self, key) - returns a Synset
		def grabKeys(self, form) - returns a list of SynsetKeys
	"""
	ssHash = {}
	def lookupWordSenseByKey(self, key):
		ssKey = key[0]
		wnum = key[1] - 1
		ss = self.lookupSynsetByKey(ssKey)
		if wnum < len(ss.synonyms):
			return ss.synonyms[wnum]
		return None
	def lookupSynsetByKey(self, key):
		if key in self.ssHash:
			 return self.ssHash[key]
		ss = self.grabSynset(key)
		if ss == None:
			 return None
		ss.impl = self
		self.ssHash[key] = ss
		return ss
	def lookupSynsetsByFormAndPOS(self, word, pos):
		f = lambda x, p=pos: x.pos==p or not p
		return filter(f, self.lookupSynsetsByForm(word))
	def lookupSynsetsByForm(self, word):
		words = self.grabBaseForms(word)
		words.append(word)
		keys = []
		for word in words:
			keys += self.grabKeys(word)
		syns = []
		for key in keys:
			syns.append(self.lookupSynsetByKey(key))
		return syns
	def toCanonicalForm(self, word):
		try:
			word = word[:word.index('(')]
		except ValueError:
			pass
		return word.replace(' ', '_')

class WordSense:
	rels = []
	def relations(self, type):
		res = []
		for rl in self.rels:
			if rl[0] == type:
				res.append(self.ss.impl.lookupWordSenseByKey(rl[1]))
		return res

class Synset:
	synonyms = []
	rels = []
	def hypernym(self):
		try:
			return self.relations(Const.HYPERNYM)[0]
		except IndexError:
			return None
	def hyponyms(self):
		return self.relations(Const.HYPONYM)
	def relations(self, type=None):
		res = []
		for rl in self.rels:
			if not type or rl[0] == type:
				res.append(self.impl.lookupSynsetByKey(rl[1]))
		return res
	def __repr__(self):
		return self.__string__()
	def __string__(self):
		res = "("
		for ws in self.synonyms:
			res += ws.form + " "
		res = res[:-1]
		res += ") "
		try:
			res += self.gloss[:self.gloss.index('"')-2]
		except ValueError:
			res += self.gloss
		return res
	   
