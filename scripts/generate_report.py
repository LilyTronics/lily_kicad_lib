"""
Generates an HTML report with all symbols.
"""

import html
import os

from string import Template
from datetime import datetime
from lib_parser import LibParser


def generate_report():
    script_path = os.path.dirname(__file__)
    template_filename = os.path.abspath(os.path.join(script_path, "templates", "report_template.html"))
    output_filename = os.path.abspath(os.path.join(script_path, "..", "documents", "symbols_report.html"))
    symbols = LibParser.get_symbols()
    print("\nGenerate report")
    generic_symbols_data = ""
    parts_data = ""
    fields = []
    for symbol in sorted(symbols, key=lambda x: x["Name"]):
        symbol_data = "{ "
        # Mandatory fields first
        for property_name in LibParser.SYMBOL_MANDATORY_FIELDS:
            value = html.escape(symbol[property_name])
            symbol_data += f'{property_name}: "{value}", '
            if property_name not in fields:
                fields.append(property_name)
        # Add non-mandatory fields
        for property_name in filter(lambda x: x not in LibParser.SYMBOL_MANDATORY_FIELDS, symbol):
            value = html.escape(symbol[property_name])
            symbol_data += f'{property_name}: "{value}", '
            if property_name not in fields:
                fields.append(property_name)
        symbol_data = symbol_data[:-2] + " }"
        if symbol["Extends"] == "":
            generic_symbols_data += f"    {symbol_data},\n"
        else:
            parts_data += f"    {symbol_data},\n"

    with open(template_filename, "r") as fp:
        template = Template(fp.read())

    with open(output_filename, "w") as fp:
        fp.write(template.substitute(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            total=len(symbols),
            fields=str(fields).replace("'", '"'),
            generic_symbols_data=generic_symbols_data[:-2],
            parts_data=parts_data[:-2]
        ))
    print("\nDone")


if __name__ == "__main__":

    generate_report()
