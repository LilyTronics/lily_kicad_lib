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

    def generate_next_code(self, category, existing_codes, series, value):
        next_code = ""
        properties = self.get_properties(category)
        dash_index = properties["product_id"].index("-") + 1
        if properties["product_id"].endswith("1xxxx"):
            # Simple sequence
            for i in range(10001, 100000):
                next_id = f"{properties["product_id"][:dash_index]}{i:05d}"
                if next_id not in existing_codes:
                    next_code = next_id
                    break
        if properties["product_id"].endswith("1xxyy"):
            # Sequence with version number
            for i in range(101, 1000):
                next_id = f"{properties["product_id"][:dash_index]}{i:03d}01"
                if next_id not in existing_codes:
                    next_code = next_id
                    break
        if "value" in properties["product_id"]:
            # Generate product code based on series and value
            if "," in series:
                series = series.split(",")[0]
            else:
                series = "0"
            # Convert value to code
            power = "-1"
            if "p" in value or "R" in value:
                value = value.replace("p", ".").replace("R", ".")
                if float(value) >= 1:
                    power = "0"
                if float(value) >= 10:
                    power = "1"
                if float(value) >= 100:
                    power = "2"
            elif "n" in value or "k" in value:
                value = value.replace("n", ".").replace("k", ".")
                if float(value) >= 1:
                    power = "3"
                if float(value) >= 10:
                    power = "4"
                if float(value) >= 100:
                    power = "5"
            elif "u" in value or "M" in value:
                value = value.replace("u", ".").replace("M", ".")
                if float(value) >= 1:
                    power = "6"
                if float(value) >= 10:
                    power = "7"
                if float(value) >= 100:
                    power = "8"
                if float(value) >= 1000:
                    power = "9"
            value = value.replace(".", "").lstrip("0")
            while len(value) < 3:
                value = f"{value}0"
            if len(value) > 3:
                value = value[:3]
            if power == "-1":
                value = f"0{value}"
            else:
                value = f"{value}{power}"
            next_code = f"{properties["product_id"][:dash_index]}{series}{value}"
        return next_code if next_code not in existing_codes else "already exist"


if __name__ == "__main__":

    pc = ProductCategories()
    _categories = pc.get_categories()
    print("Categories:", _categories)

    print("\nProperties:")
    for _category in [_categories[1], _categories[2], _categories[23], "not_existing_category"]:
        print(f"{_category}:", pc.get_properties(_category))

    print("\nNext product code")
    _series = "1,0805 X7R 10%"
    _value = "1n"
    _test_codes = {
        1: ["1911-10001", "1911-10002", "1911-10004"],
        2: ["1912-11003", "1912-11004", "1912-11005", "1912-11203"],
        23: ["2910-10101", "2910-10102", "2910-10201", "2910-10401"],
    }
    for _key in _test_codes:
        print(f"{_key}:", pc.generate_next_code(_categories[_key], _test_codes[_key], _series, _value))
