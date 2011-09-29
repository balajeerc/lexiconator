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

import os
import sys

from lexi_db import LexiDB
from lexi_query import LexiQuery
from lexi_gui import LexiGUI,LexiGUIDelegate

def import_path(fullpath):
    """ 
    Import a file with full path specification. Allows one to
    import from anywhere, something __import__ does not do. 
    """
    path, filename = os.path.split(fullpath)
    filename, ext = os.path.splitext(filename)
    sys.path.append(path)
    module = __import__(filename)
    reload(module) # Might be out of date
    del sys.path[-1]
    return module
   
def debug():
	path = os.path.abspath("./pydevd/pydevd.py")
	return import_path(path)

"""
LexiApp
Manages the Lexicanator application
"""
class LexiApp(LexiGUIDelegate):	
	def __init__(self):
		self.guiHandler = None
		self.queryHandler = None
		self.dbHandler = None
	
		#The following variables track the current state of application
		self.curr_word = ""
		self.curr_definition = ""
		self.curr_usage = ""
		self.curr_user_rating = 0
		self.curr_search_pattern = "a"
		self.curr_min_rating = 1
		self.curr_max_rating = 10
		self.curr_randomize = False
		self.curr_pattern_offset = -1
		
		#List keeping track of 30 of the last previously used words
		self.prev_word_list = []
		
	def initApplication(self, currPath):
		#First initialise the database handler
		self.dbHandler = LexiDB(currPath)
		self.dbHandler.initDB()
		#Next we initialise the query handler
		self.queryHandler = LexiQuery()
		#Finally we setup the gui hanlder
		self.guiHandler = LexiGUI(self)
		self.guiHandler.initGUI()
		
		self.curr_search_pattern = self.dbHandler.fetchLastWord()
		self.getNextWord()
		self.guiHandler.setWord(self.curr_word,
								self.curr_definition,
								self.curr_usage,
								self.curr_user_rating)				
		self.guiHandler.setMode(self.curr_search_pattern,
								self.curr_min_rating,
								self.curr_max_rating,
								self.curr_randomize)

		self.guiHandler.startLoop()
		
	def getNextWord(self):
		
		#We do a trick here
		#We don't want to display words found in the word list for
		#which there are no definitions in Wiktionary. So, we loop till we
		#get a word with a proper definition. We also set the rating of words
		#without definitions to -1 so that they won't appear the next time we
		#iterate over the words		
		foundDefined = False
		
		while not foundDefined:		
			dbQuery = self.dbHandler.fetchWord(self.curr_search_pattern.lstrip().rstrip(),
											   self.curr_min_rating,
											   self.curr_max_rating,
											   self.curr_pattern_offset)
			
			self.curr_pattern_offset = dbQuery[0]
			self.curr_word = dbQuery[1]
			self.curr_user_rating = dbQuery[2]
			
			word_info = self.queryHandler.queryWordInfo(self.curr_word,"http://lexiconator-server.appspot.com/")
			self.curr_definition = word_info[0]
			self.curr_usage = word_info[1]		
			 
			if self.curr_definition == "":
				#This means that there was no meaning found for this word in Webster's dictionary!
				#This must be one of those unimportant Latin scientific terms, whose rating we 
				#immediately set to 0
				self.dbHandler.updateRating(self.curr_word,0)
				self.curr_user_rating = 0
			else:
				foundDefined = True
				curr_word = self.curr_word.lstrip().rstrip()					
				self.guiHandler.setWord(curr_word,
										self.curr_definition,
										self.curr_usage,
										self.curr_user_rating
										)
				self.dbHandler.updateLastWord(self.curr_word)
				
			#The current pattern offset must be incremented by 1	
			self.curr_pattern_offset = self.curr_pattern_offset + 1
		
	def getPrevWord(self):
		pass
		
	def incWordRating(self):
		self.curr_user_rating = self.curr_user_rating + 1
		self.dbHandler.updateRating(self.curr_word,
									self.curr_user_rating)
		self.guiHandler.setWord(self.curr_word,
								self.curr_definition,
								self.curr_usage,
								self.curr_user_rating
								)							
		
	def decWordRating(self):
		self.curr_user_rating = self.curr_user_rating - 1
		self.dbHandler.updateRating(self.curr_word,
									self.curr_user_rating)
		self.guiHandler.setWord(self.curr_word,
								self.curr_definition,
								self.curr_usage,
								self.curr_user_rating
								)							
	
	def changeMode(self,pattern,minRating,maxRating,randomize):
		if self.curr_search_pattern != pattern or self.curr_min_rating != minRating or self.curr_max_rating != maxRating:
			#TODO: Handle randomization!
			#debug().settrace()
			self.curr_pattern_offset = -1
			self.curr_search_pattern = pattern
			self.curr_min_rating = minRating
			self.curr_max_rating = maxRating
			self.getNextWord()
			self.guiHandler.setWord(self.curr_word,
								self.curr_definition,
								self.curr_usage,
								self.curr_user_rating)