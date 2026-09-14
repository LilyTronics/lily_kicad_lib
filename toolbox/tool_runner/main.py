"""
Main script to start the application.
"""

import wx

import toolbox.tool_runner.app_data as AppData

from toolbox.tool_runner.src.controller_main import ControllerMain
from toolbox.tool_runner.src.logger import Logger


def run_main():
    logger = Logger(AppData.LOG_FILENAME)
    logger.write('Start application')
    app = wx.App(redirect=False)
    app.SetAppName(AppData.EXE_NAME)
    ControllerMain(f'{AppData.APP_NAME} V{AppData.APP_VERSION}', logger)
    app.MainLoop()
    logger.write('Application terminated')


if __name__ == '__main__':

    run_main()
