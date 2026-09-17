"""
Run the tool in a separate window for testing.
"""

import wx

from toolbox.common.logger import Logger


def run_tool(name, panel, controller):
    app = wx.App(redirect=False)
    app.SetAppName(name)
    f = wx.Frame(None, title=name)
    p = wx.Panel(f)
    console = wx.TextCtrl(p, style=wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_READONLY)
    console.SetFont(
        wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    )
    win = panel(p)
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(win, 2, wx.EXPAND | wx.ALL, 5)
    box.Add(console, 1, wx.EXPAND | wx.ALL, 5)
    p.SetSizer(box)
    f.SetInitialSize((900, 700))
    f.SetPosition((100, 50))
    f.Show()
    controller(win, Logger(console, True))
    app.MainLoop()


if __name__ == '__main__':

    from toolbox.tools.common.controller_base import ControllerBase


    class TestPanel(wx.Panel):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            lbl = wx.StaticText(self, wx.ID_ANY, 'Test panel loaded')
            lbl.SetPosition((10, 10))

    class TestController(ControllerBase):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logger.add_to_console('Test controller loaded')


    run_tool('Test', TestPanel, TestController)
