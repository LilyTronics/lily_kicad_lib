"""
Run the toolbox
"""

import wx

from toolbox.controllers.controller_main import ControllerMain


def run_toolbox(active_tab=0):
    app = wx.App(redirect=False)
    ControllerMain(active_tab)
    app.MainLoop()


if __name__ == "__main__":

    run_toolbox()
