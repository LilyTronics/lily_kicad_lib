"""
Tool info for the process design tool.
"""

from toolbox.tools.process_design.src.controller import Controller
from toolbox.tools.process_design.src.panel import Panel


class ToolInfo:
    name = 'Process design'
    image = 'tool_template.png'
    panel = Panel
    controller = Controller
    order = 3

if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
