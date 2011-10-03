#! /usr/bin/env python

from Tkinter import *
from string import atoi

class SearchFrame(Frame):
	def event(self, event):
		self.formSelected()
		
	def formSelected(self):
		form = self.formEntry.get()
		if not len(form):
			return
		syns = impl.lookupSynsetsByFormAndPOS(form, self.pos)
		self.display.type = None
		self.display.setSynsets(syns)

	pos = None
	def setPOSAny(self):
		self.pos = None;
		self.posMenu.config(text='Any')
	def setPOSNoun(self):
		self.pos = 'n';
		self.posMenu.config(text='Noun')
	def setPOSVerb(self):
		self.pos = 'v';
		self.posMenu.config(text='Verb')
	def setPOSAdj(self):
		self.pos = 'a';
		self.posMenu.config(text='Adj')
	def setPOSAdv(self):
		self.pos = 'r';
		self.posMenu.config(text='Adv')

	def createPOSMenu(self):
		posMenuButton = Menubutton(self, text='POS', underline=0)
		posMenuButton.menu = Menu(posMenuButton)
		menu = posMenuButton.menu
		menu.add_command(label='Any', command=self.setPOSAny)
		menu.add_command(label='Noun', command=self.setPOSNoun)
		menu.add_command(label='Verb', command=self.setPOSVerb)
		menu.add_command(label='Adj', command=self.setPOSAdj)
		menu.add_command(label='Adv', command=self.setPOSAdv)
		posMenuButton['menu'] = menu
		return posMenuButton
		
	def createWidgets(self):
		Label(self, text='Form:').pack(side=LEFT)

		self.formEntry = Entry(self)
		self.formEntry.bind('<Key-Return>', self.event)
		self.formEntry.pack(side=LEFT)

		self.posMenu = self.createPOSMenu()
		self.posMenu.pack(side=LEFT)
		
		self.formButton = Button(self, text='Search',
								 command=self.formSelected)
		self.formButton.pack(side=RIGHT)
		
	def __init__(self, master):
		Frame.__init__(self, master)
		Pack.config(self)
		self.createWidgets()

class DisplayFrame(Frame):
	def setSynsets(self, syns):
		self.syns = syns
		self.ssIndex = -1
		self.next()

	def prev(self):
		if len(self.syns):
			self.ssIndex -= 1
			self.ssLabel.config(text=self.syns[self.ssIndex])
			self.displayRelations(self.syns[self.ssIndex])
			if self.ssIndex >= len(self.syns) - 1:
				self.nextButton.config(state=DISABLED)
			else:
				self.nextButton.config(state=ACTIVE)
			if self.ssIndex == 0:
				self.prevButton.config(state=DISABLED)
			else:
				self.prevButton.config(state=ACTIVE)
		else:
			self.nextButton.config(state=DISABLED)
			self.prevButton.config(state=DISABLED)
			
	def next(self):
		if len(self.syns):
			self.ssIndex += 1
			self.ssLabel.config(text=self.syns[self.ssIndex])
			self.displayRelations(self.syns[self.ssIndex])
			if self.ssIndex >= len(self.syns) - 1:
				self.nextButton.config(state=DISABLED)
			else:
				self.nextButton.config(state=ACTIVE)
			if self.ssIndex == 0:
				self.prevButton.config(state=DISABLED)
			else:
				self.prevButton.config(state=ACTIVE)
		else:
			self.nextButton.config(state=DISABLED)
			self.prevButton.config(state=DISABLED)

	def displayRelations(self, ss):
		self.relList.delete(0, END)
		relations = ss.relations()
		for i in range(len(relations)):
			rel = relations[i]
			type = self.type
			if not type:
				type = ss.rels[i][0]
			self.relList.insert(END, type+' '+repr(rel))

	def relSelected(self, event):
		items = self.relList.curselection()
		if len(items):
			index = atoi(items[0])
			relations = self.syns[self.ssIndex].relations(self.type)
			self.setSynsets([relations[index]])
	
	def createWidgets(self):
		showframe = Frame(self)
		Pack.config(showframe)
		showframe.pack(side=TOP, anchor="w")
		self.prevButton = Button(showframe, text='Prev', state=DISABLED,
								 anchor="n", command=self.prev)
		self.prevButton.pack(side=LEFT, anchor="w")
		self.nextButton = Button(showframe, text='Next', state=DISABLED,
								 anchor="n", command=self.next)
		self.nextButton.pack(side=LEFT, anchor="w")
		self.ssLabel = Label(showframe, anchor="nw", justify=LEFT, width=60,
							 wraplength=420, height=4)
		self.ssLabel.pack(side=LEFT)

		scroll = Scrollbar(self)
		scroll.pack(side=RIGHT, fill=Y)

		self.relList = Listbox(self, width = 80, height = 15,
							   yscrollcommand=scroll.set)
		self.relList.bind('<Key-Return>', self.relSelected)
		self.relList.bind('<Double-Button-1>', self.relSelected)
		self.relList.pack(side=BOTTOM)

		scroll.config(command=self.relList.yview)
		
	def __init__(self, master):
		self.type = None
		Frame.__init__(self, master)
		Pack.config(self)
		self.createWidgets()

class PywnShowFrame(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		Pack.config(self)
		self.search = SearchFrame(self)
		self.search.pack(side=TOP, anchor="w")
		self.display = DisplayFrame(self)
		self.display.pack(side=BOTTOM, fill=BOTH)
		self.search.display = self.display

from stdwn import impl
from stdwn import close

if __name__ == '__main__':
	import sys
	impl.open()#sys.argv[1],int(sys.argv[2]))
	root = Tk()
	pywnframe = PywnShowFrame(root)
	root.title('PywnShow - WordNet')
	root.mainloop()
	close()
