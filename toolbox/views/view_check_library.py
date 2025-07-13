"""
View for the check library tab
"""

import wx
import wx.dataview

from toolbox.models.id_manager import IdManager


class ViewCheckLibrary(wx.Panel):

    _FIRST_COL_WIDTH = 400
    _GAP = 5

    def __init__(self, parent):
        super().__init__(parent)

        self._tree = wx.dataview.TreeListCtrl(self)
        self._tree.AppendColumn("Checks", self._FIRST_COL_WIDTH)
        self._tree.AppendColumn("Result")

        btn_run_checks = wx.Button(self, IdManager.ID_BTN_CHECK, "Run checks")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._tree, 1, wx.EXPAND | wx.ALL, self._GAP)
        sizer.Add(btn_run_checks, 0, wx.ALL, self._GAP)

        self.SetSizer(sizer)

    ##########
    # Public #
    ##########

    def initialize_tree(self, checker_names):
        self._tree.DeleteAllItems()
        root = self._tree.GetRootItem()
        for name in checker_names:
            self._tree.AppendItem(root, name)

    def add_messages(self, name, messages):
        # Find item with the given name
        item = self._tree.GetFirstItem()
        while item.IsOk():
            if self._tree.GetItemText(item) == name:
                self._tree.SetItemText(item, 1, f"{len(messages)} messages")
                for message in messages:
                    child = self._tree.AppendItem(item, f"{message["item"]}")
                    self._tree.SetItemText(child, 1, f"{message["message"]}")
                break
            item = self._tree.GetNextItem(item)


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
