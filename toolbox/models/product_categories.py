"""
Class holding product categories information.
"""

import json
import os

from toolbox.app_data import AppData


class ProductCategories:

    _DATA_FILENAME = os.path.join(AppData.APP_PATH, "toolbox", "models", "product_categories.json")

    def __init__(self):
        self._data = json.load(open(self._DATA_FILENAME, "r"))

    def get_categories(self):
        return list(self._data.keys())

    def get_properties(self, name):
        return self._data.get(name, {})


if __name__ == "__main__":

    pc = ProductCategories()
    categories = pc.get_categories()
    print(categories)
    print(pc.get_properties(categories[2]))
    print(pc.get_properties("not_existing_category"))
