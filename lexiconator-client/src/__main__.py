#!/usr/bin/python
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
				 
def main(argv):
	import lexi_app
	path = os.path.split(lexi_app.__file__)[0]
	app = lexi_app.LexiApp()
	app.initApplication(path)
	return 0 # exit errorlessly
    		
if __name__=="__main__": 
	sys.exit(main(sys.argv))