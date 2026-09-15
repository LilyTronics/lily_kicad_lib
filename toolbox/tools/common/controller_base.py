"""
Base controller for the tools.
"""


class ControllerBase:

    UPDATE_INTERVAL = 1

    def __init__(self, tool_window, logger):
        self.tool_view = tool_window
        self.logger = logger


if __name__ == '__main__':

    class ControllerTest(ControllerBase):
        pass

    c = ControllerTest(None, None)
