"""
Panel with controls for the power supply
"""

import wx
import wx.dataview

import toolbox.tools.common.gui_sizes as GuiSizes


class Panel(wx.Panel):

    ID_BTN_CHECK = wx.NewIdRef()

    _FIRST_COL_WIDTH = 400


    def __init__(self, parent):
        super().__init__(parent)

        self._tree = wx.dataview.TreeListCtrl(self)
        self._tree.AppendColumn('Checks', self._FIRST_COL_WIDTH)
        self._tree.AppendColumn('Result')

        btn_run_checks = wx.Button(self, self.ID_BTN_CHECK, 'Run checks')

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._tree, 1, wx.EXPAND | wx.ALL, GuiSizes.BOX_SPACING)
        sizer.Add(btn_run_checks, 0, wx.ALL, GuiSizes.BOX_SPACING)

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
                self._tree.SetItemText(item, 1, f'{len(messages)} messages')
                if len(messages) > 0:
                    for message in messages:
                        child = self._tree.AppendItem(item, f'{message['item']}')
                        self._tree.SetItemText(child, 1, f'{message['message']}')
                    self._tree.Expand(item)
                else:
                    self._tree.Collapse(item)
                break
            item = self._tree.GetNextItem(item)


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.check_library.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
