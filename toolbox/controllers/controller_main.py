"""
Main controller
"""

from toolbox.controllers.controller_check_library import ControllerCheckLibrary
from toolbox.views.view_main import ViewMain


class ControllerMain:

    _controllers = [ControllerCheckLibrary]

    def __init__(self):
        self._view = ViewMain()

        for controller in self._controllers:
            c = controller(self._view, self._view.get_notebook())
            self._view.add_page(c.name, c.get_view())

        self._view.ShowModal()
        self._view.Destroy()


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
