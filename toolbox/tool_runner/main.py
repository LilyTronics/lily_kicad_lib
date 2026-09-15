"""
Main script to start the application.
"""

import wx

import toolbox.tool_runner.app_data as AppData

from toolbox.tool_runner.src.controller_main import ControllerMain


def run_main():
    app = wx.App(redirect=False)
    app.SetAppName(AppData.EXE_NAME)
    ControllerMain(f'{AppData.APP_NAME} V{AppData.APP_VERSION}')
    app.MainLoop()


if __name__ == '__main__':

    run_main()
