"""
Controller for tool template.
"""


from toolbox.tools.common.controller_base import ControllerBase


class Controller(ControllerBase):
    pass


if __name__ == "__main__":

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.tool_template.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
