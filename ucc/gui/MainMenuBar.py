'''
'''

import setpath
setpath.setpath(__file__)

import wx
from ucc.gui.Registry import Registry

class MainMenuBar(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self)
        self.parent = parent
        
        # setup menu
        
        filemenu = wx.Menu()
        filemenu.Append(Registry.ID_OPEN, "&Open Package\tCtrl+O", u"Open a \xb5CC package")
        filemenu.Append(Registry.ID_SAVE_WORD, "&Save Word\tCtrl+S", "Save the Current Word")
        filemenu.AppendSeparator()
        filemenu.Append(Registry.ID_EXIT, "E&xit", u"Terminate \xb5CC Package Editor.")
        
        helpmenu = wx.Menu()
        helpmenu.Append(Registry.ID_ABOUT, "&About")
        
        self.Append(filemenu, "&File")
        self.Append(helpmenu, "&Help")
        
        self.setupEventHandlers()
        
    def setupEventHandlers(self):
        wx.EVT_MENU(self.parent, Registry.ID_OPEN, Registry.app.onOpen)
        wx.EVT_MENU(self.parent, Registry.ID_EXIT, Registry.app.onExit)
        wx.EVT_MENU(self.parent, Registry.ID_ABOUT, Registry.app.onAbout)