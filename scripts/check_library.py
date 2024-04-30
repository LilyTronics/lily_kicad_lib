"""
Checks the library and report the errors
"""

import html
import os

from string import Template
from datetime import datetime


def generate_report():
    mandatory_properties = [
        "Name",
        "Extends",
        "Reference",
        "Value",
        "Description",
        "Datasheet",
        "Footprint",
        "Revision"
    ]
    ignore_fields = [
        "ki_locked"
    ]
    script_path = os.path.dirname(__file__)
    lib_filename = os.path.abspath(os.path.join(script_path, "..", "symbols", "lily_symbols.kicad_sym"))
    template_filename = os.path.abspath(os.path.join(script_path, "templates", "report_template.html"))
    output_filename = os.path.abspath(os.path.join(script_path, "..", "documents", "symbols_report.html"))
    print("Library file :", lib_filename)
    print("Template file:", template_filename)
    print("Output file  :", output_filename)

    print("\nRead library")
    with open(lib_filename, "r") as fp:
        lines = fp.readlines()
    print(f"Read: {len(lines)} lines")

    print("\nParsing symbols")
    symbols = []
    property_names = []
    i = 0
    while i < len(lines):
        symbol = {}
        if lines[i].startswith("\t(symbol "):
            symbol["Name"] = lines[i].strip()[8:].strip('"')
            while i < len(lines):
                i += 1
                if lines[i].startswith("\t\t(extends "):
                    symbol["Extends"] = lines[i].strip().strip(")")[9:].strip('"')
                elif lines[i].startswith("\t\t(property "):
                    parts = lines[i].strip()[10:].split('" "')
                    if len(parts) == 2:
                        property_name = parts[0].strip('"')
                        if property_name not in ignore_fields:
                            symbol[property_name] = parts[1].strip().strip('"')
                            if property_name not in mandatory_properties and property_name not in property_names:
                                property_names.append(property_name)
                elif lines[i].startswith("\t)"):
                    break
            symbols.append(symbol)
        i += 1
    print(f"Found: {len(symbols)} symbols")
    print(f"Extra properties: {property_names}")

    print("\nGenerate report")
    generic_symbols_data = ""
    parts_data = ""
    for symbol in sorted(symbols, key=lambda x: x["Name"]):
        symbol_data = "{ "
        for property_name in mandatory_properties:
            value = html.escape(symbol.get(property_name, ""))
            symbol_data += f'{property_name}: "{value}", '
        for property_name in property_names:
            value = html.escape(symbol.get(property_name, ""))
            symbol_data += f'{property_name}: "{value}", '
        symbol_data = symbol_data[:-2] + " }"
        if symbol.get("Extends", None) is None:
            generic_symbols_data += f"    {symbol_data},\n"
        else:
            parts_data += f"    {symbol_data},\n"

    with open(template_filename, "r") as fp:
        template = Template(fp.read())

    with open(output_filename, "w") as fp:
        fp.write(template.substitute(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            total=len(symbols),
            fields=str(mandatory_properties + property_names).replace("'", '"'),
            generic_symbols_data=generic_symbols_data[:-2],
            parts_data=parts_data[:-2]
        ))
    print("\nDone")


if __name__ == "__main__":

    generate_report()
