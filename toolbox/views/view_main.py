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

        self._notebook = wx.Notebook(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._notebook, 1, wx.EXPAND | wx.ALL, self._GAP)
        self.SetSizer(sizer)

        self.SetInitialSize(wx.Size(self._WINDOW_SIZE))

    ##########
    # Public #
    ##########

    def get_notebook(self):
        return self._notebook

    def add_page(self, page_name, page_view):
        self._notebook.AddPage(page_view, page_name)


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
