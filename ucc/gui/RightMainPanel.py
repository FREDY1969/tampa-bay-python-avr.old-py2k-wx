# RightMainPanel.py

r'''
'''

import os
import wx, wx.py
import wx.lib.scrolledpanel as scrolled

from ucc.gui import Registry
from ucc.gui import controls
from ucc.gui import debug

class RightMainPanel(wx.Panel):
    def __init__(self, parent, id, style):
        super(RightMainPanel, self).__init__(parent, id, style=style)
        
        # setup splitter
        
        splitter = self.splitter = \
          wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_LIVE_UPDATE)
        
        # setup panels
        
        topPanel = self.topPanel = \
          scrolled.ScrolledPanel(splitter, wx.ID_ANY, style=wx.BORDER_SUNKEN)
        topSizer = self.topSizer = wx.FlexGridSizer(cols=2, hgap=2, vgap=2)
        topSizer.SetFlexibleDirection(wx.HORIZONTAL)
        topSizer.AddGrowableCol(1, 1)
        topPanel.SetSizer(topSizer)
        topPanel.SetupScrolling(scroll_x = False)
        bottomText = self.bottomText = \
          wx.py.editwindow.EditWindow(splitter, wx.ID_ANY,
                                      style=wx.TE_MULTILINE|wx.BORDER_SUNKEN)
        bottomText.setDisplayLineNumbers(True)
        
        # setup sizer
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # add top and bottom stuff
        
        splitter.SetMinimumPaneSize(200)
        splitter.SetSashGravity(0.0)
        splitter.SplitHorizontally(topPanel, bottomText,
          Registry.config.getint('gui', 'question-panel-height'))
        debug.trace("Height configuration value: %s" %
                    Registry.config.getint('gui', 'question-panel-height'))
        
        sizer.Add(splitter, 1, wx.EXPAND)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Fit()
        
        debug.trace("RightMainPanel height: %s" %
                    self.GetClientSize().GetHeight())
        
    
    def paint(self):
        debug.trace("Painting rightMainPanel")
        self.buildWord()
    
    def buildWord(self):
        debug.trace("RightMainPanel.buildWord")
        self.topSizer.Clear(True)
        
        # setup word controls
        
        if Registry.currentWord:
            for question in Registry.currentWord.kind_obj.questions or ():
                self.topSizer.Add(
                    wx.StaticText(self.topPanel, wx.ID_ANY, question.label))
                if not hasattr(question, 'control'):
                    msg = "<%s %s> has no control" % \
                            (question.__class__.__name__, question.name)
                    debug.warn(msg)
                    self.topSizer.Add(wx.StaticText(self.topPanel, wx.ID_ANY,
                                                    msg))
                else:
                    cls = getattr(getattr(controls, question.control),
                                  question.control)
                    debug.trace('%s is being renderd as %s' % (question.name, cls.__name__))
                    self.topSizer.Add(cls.makeControl(
                        self.topPanel,
                        question,
                        lambda question=question:
                            Registry.currentWord.get_answer(question.name),
                        lambda new_ans, question=question:
                            Registry.currentWord.set_answer(question.name,
                                                            new_ans)))
        else:
            debug.notice('No word currently selected')
        
        self.topSizer.Layout()
        
        # bottom text
        
        self.bottomText.ClearAll()
        if Registry.currentWord:
            source_filename = Registry.currentWord.get_filename()
            if source_filename and os.path.exists(source_filename):
                self.bottomText.LoadFile(source_filename)

