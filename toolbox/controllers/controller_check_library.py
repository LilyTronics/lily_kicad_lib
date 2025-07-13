"""
Check library controller.
"""

import wx

from toolbox.models.id_manager import IdManager
from toolbox.models.symbols_checker import SymbolsChecker
from toolbox.views.view_check_library import ViewCheckLibrary


class ControllerCheckLibrary:

    name = "Check Libraries"

    _checks = {
        "Check symbols" : SymbolsChecker
    }

    def __init__(self, parent):
        self._view = ViewCheckLibrary(parent)
        self._view.initialize_tree(list(self._checks.keys()))
        self._view.Bind(wx.EVT_BUTTON, self._on_check_click, id=IdManager.ID_BTN_CHECK)

    ##################
    # Event handlers #
    ##################

    def _on_check_click(self, event):
        print("Run checks")

    ##########
    # Public #
    ##########

    def get_view(self):
        return self._view


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
