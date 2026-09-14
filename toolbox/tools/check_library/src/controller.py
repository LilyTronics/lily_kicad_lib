"""
Controller for tool template.
"""

import wx

from toolbox.common.checkers.erp_checker import ErpChecker
from toolbox.common.checkers.footprints_checker import FootprintsChecker
from toolbox.common.checkers.projects_checker import ProjectsChecker
from toolbox.common.checkers.symbols_checker import SymbolsChecker
from toolbox.common.checkers.unused_items_checker import UnusedItemsChecker

from toolbox.tools.common.controller_base import ControllerBase


class Controller(ControllerBase):

    _checkers = {
        'Check symbols': SymbolsChecker,
        'Check footprints': FootprintsChecker,
        'Check unused items': UnusedItemsChecker,
        'Check ERP data': ErpChecker,
        'Check projects': ProjectsChecker
    }

    def __init__(self, *args):
        super().__init__(*args)
        self.tool_view.initialize_tree(list(self._checkers.keys()))
        self.tool_view.Bind(wx.EVT_BUTTON, self._on_check_click, self.tool_view.ID_BTN_CHECK)

    ###########
    # Private #
    ###########

    def _run_checker(self, checker):
        self.app_view.add_to_console(f'\nRun checker: {checker}')
        self._checkers[checker].stdout = self.app_view.add_to_console
        messages = self._checkers[checker].run()
        self.tool_view.add_messages(checker, messages)

    ##################
    # Event handlers #
    ##################

    def _on_check_click(self, _event):
        self.tool_view.initialize_tree(list(self._checkers.keys()))
        self.app_view.clear_console()
        for checker in self._checkers:
            wx.CallAfter(self._run_checker, checker)


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.check_library.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
