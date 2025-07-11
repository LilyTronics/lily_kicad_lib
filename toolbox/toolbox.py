"""
Run the toolbox
"""

import wx

from toolbox.controllers.controller_main import ControllerMain


def run_toolbox():
    app = wx.App(redirect=False)
    ControllerMain()
    app.MainLoop()


if __name__ == "__main__":

    run_toolbox()
