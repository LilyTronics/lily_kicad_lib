"""
Generates an HTML report with all symbols.
"""

import html

from string import Template
from datetime import datetime


def generate_report():
    mandatory_properties = [
        "Name",
        "Extends",
        "Reference",
        "Value",
        "Footprint",
        "Description",
        "Datasheet",
        "Revision",
        "ki_fp_filters"
    ]
    with open("../symbols/lily_symbols.kicad_sym", "r") as fp:
        lines = fp.readlines()
    print(f"Read: {len(lines)} lines")
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
                        symbol[property_name] = parts[1].strip().strip('"')
                        if property_name not in mandatory_properties and property_name not in property_names:
                            property_names.append(property_name)
                elif lines[i].startswith("\t)"):
                    break
            symbols.append(symbol)
        i += 1
    print(f"Found: {len(symbols)} symbols")
    print(f"Extra properties: {property_names}")
    print("Generate report")

    output = "<tr>"
    output += "<th>#</th>"
    for property_name in mandatory_properties:
        output += f"<th>{html.escape(property_name)}</th>"
    for property_name in property_names:
        output += f"<th>{html.escape(property_name)}</th>"
    output += "</tr>\n"
    i = 1
    for symbol in sorted(symbols, key=lambda x: x["Name"]):
        output += "<tr>"
        output += f"<td>{i}</td>"
        for property_name in mandatory_properties:
            value = html.escape(symbol.get(property_name, "not available"))
            output += f"<td>{value}</td>"
        for property_name in property_names:
            value = html.escape(symbol.get(property_name, "not available"))
            output += f"<td>{value}</td>"
        output += "</tr>\n"
        i += 1
    with open("symbols_report_template.html", "r") as fp:
        template = Template(fp.read())
    with open("../documents/symbols_report.html", "w") as fp:
        fp.write(template.substitute(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            total=len(symbols),
            content=output
        ))
    print("Done")


if __name__ == "__main__":

    generate_report()
