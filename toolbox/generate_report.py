"""
Generates an HTML report with all symbols.
"""

import base64
import html
import os

from string import Template
from datetime import datetime
from toolbox.models.parsers.lib_parser import LibParser


SYMBOL_FIRST_FIELDS = [
    "Name",
    "Extends",
    "Reference",
    "Value",
    "Description",
    "Footprint",
    "Revision"
]

SYMBOL_LAST_FIELDS = [
    "Datasheet"
]

def generate_report():
    script_path = os.path.dirname(__file__)
    template_filename = os.path.abspath(os.path.join(script_path, "templates", "report_template.html"))
    output_filename = os.path.abspath(os.path.join(script_path, "..", "docs", "library_report.html"))
    print("Generate report")

    # Symbols
    generic_symbols_data = ""
    parts_data = ""
    symbols = LibParser.get_symbols()
    symbol_fields = SYMBOL_FIRST_FIELDS[:]
    symbol_fields.extend(filter(lambda x: x not in SYMBOL_FIRST_FIELDS and x not in SYMBOL_LAST_FIELDS, symbols[0]))
    symbol_fields.extend(SYMBOL_LAST_FIELDS)
    for symbol in sorted(symbols, key=lambda x: x["Name"]):
        symbol_data = "{ "
        # Mandatory fields first
        for property_name in symbol_fields:
            value = html.escape(symbol.get(property_name, ""))
            symbol_data += f'{property_name}: "{value}", '
        symbol_data = symbol_data[:-2] + " }"
        if symbol.get("Extends", None) is None:
            generic_symbols_data += f"    {symbol_data},\n"
        else:
            parts_data += f"    {symbol_data},\n"

    # Footprints
    footprint_fields = ["Name", "Revision", "Model", "Image"]
    footprints_data = ""
    footprints = LibParser.get_footprints()
    for footprint in sorted(footprints, key=lambda x: x["Name"]):
        footprint_data = "{ "
        for field in footprint_fields:
            value = footprint.get(field, "")
            if isinstance(value, dict):
                value = value["Value"]
            footprint_data += f'{field}: "{html.escape(value)}", '
        footprint_data = footprint_data[:-2]
        # Add image data if available
        image_filename = os.path.join(LibParser.LIB_FOOTPRINT_PATH, f"{footprint["Name"]}.png")
        if os.path.isfile(image_filename):
            with open(image_filename, "rb") as img_file:
                # Encode the image to Base64
                base64_string = base64.b64encode(img_file.read()).decode('utf-8')
                footprint_data += f", Image: \"{base64_string}\""
        footprint_data += " }"
        footprints_data += f"    {footprint_data},\n"

    with open(template_filename, "r") as fp:
        template = Template(fp.read())

    with open(output_filename, "w") as fp:
        fp.write(template.substitute(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            total_symbols=len(symbols),
            total_footprints=len(footprints),
            symbol_fields=str(symbol_fields).replace("'", '"'),
            footprint_fields=str(footprint_fields).replace("'", '"'),
            generic_symbols_data=generic_symbols_data[:-2],
            parts_data=parts_data[:-2],
            footprints_data=footprints_data[:-2]
        ))
    print("\nDone")


if __name__ == "__main__":

    generate_report()
