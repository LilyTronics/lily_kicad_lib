"""
Main controller
"""

from toolbox.views.view_main import ViewMain


class ControllerMain:

    def __init__(self):
        self._view = ViewMain()
        self._view.ShowModal()


if __name__ == "__main__":

    from toolbox.toolbox import run_toolbox

    run_toolbox()
