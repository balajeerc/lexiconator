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
import sqlite3

class LexiDB():
	
	def __init__(self,currPath):
		self.curr_path = currPath
	
	def initDB(self):
		"""Initialises the database"""		
		#Connect to an existing file named words.db or create a new one
		conn = sqlite3.connect(os.path.join(self.curr_path,'words.db'))		
		#Get the cursor
		c = conn.cursor()		
		# Create table if it doesnt exist already
		c.execute('''CREATE TABLE IF NOT EXISTS 
					Words(Id INTEGER PRIMARY KEY, Word TEXT, UserRating INTEGER)''')	
		c.execute("""SELECT * FROM Words""")		
		rowCount = 0
		for each_row in c:
			rowCount = rowCount+1
			break			
		if rowCount <= 0:
			#This means that the list of words from the text file has not been 
			#entered into the database. We proceed to do just that.
			f = open(os.path.join(self.curr_path,'wordlist.txt'), 'r')
			i = 1
			for each_word in f:
				#Give each word a default initial rating of 5
				t = (i,each_word,5)
				c.execute('INSERT INTO Words VALUES (?,?,?)', t)
				i = i+1		
		#Commit the changes
		conn.commit()		
		#Close the open database connection
		conn.close()
	
	def fetchWord(self, searchPattern, minRating, maxRating, searchOffset=-1):
		"""Retrieves a list of records from the database using the search pattern and rating range
		specified. This fetch operation supports two modes. The first is where search offset is -1. In this 
		case, the word fetched is based on the search pattern itself. Instead, if searchOffset is a positive
		number, we simply fetch the word at that index from the dictionary (a faster query).
		Returns a tuple of the form (index, word, user_rating)
		
		Keyword arguments:
		searchPattern -- a text string indicating the sequence of letters the word should start with
		minRating -- minimum rating for the specified word
		maxRating -- maximum rating for the specified word
		searchOffset -- offset in the query result set. Set this to -1 to get search for word by pattern
						set this to a positive number, say 2, the word by its index in the word list database
		"""
		#Connect to an existing file named words.db or create a new one
		conn = sqlite3.connect(os.path.join(self.curr_path,'words.db'))		
		#Get the cursor
		c = conn.cursor()
		
		if searchOffset == -1:				
			#Setup the pattern
			t = (searchPattern+"%",minRating,maxRating,)
			c.execute("""SELECT * FROM Words WHERE
						 Word LIKE ? AND
						 UserRating >= ? AND
						 UserRating <= ?
						 ORDER BY Id
						 LIMIT 1""",
						 t)
		else:
			t = (searchOffset,minRating,maxRating,)
			c.execute("""SELECT * FROM Words WHERE
						 Id >= ? AND
						 UserRating >= ? AND
						 UserRating <= ?
						 ORDER BY Id
						 LIMIT 1""",
						 t)

		result = None
		for each_row in c:			
			result = each_row
			break
			
		if not result:
			#No word was found matching query
			result = (-1,"","")
			
		#Close the open database connection
		conn.close()		
		#Return the results		
		return result	
	
	def updateRating(self,word,newRating):
		"""Updates the rating of a specified word.
		
		Keyword Parameters:
		word -- word whose rating needs to be updated
		newRating -- new rating of this word
		"""
		#Connect to an existing file named words.db or create a new one
		conn = sqlite3.connect(os.path.join(self.curr_path,'words.db'))		
		#Get the cursor
		c = conn.cursor()		
		#Setup the pattern
		t = (newRating,word,)
		c.execute("""UPDATE Words
					 SET UserRating = ? WHERE
					 Word = ?""",
					 t)
		#Commit the changes
		conn.commit()
		#Close the connection
		conn.close()

		