"""
Generate product ID controller.
"""

import wx

from toolbox.models.id_manager import IdManager
from toolbox.models.product_categories import ProductCategories
from toolbox.views.view_generate_product_id import ViewGenerateProductId


class ControllerGenerateProductId:

    name = "Generate product ID"

    def __init__(self, main_view, notebook):
        self._main_view = main_view
        self._view = ViewGenerateProductId(notebook)
        self._view.Bind(wx.EVT_BUTTON, self._on_reload_click, id=IdManager.ID_BTN_RELOAD)
        self._view.Bind(wx.EVT_CHOICE, self._on_category_select, id=IdManager.ID_CMB_CATEGORIES)
        self._load_categories()

    ###########
    # Private #
    ###########

    def _load_categories(self):
        categories = []
        try:
            self._product_categories = ProductCategories()
            categories = self._product_categories.get_categories()
        except Exception as e:
            self._main_view.add_to_console(f"Error loading categories: {e}")
        self._view.set_categories(categories)

    ##################
    # Event handlers #
    ##################

    def _on_reload_click(self, _event):
        self._load_categories()

    def _on_category_select(self, event):
        properties = self._product_categories.get_properties(event.GetString())
        self._view.enable_controls(properties)

    ##########
    # Public #
    ##########

    def get_view(self):
        return self._view


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(1)
