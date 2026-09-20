"""
Tool info for the check design.
"""

from toolbox.tools.check_design.src.controller import Controller
from toolbox.tools.check_design.src.panel import Panel


class ToolInfo:
    name = 'Check design'
    image = 'check_design.png'
    panel = Panel
    controller = Controller
    order = 2


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
