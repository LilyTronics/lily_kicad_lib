"""
Panel with controls for the power supply
"""

import wx
import wx.lib.filebrowsebutton as filebrowse

import toolbox.tools.common.gui_sizes as GuiSizes


class Panel(wx.Panel):

    ID_BTN_CHECK = wx.NewIdRef()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._txt_messages = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_READONLY
        )
        self._txt_messages.SetFont(
            wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        )

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self._create_controls(), 0, wx.EXPAND | wx.ALL, GuiSizes.BOX_SPACING)
        box.Add(self._txt_messages, 1, wx.EXPAND | wx.ALL, GuiSizes.BOX_SPACING)

        self.SetSizer(box)

    ###########
    # Private #
    ###########

    def _create_controls(self):
        lbl_file = wx.StaticText(self, wx.ID_ANY, 'Design file:')
        self._btn_file = filebrowse.FileBrowseButton(self, labelText='', fileMask='*.kicad_pro')
        btn_check = wx.Button(self, self.ID_BTN_CHECK, 'Check design')

        grid = wx.GridBagSizer(*GuiSizes.GRID_SPACING)
        grid.Add(lbl_file, (0, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._btn_file, (0, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        grid.Add(btn_check, (1, 0), (1, 2))

        grid.AddGrowableCol(1)

        return grid

    ##########
    # Public #
    ##########

    def get_design_file(self):
        return self._btn_file.GetValue().strip()

    def clear_messages(self):
        self._txt_messages.Clear()

    def add_message(self, message):
        self._txt_messages.AppendText(f'{message}\n')


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.check_design.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
