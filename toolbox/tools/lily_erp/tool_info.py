"""
Tool info for the tool template.
"""

from toolbox.tools.lily_erp.src.controller import Controller
from toolbox.tools.lily_erp.src.panel import Panel


class ToolInfo:
    name = 'Lily ERP'
    image = 'lily_erp.png'
    panel = Panel
    controller = Controller
    order = 4


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
