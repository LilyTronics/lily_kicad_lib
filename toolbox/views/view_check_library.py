"""
View for the check library tab
"""

import wx
import wx.dataview


class ViewCheckLibrary(wx.Panel):

    _GAP = 5

    def __init__(self, parent):
        super().__init__(parent)

        self._tree = wx.dataview.TreeListCtrl(self, wx.ID_ANY)
        self._tree.AppendColumn("Check")
        self._tree.AppendColumn("Result")

        btn_run_checks = wx.Button(self, wx.ID_ANY, "Run checks")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._tree, 1, wx.EXPAND | wx.ALL, self._GAP)
        sizer.Add(btn_run_checks, 0, wx.ALL, self._GAP)

        self.SetSizer(sizer)


if __name__ == "__main__":

    from toolbox.toolbox import run_toolbox

    run_toolbox()
