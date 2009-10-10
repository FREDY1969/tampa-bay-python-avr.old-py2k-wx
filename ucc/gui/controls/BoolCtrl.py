r'''Control for boolean word values'''

import wx

class BoolCtrl(wx.Window):
    def __init__(self, parent, question, label):
        wx.Window.__init__(self, parent)
        
        self.parent = parent
        self.question = question
        self.label = label
        
        self.value = None # question.value
        self.paintControl()
    
    def paintControl(self):
        wx.CheckBox(self, wx.ID_ANY, self.label)
    
    def getValue(self):
        return self.value
