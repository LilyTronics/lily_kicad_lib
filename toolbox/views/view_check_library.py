"""
View for the check library tab
"""

import wx
import wx.dataview

from toolbox.models.id_manager import IdManager


class ViewCheckLibrary(wx.Panel):

    _GAP = 5

    def __init__(self, parent):
        super().__init__(parent)

        self._tree = wx.dataview.TreeListCtrl(self)
        self._tree.AppendColumn("Checks")
        self._tree.AppendColumn("Result")

        btn_run_checks = wx.Button(self, IdManager.ID_BTN_CHECK, "Run checks")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._tree, 1, wx.EXPAND | wx.ALL, self._GAP)
        sizer.Add(btn_run_checks, 0, wx.ALL, self._GAP)

        self.SetSizer(sizer)

    ##########
    # Public #
    ##########

    def initialize_tree(self, checks):
        self._tree.DeleteAllItems()
        root = self._tree.GetRootItem()
        for check in checks:
            self._tree.AppendItem(root, check)
            # self._tree.SetItemText(child, 1, "2 messages")
            # for i in range(2):
            #     msg = self._tree.AppendItem(child, f"Line {i}")
            #     self._tree.SetItemText(msg, 1, f"This is message {i}")


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
