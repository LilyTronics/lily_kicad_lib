"""
Check library controller.
"""

import wx

from toolbox.app_data import AppData
from toolbox.controllers.controller_base import ControllerBase
from toolbox.models.id_manager import IdManager
from toolbox.models.erp_checker import ErpChecker
from toolbox.models.footprints_checker import FootprintsChecker
from toolbox.models.projects_checker import ProjectsChecker
from toolbox.models.symbols_checker import SymbolsChecker
from toolbox.views.view_check_library import ViewCheckLibrary


class ControllerCheckLibrary(ControllerBase):

    name = "Check Libraries"

    _checkers = {
        "Check symbols": SymbolsChecker,
        "Check footprints": FootprintsChecker,
        "Check ERP data": ErpChecker,
        "Check projects": ProjectsChecker
    }

    def __init__(self, main_view, notebook):
        super().__init__(main_view, ViewCheckLibrary(notebook))
        self._view.initialize_tree(list(self._checkers.keys()))
        self.bind(wx.EVT_BUTTON, self._on_check_click, IdManager.ID_BTN_CHECK)

    ###########
    # Private #
    ###########

    def _run_checker(self, checker):
        self._main_view.add_to_console(f"\nRun checker: {checker}")
        self._checkers[checker].stdout = self._main_view.add_to_console
        messages = self._checkers[checker].run()
        self._view.add_messages(checker, messages)

    ##################
    # Event handlers #
    ##################

    def _on_check_click(self, _event):
        self._view.initialize_tree(list(self._checkers.keys()))
        self._main_view.clear_console()
        for checker in self._checkers:
            wx.CallAfter(self._run_checker, checker)


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
