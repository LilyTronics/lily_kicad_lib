"""
Tool info for the check library.
"""

from toolbox.tools.check_library.src.controller import Controller
from toolbox.tools.check_library.src.panel import Panel


class ToolInfo:
    name = 'Check libraries'
    image = 'check_library.png'
    panel = Panel
    controller = Controller


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
