"""
Controller for tool template.
"""


from toolbox.tools.common.controller_base import ControllerBase


class Controller(ControllerBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.add_to_console("Tool template controller loaded")



if __name__ == "__main__":

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.tool_template.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
