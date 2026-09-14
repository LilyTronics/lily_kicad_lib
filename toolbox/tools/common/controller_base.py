"""
Base controller for the tools.
"""

import time
import traceback


class ControllerBase:

    UPDATE_INTERVAL = 1

    def __init__(self, tool_window, app_window):
        self.tool_view = tool_window
        self.app_view = app_window


if __name__ == '__main__':

    class ControllerTest(ControllerBase):
        pass

    c = ControllerTest(None, None)
