#!/usr/bin/python

# tk_gui.py

from __future__ import with_statement

import sys
import os.path
import contextlib

from Tkinter import *
import Pmw
import sqlite3 as db

db_filename = 'python-avr.db'

class App(object):
    def __init__(self):
        self.root = Tk()

        menubar = Menu(self.root)
        menubar.add_command(label="Quit", command=self.root.quit)
        menubar.add_command(label="Edit", command=self.edit)

        self.root.config(menu=menubar)

        vert_pane = Pmw.PanedWidget(self.root, orient='horizontal',
                                    hull_width=1200,
                                    hull_height=900)
        vert_pane.pack(expand=1, fill='both')
        vert_pane.add('list', min=200)
        db_cur.execute("select name, id from word order by name")
        self.words = dict(db_cur)
        self.word_list = Pmw.ScrolledListBox(vert_pane.pane('list'),
                                             items=sorted(self.words.keys()),
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
        word_name = self.cur_word()
        self.selected_word = word(self.words[word_name], word_name, self)

    def run(self):
        self.root.mainloop()

class word(object):
    def __init__(self, id, name, app):
        self.app = app
        self.id = id
        self.word = word
        print "id:", repr(id)
        db_cur.execute("""select kind, defining_word, file_suffix
                          from word
                          where id = ?
                       """, (id,))
        self.kind, self.defining_word, self.file_suffix = db_cur.fetchone()
        self.answers = get_answers(self.id)
        for a in self.answers: a.dump()

class answer(object):
    def __init__(self, id, question_text, text):
        self.id = id
        self.question_text = question_text
        self.text = text
        with contextlib.closing(db_conn.cursor()) as cur:
            cur.execute("""select answer.id,
                                  ifnull(meta.answer, question.answer),
                                  answer.answer
                           from answer inner join answer as question
                             on answer.question_id = question.id
                                left outer join answer as meta
                                on cast(question.answer as int) = meta.id
                           where answer.parent = ?
                           order by question.position, answer.position
                        """, (id,))
            self.children = tuple(map(lambda row: answer(*row), cur))
    def dump(self, indent = 0):
        print ' ' * indent + "%s: %s" % (self.question_text, self.text)
        for child in self.children:
            child.dump(indent + 4)

def get_answers(word_id):
    db_cur.execute("""select answer.id, ifnull(meta.answer, question.answer),
                             answer.answer
                      from answer inner join answer as question
                        on answer.question_id = question.id
                           left outer join answer as meta
                           on cast(question.answer as int) = meta.id
                      where answer.word_id = ? and answer.parent is null
                      order by question.position, answer.position
                   """, (word_id,))
    return tuple(map(lambda row: answer(*row), db_cur))

#w = Entry(???)
#W = Text(???)
#w = Label(root, text="Hello, world!")
#w.pack()



if len(sys.argv) != 2:
    sys.stderr.write("usage: tk_gui directory\n")
    sys.exit(2)

dir = sys.argv[1]

with contextlib.closing(db.connect(os.path.join(dir, db_filename))) as db_conn:
    with contextlib.closing(db_conn.cursor()) as db_cur:
        App().run()

