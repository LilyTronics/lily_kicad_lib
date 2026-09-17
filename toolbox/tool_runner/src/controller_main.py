"""
Main controller for the tool runner
"""

import os
import wx

import toolbox.tool_runner.app_data as AppData

from toolbox.common.logger import Logger
from toolbox.tool_runner.src.application_settings import ApplicationSettings
from toolbox.tool_runner.src.tools_registry import ToolsRegistry
from toolbox.tool_runner.src.view_frame_main import ViewFrameMain


class ControllerMain:

    def __init__(self, title):
        self._controllers = []
        self._app_settings = ApplicationSettings()
        self._view = ViewFrameMain(title)
        self._view.Show()
        self._logger = Logger(self._view.get_console(), AppData.DEBUG)
        wx.CallAfter(self._prepare_view)
        wx.CallAfter(self._load_tools)

    ###########
    # Private #
    ###########

    def _prepare_view(self):
        value = self._app_settings.get_main_window_position()
        if -1 not in value:
            self._view.SetPosition(value)
        value = self._app_settings.get_main_window_size()
        if -1 not in value:
            self._view.SetSize(value)
        self._view.Maximize(self._app_settings.get_main_window_maximized())

        self._view.Bind(wx.EVT_CLOSE, self._on_view_close)
        self._view.Bind(wx.EVT_BUTTON, self._on_reload, id=self._view.ID_RELOAD)

    def _load_callback(self,message):
        self._logger.add_to_console(message)

    def _load_tools(self):
        del self._controllers[:]
        self._view.remove_tools()
        lbk = self._view.get_list_book()
        ToolsRegistry.load(self._load_callback)
        for tool in ToolsRegistry.get_tools():
            image_path = os.path.join(tool.path, tool.image)
            window = tool.panel(lbk)
            self._view.add_tool(tool.name, window, wx.Bitmap(image_path))
            self._controllers.append(tool.controller(window, self._logger))

    ##################
    # Event handlers #
    ##################

    def _on_reload(self, event):
        self._logger.clear_console()
        self._logger.add_to_console('Reload tools')
        self._load_tools()
        event.Skip()

    def _on_view_close(self, event):
        self._app_settings.store_main_window_maximized(self._view.IsMaximized())
        if not self._view.IsMaximized():
            self._app_settings.store_main_window_position(*self._view.GetPosition())
            self._app_settings.store_main_window_size(*self._view.GetSize())
        event.Skip()


if __name__ == '__main__':

    from toolbox.tool_runner.main import run_main

    run_main()
