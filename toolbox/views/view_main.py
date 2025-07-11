"""
Main view for the toolbox
"""

import wx
import wx.dataview


class ViewMain(wx.Dialog):

    _WINDOW_TITLE = "KiCad Toolbox"
    _WINDOW_SIZE = (1000, 800)
    _GAP = 5

    def __init__(self):
        super().__init__(None, title=self._WINDOW_TITLE)

        notebook = wx.Notebook(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, self._GAP)
        self.SetSizer(sizer)

        self.SetInitialSize(wx.Size(self._WINDOW_SIZE))


if __name__ == "__main__":

    from toolbox.toolbox import run_toolbox

    run_toolbox()
