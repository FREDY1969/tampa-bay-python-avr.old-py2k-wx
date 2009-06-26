#!/usr/bin/python

# tk_gui.py

from Tkinter import *
import Pmw
import sqlite3 as db

class App(object):
    def __init__(self):
        self.root = Tk()

        menubar = Menu(self.root)
        menubar.add_command(label="Edit", command=self.edit)
        menubar.add_command(label="Quit", command=self.root.quit)

        self.root.config(menu=menubar)

        vert_pane = Pmw.PanedWidget(self.root, orient='horizontal',
                                    hull_width=1200,
                                    hull_height=900)
        vert_pane.pack(expand=1, fill='both')
        vert_pane.add('list', min=200)
        self.word_list = Pmw.ScrolledListBox(vert_pane.pane('list'),
                                             items=('agitate', 'fill', 'spin'),
                                             labelpos='nw',
                                             label_text="Words",
                                             selectioncommand=self.select_word,
                                             usehullsize=1)
        self.word_list.pack(expand=1, fill='both')
        vert_pane.add('word-view')

        horz_pane = Pmw.PanedWidget(vert_pane.pane('word-view'),
                                    orient='vertical')
        horz_pane.pack(expand=1, fill='both')
        horz_pane.add('top', min=200)
        self.top_pane = horz_pane.pane('top')
        horz_pane.add('bottom')
        self.word_body = Pmw.ScrolledText(horz_pane.pane('bottom'),
                                          usehullsize=1)
        self.word_body.pack(expand=1, fill='both')

        #Button(frame, text="Hello", command=self.say_hi).pack(side=LEFT)

    def edit(self):
        print "edit called"

    def cur_word(self):
        return self.word_list.getvalue()[0]

    def select_word(self):
        print "select_word:", self.cur_word()

    def run(self):
        self.root.mainloop()

#w = Entry(???)
#W = Text(???)
#w = Label(root, text="Hello, world!")
#w.pack()

App().run()

