#
# 	Lexiconator - A Free Word Learning Aid, like Flash Cards
#	Copyright (C) 2011 Balajee.R.C 
#
#	This library is free software; you can redistribute it and/or
#	modify it under the terms of the GNU Lesser General Public
#	License as published by the Free Software Foundation; either
#	version 3 of the License, or (at your option) any later version.
#
#	This library is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#	Lesser General Public License for more details.
#
#	You should have received a copy of the GNU Lesser General Public
#	License along with this library; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Lexicanator web site: http://www.balajeerc.info/lexicanator

import json
import urllib2
import os
import sys

class LexiQuery():
	def __init__(self, srcPath):
		self.srcPath = srcPath
		pywn_path = os.path.join(srcPath,"pywn")
		sys.path.append(pywn_path)
		os.environ['WNDICT'] = os.path.join(pywn_path,'dict')
		from stdwn import impl
		self.impl = impl
		
	def queryWordInfo(self,word,url="http://localhost:8080"):
		"""Queries the Google app engine server for the definition and usage of specified
		word and returns the result as a tuple pf the form: (definition, usage).
		
		Keyword Parameters:
		word -- word to query the wordnik database for
		"""
		word = word.rstrip()
		word = word.lstrip()
		query_url = url + "?word=" + word
		
		try:
			query_result = urllib2.urlopen(query_url)
			result_json = query_result.read()
			result_list = json.loads(result_json)
			return (result_list[0],result_list[1])
		
		except urllib2.URLError:
			#This would happen if there is no access to the internet
			#In such a case query the result from local wordnet database
			synsets = self.impl.lookupSynsetsByForm(word)
			definition_string = ""
			for i in range(len(synsets)):
				definition_string = definition_string + str(i+1) + "." + synsets[i].gloss + "\n" 
			
			return (definition_string,"")	
#def main():
#	queryHandler = LexiQuery()
#	print queryHandler.queryWordInfo("aa")
#	
#		
#if __name__=="__main__": 
#	main()		