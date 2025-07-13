"""
Check library controller.
"""

from toolbox.views.view_check_library import ViewCheckLibrary


class ControllerCheckLibrary:

    name = "Check Libraries"

    def __init__(self, parent):
        self._view = ViewCheckLibrary(parent)

    ##########
    # Public #
    ##########

    def get_view(self):
        return self._view


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
