"""
Main controller
"""

from toolbox.app_data import AppData
from toolbox.controllers.controller_check_library import ControllerCheckLibrary
from toolbox.controllers.controller_generate_product_id import ControllerGenerateProductId
from toolbox.views.view_main import ViewMain


class ControllerMain:

    _controllers = [ControllerCheckLibrary, ControllerGenerateProductId]

    def __init__(self, active_tab):
        self._view = ViewMain()
        self._view.add_to_console(f"Path: {AppData.APP_PATH}")

        for controller in self._controllers:
            c = controller(self._view, self._view.get_notebook())
            self._view.add_page(c.name, c.get_view())

        self._view.get_notebook().SetSelection(active_tab)
        self._view.ShowModal()
        self._view.Destroy()


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
