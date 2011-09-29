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

import urwid

"""
LexiGUIDelegate
Delegate class for the GUI's event handling
"""
class LexiGUIDelegate:
    def __init__(self):
        pass

    def getNextWord(self):
        pass

    def getPrevWord(self):
        pass

    def incWordRating(self):
        pass

    def decWordRating(self):
        pass

    def changeMode(self, pattern, minRating, maxRating, randomize):
        pass


"""
LexiGUI
GUI for Lexiconator
"""
class LexiGUI:

    def __init__(self, delegate):
    	
    	#Instead of creating separate variables to store the widgets used,
    	#we use one dictionary that stores all the widgets by key
        self.widget_table = {}
        
        #Main loop for the GUI
        self.main_loop = None
        
        #Indicates if the dialog popup box used to change search pattern is active
        self.dialog_on = False
        
        #Delegate assigned to handle events in the GUI
        self.delegate = delegate
        
        #Indicates if the  definition and usage for current word are being displayed
        self.show_def = False
        self.curr_definition_text = ""
        self.curr_usage_text = ""
        
    def setDelegate(self, delegate):
        """Setter method for assigning the GUI's event delegate

        Keyword Arguments:
        delegate -- event delegate for this GUI (must be subclass of LexiGUIDelegate)\t
        """
        self.delegate = delegate

    def setWord(self, word, definition, usage, rating):
        """Updates the GUI with the new word's record - definition, usage and user rating

        Keyword Arguments:
        word -- new word to update GUI with
        definition -- definition of the new word
        usage -- usage for the new word
        rating -- user rating of the new word \t
        """
        self.widget_table['word_content'].set_text(('body', word.lstrip().rstrip()))
        self.widget_table['rating_value'].set_text(('body', str(rating)))
		
		#When a word change occurrs, we want to ensure that the defintion and usage
		#are hidden till the user presses SPACE
        self.curr_definition_text = definition
        self.curr_usage_text  = usage
        self.show_def = False
    	self.showDefinition()
    	
    def showDefinition(self):
    	"""Shows or hides the current word's definition and usage based on the specified status
    	"""        
    	definition_text_shown = " "
    	usage_text_shown = " "
    	
    	if self.show_def:
    		definition_text_shown = self.curr_definition_text
    		usage_text_shown = self.curr_usage_text
    	
        self.widget_table['definition_content'].set_text(('body', definition_text_shown))
        self.widget_table['usage_content'].set_text(('body', usage_text_shown))
    		    

    def setMode(self, pattern, minRating, maxRating, randomize):
        """Updates the GUI with the specified mode parameters

        Keyword Arguments:
        pattern -- string indicating search pattern
        minRating -- integer minimum rating specified for word
        maxRating -- integer maximum rating specified for word search
        randomize -- boolean indicating whether the search must be random \t
        """
        self.widget_table['search_pattern'].set_edit_text(pattern)
        self.widget_table['min_rating'].set_edit_text(str(minRating))
        self.widget_table['max_rating'].set_edit_text(str(maxRating))

    def initGUI(self):
        """Initialises the GUI with our widget layout
        """
        
        #Palettes define the styles used to display the various widgets and the text
        #contained within
        self.widget_table['palette'] = [('heading', 'black,bold', 'dark cyan', 'standout'),
         ('body', 'black', 'dark cyan', 'standout'),
         ('foot', 'light gray', 'black'),
         ('key', 'light cyan', 'black', 'underline'),
         ('title', 'white', 'black'),
         ('editbx', 'black', 'dark cyan'),
         ('editcp', 'black,bold', 'dark cyan', 'standout'),
         ('dialog_body', 'dark cyan,bold', 'black', 'standout'),
         ('dialog_heading', 'dark cyan', 'black', 'standout')]

        footer_text = [('title', 'Lexicanator'),' ',
                       ('key', 'ESC'),':exits, ',
                       ('key', 'TAB'), ':search, ',
                       ('key', 'SPACE'), ':show/hide, ',
                       ('key', 'LEFT'),':next-word, ',
                       ('key', 'RIGHT'),':prev-word, ',
                       ('key', 'UP'),':rate-up, ',
                       ('key', 'DOWN'),':rate-down ',
                      ]
                       
        dialog_header_text = [('title', 'Change Mode')]
        dialog_footer_text = [('title', 'Enter to Apply Changes')]
        
        blank = urwid.Divider()
        
        #Layout of the main content area
        self.widget_table['word_heading'] = urwid.Text(('heading', 'Word: '))
        self.widget_table['word_content'] = urwid.Text(('body', 'Word content comes here'))
        self.widget_table['word_content_pad'] = (urwid.Padding(self.widget_table['word_content'], ('fixed left', 2), ('fixed right', 2), 20),)
        self.widget_table['definition_heading'] = urwid.Text(('heading', 'Definition:'))
        self.widget_table['definition_content'] = urwid.Text(('body', ''))
        self.widget_table['usage_heading'] = urwid.Text(('heading', 'Usage:'))
        self.widget_table['usage_content'] = urwid.Text(('body', ''))
        self.widget_table['rating_heading'] = urwid.Text(('heading', 'Rating:'))
        self.widget_table['rating_value'] = urwid.Text(('body', 'Rating value comes here'))        
        main_content_list = [blank,
                             self.widget_table['word_heading'],
                             blank,
                             urwid.Padding(self.widget_table['word_content'],
                                          ('fixed left',2),
										  ('fixed right',2), 
										  20),
                             blank,
                             self.widget_table['definition_heading'],
                             blank,
                             urwid.Padding(self.widget_table['definition_content'],
										  ('fixed left',2),
										  ('fixed right',2), 
										  20),										
                             blank,
                             self.widget_table['usage_heading'],
                             blank,
                             urwid.Padding(self.widget_table['usage_content'],
										  ('fixed left',2),
										  ('fixed right',2), 
										  20),										
                             blank,
                             self.widget_table['rating_heading'],
                             blank,
                             self.widget_table['rating_value']]

        #Layout of the popup dialog
        self.widget_table['search_pattern'] = urwid.Edit('Enter search pattern: ', '(blank)', multiline=False, align='center')
        self.widget_table['search_pattern_formatted'] = urwid.AttrMap(self.widget_table['search_pattern'], 'dialog_heading', 'dialog_heading')
        self.widget_table['max_rating'] = urwid.IntEdit(('editcp', 'Max rating: '), 5)
        self.widget_table['max_rating_formatted'] = urwid.AttrWrap(self.widget_table['max_rating'], 'dialog_heading', 'dialog_heading')
        self.widget_table['min_rating'] = urwid.IntEdit(('editcp', 'Min rating: '), 5)
        self.widget_table['min_rating_formatted'] = urwid.AttrWrap(self.widget_table['min_rating'], 'dialog_heading', 'dialog_heading')
        self.widget_table['randomize'] = urwid.CheckBox('Randomize')
        self.widget_table['randomize_formatted'] = urwid.AttrWrap(self.widget_table['randomize'], 'dialog_heading', 'dialog_heading')
        self.widget_table['footer'] = urwid.AttrMap(urwid.Text(footer_text), 'foot')
        self.widget_table['dialog_header'] = urwid.AttrMap(urwid.Text(dialog_header_text, align='center'), 'foot')
        self.widget_table['dialog_footer'] = urwid.AttrMap(urwid.Text(dialog_footer_text, align='center'), 'foot')                             
        dialog_content_list = [blank,
                               self.widget_table['search_pattern_formatted'],
                               blank,
                               self.widget_table['min_rating_formatted'],
                               blank,
							   self.widget_table['max_rating_formatted'],
							   blank,
                               self.widget_table['randomize_formatted'],
                               blank]
                               
        self.widget_table['main_content'] = urwid.ListBox(urwid.SimpleListWalker(main_content_list))
        self.widget_table['dialog_content'] = urwid.ListBox(urwid.SimpleListWalker(dialog_content_list))
        self.widget_table['main_frame'] = urwid.Frame(urwid.AttrMap(self.widget_table['main_content'], 'body'), footer=self.widget_table['footer'])
        self.widget_table['dialog_frame'] = urwid.Frame(urwid.AttrMap(self.widget_table['dialog_content'], 'dialog_body'), header=self.widget_table['dialog_header'], footer=self.widget_table['dialog_footer'])
        self.widget_table['main_overlay'] = urwid.Overlay(self.widget_table['dialog_frame'], self.widget_table['main_frame'], 'center', ('relative', 35), 'middle', ('relative', 25))

    def startLoop(self):
        self.main_loop = urwid.MainLoop(self.widget_table['main_frame'], self.widget_table['palette'], unhandled_input=self.handleInput)
        self.main_loop.run()

    def handleInput(self, input):
    	"""Input handler for the GUI. Note that this is only an entry point for the
    	event handling. This method in turn calls various methods on its assigned delegate
    	
		Keyword Arguments:
		input -- the key that initiated the event    	
        """
        if input == 'esc':
            raise urwid.ExitMainLoop()
        if input == 'tab':
            if self.dialog_on:
                self.main_loop.widget = self.widget_table['main_frame']
                self.dialog_on = False
            else:
                self.main_loop.widget = self.widget_table['main_overlay']
                self.dialog_on = True
        if input == 'enter':
            if self.dialog_on:
                self.main_loop.widget = self.widget_table['main_frame']
                self.dialog_on = False
                new_search_pattern = self.widget_table['search_pattern'].get_edit_text()
                new_max_rating = int(self.widget_table['max_rating'].get_edit_text())
                new_min_rating = int(self.widget_table['min_rating'].get_edit_text())
                new_randomize = self.widget_table['randomize'].get_state()
                self.delegate.changeMode(new_search_pattern, new_min_rating, new_max_rating, new_randomize)
        elif input == 'up':
            if not self.dialog_on:
                self.delegate.incWordRating()
        elif input == 'down':
            if not self.dialog_on:
                self.delegate.decWordRating()
        elif input == 'left':
            if not self.dialog_on:
                self.delegate.getPrevWord()
        elif input == 'right':
            if not self.dialog_on:
                self.delegate.getNextWord()
        elif input == ' ':            
            if not self.dialog_on:
            	#print("Showing definition!")
                self.show_def = not self.show_def 
                self.showDefinition()        
