"""
Panel with controls for the power supply
"""

import wx

import toolbox.tools.common.gui_sizes as GuiSizes


class Panel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)


if __name__ == "__main__":

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.tool_template.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
