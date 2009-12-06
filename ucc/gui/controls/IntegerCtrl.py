r'''Control for integer word values'''

import wx
from ucc.gui.controls.BaseCtrl import BaseCtrl

class IntegerCtrl(BaseCtrl):
    def init2(self):
        self.sc = wx.SpinCtrl(self, -1, name=self.question.name, pos=(20,0))
        self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.sc)

    def setInitialValue(self):
        self.sc.SetValue(self.answer_getter().get_value())
    
    def OnSpin(self, event):
        self.answer_getter().value = str(self.sc.GetValue())
    
