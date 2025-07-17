"""
Generate product ID controller.
"""

import wx

from toolbox.models.erp_connect import get_components_from_erp
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
        self._view.Bind(wx.EVT_BUTTON, self._on_generate_click, id=IdManager.ID_BTN_GENERATE)
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

    def _on_generate_click(self, _event):
        error = ""
        properties = {}
        data = self._view.get_input()
        if data["category"] == "":
            error = "Select a category."

        if error == "":
            properties = self._product_categories.get_properties(data["category"])
            if "product_id" not in properties:
                error = f"No properties found for category '{data["category"]}'."
            elif "-" not in properties["product_id"]:
                error = f"Wrong product ID format '{properties["product_id"]}' for category '{data["category"]}'."

        if error == "":
            series = ""
            if "," in data["series"]:
                series = data["series"].split(",")[0]
            id_filter = f"{properties["product_id"][:properties["product_id"].index("-") + 1]}{series}%"
            print(id_filter)
            result = get_components_from_erp(self._main_view.add_to_console, id_filter)
            if not result[0]:
                error = "Failed to retrieve components from the ERP database."
            else:
                product_ids = sorted(list(map(lambda r: r["default_code"], result[1])))
                output = {
                    "low": "na" if len(product_ids) == 0 else product_ids[0],
                    "high": "na" if len(product_ids) == 0 else product_ids[-1],
                    "next": self._product_categories.generate_next_code(data["category"], product_ids,
                                                                        data["series"], data["value"])
                }
                self._view.set_product_ids(output)

        if error != "":
            dlg = wx.MessageDialog(self._view, error, "Generate product ID", style=wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()

    ##########
    # Public #
    ##########

    def get_view(self):
        return self._view


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(1)
