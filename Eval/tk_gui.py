#!/usr/bin/python

# tk_gui.py

from __future__ import with_statement

import sys
import os.path
import contextlib
import subprocess

from Tkinter import *
import Pmw
import sqlite3 as db

db_filename = 'python-avr.db'

class App(object):
    def __init__(self):
        self.root = Tk()

        menubar = Menu(self.root)
        menubar.add_command(label="New", command=self.new)
        menubar.add_command(label="Save", command=self.save)
        menubar.add_command(label="Edit", command=self.edit)
        menubar.add_command(label="Quit", command=self.root.quit)

        self.root.config(menu=menubar)

        vert_pane = Pmw.PanedWidget(self.root, orient='horizontal',
                                    hull_width=1200,
                                    hull_height=900)
        vert_pane.pack(expand=1, fill='both')
        vert_pane.add('list', min=200)
        db_cur.execute("select name, id from word order by name")
        self.words = dict(db_cur)
        word_list = sorted(self.words.keys())
        print "word_list:", word_list
        self.word_list = Pmw.ScrolledListBox(vert_pane.pane('list'),
                                             items=word_list,
                                             labelpos='nw',
                                             label_text="Words",
                                             selectioncommand=self.select_word,
                                             usehullsize=1)
        self.word_list.pack(expand=1, fill='both')
        self.word_list.setvalue(word_list[0].encode())
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

        self.select_word()

    def new(self):
        self.selected_word = word.new(self)
        self.word_list.setlist(
          sorted((self.selected_word.name,) + self.word_list.get()))
        self.words[self.selected_word.name] = self.selected_word.id
        self.word_list.setvalue(self.selected_word.name)
        self.selected_word.display()

    def edit(self):
        if self.selected_word.filename:
            subprocess.check_call(('gvim', '-f', self.selected_word.filename),
                                  close_fds=True)
            with open(self.selected_word.filename) as f:
                self.selected_word.file_contents = f.read()
            self.word_body.setvalue(self.selected_word.file_contents)

    def save(self):
        self.selected_word.save()

    def cur_word(self):
        return self.word_list.getvalue()[0]

    def select_word(self):
        word_name = self.cur_word()
        self.selected_word = word.from_db(self.words[word_name], self)
        self.selected_word.display()

    def run(self):
        self.root.mainloop()

class word(object):
    def __init__(self, id, name, app, kind, defining_word):
        self.app = app
        self.id = id
        self.name = name
        self.kind = kind
        self.defining_word = defining_word
        db_cur.execute("""select answer 
                          from answer
                          where word_id = ? and question_id = ?
                       """, (kind, filename_suffix_qid))
        filename_suffix = db_cur.fetchone()[0]
        if filename_suffix:
            self.filename = os.path.join(dir, '.'.join((self.name,
                                                        filename_suffix)))
            with open(self.filename) as f:
                self.file_contents = f.read()
        else:
            self.filename = ''

    @classmethod
    def from_db(cls, id, app):
        print "id:", repr(id)
        db_cur.execute("""select name, kind, defining_word
                            from word
                          where id = ?
                       """, (id,))
        name, kind, defining_word = db_cur.fetchone()
        ans = cls(id, name, app, kind, defining_word)
        ans.answers = get_answers(id)
        return ans

    @classmethod
    def new(cls, app):
        db_cur.execute("""select name, id from word where defining_word = 1""")
        kinds = dict(db_cur)
        for kind in sorted(kinds.keys()): print kind
        while True:
            k = raw_input("which kind? ")
            if k in kinds:
                kind = kinds[k]
                defining_word = kind == 1
                break
        name = raw_input("name? ")
        try:
            db_cur.execute("""insert into word (name, kind, defining_word)
                              values (?, ?, ?)
                           """, (name, kind, defining_word))
            print "lastrowid:", db_cur.lastrowid
            id = db_cur.lastrowid
            ans = cls(id, name, app, kind, kind == 1)
            if ans.filename:
                open(ans.filename, 'w').close()
            ans.answers = create_answers(kind, id)
        except Exception:
            db_conn.rollback()
            raise
        db_conn.commit()
        return ans

    def display(self):
        for a in self.answers: a.dump()
        if self.filename:
            self.app.word_body.setvalue(self.file_contents)
        else:
            self.app.word_body.clear()

    def save(self):
        if self.filename:
            self.app.word_body.exportfile(self.filename)
            self.file_contents = self.app.word_body.get()

    def changed(self):
        return self.filename and self.file_contents != self.app.word_body.get()


class answer(object):
    def __init__(self, id, question_text, text):
        self.id = id
        self.question_text = question_text
        self.text = text

    @classmethod
    def new(cls, word_id, question_id, question_text, position):
        db_cur.execute("""insert into answer (question_id, position, word_id,
                                              answer)
                          values (?, ?, ?, '')
                       """, (question_id, position, word_id))
        id = db_cur.lastrowid
        ans = cls(id, question_text, '')
        with contextlib.closing(db_conn.cursor()) as cur:
            cur.execute("""select answer.id,
                                  ifnull(meta.answer, answer.answer),
                                  answer.position
                           from answer left outer join answer as meta
                             on cast(answer.answer as int) = meta.id
                                inner join answer as repeatable
                             on answer.id = repeatable.parent
                           where answer.parent = ? and answer.question_id = 2
                             and repeatable.question_id = 3
                             and repeatable.answer = 'False'
                           order by answer.position
                        """, (question_id,))
            ans.children = tuple(map(lambda row: answer.new(word_id, *row),
                                     cur))
        return ans

    @classmethod
    def from_db(cls, id, question_text, text):
        ans = cls(id, question_text, text)
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
            ans.children = tuple(map(lambda row: answer.from_db(*row), cur))
        return ans

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
    return tuple(map(lambda row: answer.from_db(*row), db_cur))

def create_answers(kind, word_id):
    db_cur.execute("""select answer.id, answer.answer, answer.position
                      from answer inner join answer as repeatable
                        on answer.id = repeatable.parent
                      where answer.question_id = 1 and answer.parent is null
                        and repeatable.question_id = 3
                        and repeatable.answer = 'False'
                      order by answer.position
                   """)
    return tuple(map(lambda row: answer.new(word_id, *row), db_cur))

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
        db_cur.execute("""select id
                          from answer
                          where word_id = 1 and answer = 'filename suffix'
                       """)
        filename_suffix_qid = db_cur.fetchone()[0]
        print "filename_suffix_qid:", filename_suffix_qid
        App().run()

