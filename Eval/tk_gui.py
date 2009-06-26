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
        self.words_by_id = dict(zip(self.words.itervalues(),
                                    self.words.iterkeys()))
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
        self.top_pane = Pmw.ScrolledFrame(horz_pane.pane('top'),
                                          horizflex='elastic',
                                          hscrollmode='none',
                                          labelpos='n',
                                          vertflex='expand',
                                          vertfraction=0.15,
                                          usehullsize=1)
        self.top_pane.pack(expand=1, fill='both')

        horz_pane.add('bottom')
        self.word_body = Pmw.ScrolledText(horz_pane.pane('bottom'),
                                          usehullsize=1)
        self.word_body.pack(expand=1, fill='both')

    def new(self):
        self.selected_word = word.new()
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
        self.selected_word = word.from_db(self.words[word_name])
        self.selected_word.display()

    def run(self):
        self.root.mainloop()

class word(object):
    def __init__(self, id, name, kind, defining_word):
        self.id = id
        self.name = name
        self.kind = kind
        self.kind_name = app.words_by_id[kind]
        self.defining_word = defining_word
        db_cur.execute("""select answer 
                          from answer
                          where word_id = ? and question_id = ?
                       """, (kind, filename_suffix_qid))
        filename_suffix = db_cur.fetchone()[0]
        if filename_suffix:
            self.filename = os.path.join(dir, '.'.join((self.name,
                                                        filename_suffix)))
        else:
            self.filename = ''

    @classmethod
    def from_db(cls, id):
        print "id:", repr(id)
        db_cur.execute("""select name, kind, defining_word
                            from word
                          where id = ?
                       """, (id,))
        name, kind, defining_word = db_cur.fetchone()
        ans = cls(id, name, kind, defining_word)
        if ans.filename:
            with open(ans.filename) as f:
                ans.file_contents = f.read()
        ans.answers = get_answers(id)
        return ans

    @classmethod
    def new(cls):
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
            ans = cls(id, name, kind, kind == 1)
            if ans.filename:
                open(ans.filename, 'w').close()
                ans.file_contents = ''
            ans.answers = create_answers(kind, id)
        except Exception:
            db_conn.rollback()
            raise
        db_conn.commit()
        return ans

    def display(self):
        app.top_pane.configure(label_text="%s %s" % (self.kind_name, self.name))
        answer.display_list(self.answers)
        if self.filename:
            app.word_body.setvalue(self.file_contents)
        else:
            app.word_body.clear()

    def save(self):
        if self.filename:
            app.word_body.exportfile(self.filename)
            self.file_contents = app.word_body.get()

    def changed(self):
        return self.filename and self.file_contents != app.word_body.get()


class answer(object):
    def __init__(self, id, question_id, question_text, text):
        self.id = id
        self.question_id = question_id
        self.question_text = question_text
        self.text = text
        with contextlib.closing(db_conn.cursor()) as cur:
            cur.execute("""select answer from answer
                            where question_id = ? and parent = ?
                        """, (repeatable_qid, question_id,))

    @classmethod
    def new(cls, word_id, question_id, question_text, position):
        with contextlib.closing(db_conn.cursor()) as cur:
            cur.execute("""insert into answer (question_id, position, word_id,
                                               answer)
                           values (?, ?, ?, '')
                        """, (question_id, position, word_id))
            id = db_cur.lastrowid
            ans = cls(id, question_text, '')
            cur.execute("""select answer.id,
                                  ifnull(meta.answer, answer.answer),
                                  answer.position
                           from answer left outer join answer as meta
                             on cast(answer.answer as int) = meta.id
                                inner join answer as repeatable
                             on answer.id = repeatable.parent
                           where answer.parent = ? and answer.question_id = ?
                             and repeatable.question_id = ?
                             and repeatable.answer = 'False'
                           order by answer.position
                        """, (question_id, subquestion_qid, repeatable_qid))
            ans.children = tuple(map(lambda row: answer.new(word_id, *row),
                                     cur))
        return ans

    @classmethod
    def from_db(cls, id, question_id, question_text, text):
        ans = cls(id, question_id, question_text, text)
        with contextlib.closing(db_conn.cursor()) as cur:
            cur.execute("""select answer.id, question.id,
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

    @staticmethod
    def display_list(l, indent = 0, row = 0):
        for a in l[:-1]:
            row = a.display(indent, row, False)
        if l:
            return l[-1].display(indent, row, True)
        else:
            return row

    def display(self, indent, row, last):
        print ' ' * indent + "%s: %s" % (self.question_text, self.text)
        return answer.display_list(self.children, indent + 4, row + 1)

def get_answers(word_id):
    db_cur.execute("""select answer.id,
                             question.id,
                             ifnull(meta.answer, question.answer),
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
                        and repeatable.question_id = ?
                        and repeatable.answer = 'False'
                      order by answer.position
                   """, (repeatable_qid,))
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
        db_cur.execute("""select id, answer
                          from answer
                          where word_id = 1
                          order by id
                       """)
        question_qid = repeatable_qid = subquestion_qid = \
          filename_suffix_qid = None
        for id, question in db_cur:
            print "id:", id, "question:", question
            if question == 'question':
                question_qid = id
            elif question == 'repeatable':
                repeatable_qid = id
            elif question.isdigit() and int(question) == question_qid:
                subquestion_qid = id
            elif question == 'filename suffix':
                filename_suffix_qid = id
        assert question_qid, \
               "failed to find the 'question' compiler question"
        assert repeatable_qid, \
               "failed to find the 'repeatable' compiler question"
        assert subquestion_qid, \
               "failed to find the 'subquestion' compiler question"
        assert filename_suffix_qid, \
               "failed to find the 'filename suffix' compiler question"
        print "question_qid:", question_qid
        print "repeatable_qid:", repeatable_qid
        print "subquestion_qid:", subquestion_qid
        print "filename_suffix_qid:", filename_suffix_qid
        app = App()
        app.select_word()
        app.run()

