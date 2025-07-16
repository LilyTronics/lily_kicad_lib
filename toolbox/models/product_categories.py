"""
Class holding product categories information.
"""

import json
import os

from toolbox.app_data import AppData


class ProductCategories:

    _DATA_FILENAME = os.path.join(AppData.APP_PATH, "toolbox", "models", "product_categories.json")

    def __init__(self):
        self._data = {}
        self._data = json.load(open(self._DATA_FILENAME, "r"))

    def get_categories(self):
        return list(self._data.keys())


if __name__ == "__main__":

    pc = ProductCategories()

    print(pc.get_categories())
