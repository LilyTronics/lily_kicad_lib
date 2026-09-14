"""
Run the tool in a separate window for testing.
"""

import wx


def run_tool(name, panel, controller):
    app = wx.App(redirect=False)
    app.SetAppName(name)
    f = wx.Frame(None, title=name)
    win = panel(f)
    f.SetInitialSize((900, 700))
    f.SetPosition((100, 50))
    f.Show()
    controller(win)
    app.MainLoop()


if __name__ == '__main__':

    class TestPanel(wx.Panel):
        pass

    class TestController:

        def __init__(self, window):
            self._view = window

    run_tool('Test', TestPanel, TestController)
