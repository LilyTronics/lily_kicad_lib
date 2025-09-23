"""
Base controller for the tool controllers.
"""


class ControllerBase:

    def __init__(self, main_view, view):
        self._main_view = main_view
        self._view = view

    ##########
    # Public #
    ##########

    def bind(self, event, event_handler, control_id):
        self._view.Bind(event, event_handler, id=control_id)

    def get_view(self):
        return self._view


if __name__ == "__main__":
    from toolbox.run_toolbox import run_toolbox

    run_toolbox()
