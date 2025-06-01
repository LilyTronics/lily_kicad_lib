"""
Create a CVS file for import in ERP.
Only parts with a valid Lily ID can be used for import.
"""

import csv
import re

from scripts.models.lib_parser import LibParser


_OUTPUT_FILE = "import_to_erp.csv"


def _get_symbols():
    # Populate a list sorted by Lily_ID and only with valid IDs
    valid_id = r"^\d{4}-\d{5}$"
    return [
        symbol for symbol in sorted(LibParser.get_symbols(), key=lambda x: x["Lily_ID"])
        if re.match(valid_id, symbol["Lily_ID"])
    ]


def generate_erp_import():
    mapped_data = [
        {
            "External ID": symbol["Lily_ID"],
            "Name": symbol["Name"].replace("_", " "),
            "Internal Reference": symbol["Lily_ID"],
            "Barcode": symbol["Lily_ID"],
            "Product Type": "Goods",
            "Product Category": "Electronic components"
        }
        for symbol in _get_symbols()
    ]
    with open(_OUTPUT_FILE, "w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=mapped_data[0].keys(), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(mapped_data)


if __name__ == "__main__":

    generate_erp_import()
