"""
Main view for the toolbox
"""

import wx
import wx.dataview


class ViewMain(wx.Dialog):

    _WINDOW_TITLE = "KiCad Toolbox"
    _WINDOW_SIZE = (1200, 800)
    _GAP = 5

    def __init__(self):
        super().__init__(None, title=self._WINDOW_TITLE)

        self._notebook = wx.Notebook(self)
        self._txt_console = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_READONLY)
        self._txt_console.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._notebook, 2, wx.EXPAND | wx.ALL, self._GAP)
        sizer.Add(self._txt_console, 1, wx.EXPAND | wx.ALL, self._GAP)
        self.SetSizer(sizer)

        self.SetInitialSize(wx.Size(self._WINDOW_SIZE))

    ##########
    # Public #
    ##########

    def get_notebook(self):
        return self._notebook

    def add_page(self, page_name, page_view):
        self._notebook.AddPage(page_view, page_name)

    def add_to_console(self, message):
        self._txt_console.AppendText(f"{message}\n")


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
