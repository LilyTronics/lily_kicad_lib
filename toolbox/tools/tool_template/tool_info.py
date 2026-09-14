"""
Tool info for the tool template.
"""

from toolbox.tools.tool_template.src.controller import Controller
from toolbox.tools.tool_template.src.panel import Panel


class ToolInfo:
    name = 'Tool template'
    image = 'tool_template.png'
    panel = Panel
    controller = Controller


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
