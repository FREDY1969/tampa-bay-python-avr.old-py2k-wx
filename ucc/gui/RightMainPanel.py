# RightMainPanel.py

r'''
'''

import wx, wx.py
import wx.lib.scrolledpanel as scrolled

from ucc.gui.Registry import Registry
from ucc.gui import controls

class RightMainPanel(wx.Panel):
    def __init__(self, parent, id, style):
        wx.Panel.__init__(self, parent, id, style=style)

        # setup splitter

        splitter = self.splitter = \
          wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_LIVE_UPDATE)

        # setup panels

        topPanel = self.topPanel = \
          scrolled.ScrolledPanel(splitter, wx.ID_ANY, style=wx.BORDER_SUNKEN)
        topSizer = self.topSizer = wx.BoxSizer(wx.VERTICAL)
        topPanel.SetSizer(topSizer)
        #topPanel.SetAutoLayout(1)
        topPanel.SetupScrolling()
        bottomText = self.bottomText = \
          wx.py.editwindow.EditWindow(splitter, wx.ID_ANY,
                                      style=wx.TE_MULTILINE | wx.BORDER_SUNKEN)
        self.bottomText.setDisplayLineNumbers(True)

        # setup sizer

        sizer = wx.BoxSizer(wx.VERTICAL)

        # add top and bottom stuff

        splitter.SetMinimumPaneSize(200)
        splitter.SetSashGravity(0.0)
        splitter.SplitHorizontally(topPanel, bottomText,
          Registry.config.getint('gui', 'question-panel-height'))
        print "height", Registry.config.getint('gui', 'question-panel-height')

        print "RightMainPanel height", self.GetClientSize().GetHeight()

        sizer.Add(splitter, 1, wx.EXPAND)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Fit()
        print "RightMainPanel height", self.GetClientSize().GetHeight()

        self.test = None


    def paint(self):
        print "painting rightMainPanel"
        self.buildWord()

    def buildWord(self):

        # setup controls

        self.topSizer.Clear(True)

        if Registry.currentWord:
            for question in Registry.parentWord.questions or ():
                if not hasattr(question, 'control'):
                    msg = "<%s %s> has not 'control'" % \
                            (question.__class__.__name__, question.name)
                    print msg
                    self.topSizer.Add(wx.StaticText(self.topPanel, wx.ID_ANY,
                                                    msg))
                else:
                    cls = getattr(getattr(controls, question.control),
                                  question.control)
                    print question.control, cls
                    self.topSizer.Add(cls(self.topPanel,
                                          question,
                                          Registry.currentWord.get_answer(
                                            question.name),
                                          question.label))

        self.topSizer.Layout()

        # bottom text

        self.bottomText.ClearAll()
        if Registry.currentWordPath:
            self.bottomText.LoadFile(Registry.currentWordPath)

