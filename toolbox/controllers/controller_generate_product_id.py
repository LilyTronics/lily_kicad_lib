"""
Generate product ID controller.
"""

import wx

from toolbox.models.id_manager import IdManager
from toolbox.views.view_generate_product_id import ViewGenerateProductId


class ControllerGenerateProductId:

    name = "Generate product ID"

    def __init__(self, main_view, notebook):
        self._main_view = main_view
        self._view = ViewGenerateProductId(notebook)

    ##########
    # Public #
    ##########

    def get_view(self):
        return self._view


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(1)
