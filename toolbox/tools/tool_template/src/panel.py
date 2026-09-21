"""
Panel with controls for tool template
"""

import wx


class Panel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lbl = wx.StaticText(self, wx.ID_ANY, "Tool template panel loaded")
        lbl.SetPosition((10, 10))


if __name__ == "__main__":

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.tool_template.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
