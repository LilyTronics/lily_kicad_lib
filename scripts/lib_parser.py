"""
Parsing the library and returns the symbols/footprints.
"""

import glob
import os


class LibParser:

    SYMBOL_MANDATORY_FIELDS = [
        "Name",
        "Extends",
        "Reference",
        "Value",
        "Description",
        "Datasheet",
        "Footprint",
        "Revision"
    ]
    SYMBOL_IGNORE_FIELDS = [
        "ki_locked"
    ]

    @classmethod
    def get_symbols(cls):
        script_path = os.path.dirname(__file__)
        lib_filename = os.path.abspath(os.path.join(script_path, "..", "symbols", "lily_symbols.kicad_sym"))
        print(f"\nRead symbols library: {lib_filename}")
        with open(lib_filename, "r") as fp:
            lines = fp.readlines()
        symbols = []
        i = 0
        fields = []
        while i < len(lines):
            symbol = {}
            if lines[i].startswith("\t(symbol "):
                symbol["Name"] = lines[i].strip()[8:].strip('"')
                while i < len(lines):
                    i += 1
                    property_name = ""
                    if lines[i].startswith("\t\t(extends "):
                        symbol["Extends"] = lines[i].strip().strip(")")[9:].strip('"')
                        property_name = "Extends"
                    elif lines[i].startswith("\t\t(property "):
                        parts = lines[i].strip()[10:].split('" "')
                        if len(parts) == 2:
                            property_name = parts[0].strip('"')
                            if property_name not in cls.SYMBOL_IGNORE_FIELDS:
                                symbol[property_name] = parts[1].strip().strip('"')
                    elif lines[i].startswith("\t)"):
                        break
                    if (property_name != "" and property_name not in fields and
                            property_name not in cls.SYMBOL_IGNORE_FIELDS):
                        fields.append(property_name)
                symbols.append(symbol)
            i += 1
        # Make sure all symbols have the same fields
        for symbol in symbols:
            for field in fields:
                if field not in symbol:
                    symbol[field] = ""
        return symbols

    @classmethod
    def get_footprints(cls):
        script_path = os.path.dirname(__file__)
        lib_path = os.path.abspath(os.path.join(script_path, "..", "lily_footprints.pretty"))
        print(f"\nRead footprints library: {lib_path}")
        footprints = []
        fields = []
        for item in glob.glob(os.path.join(lib_path, "*.kicad_mod")):
            with open(item, "r") as fp:
                lines = fp.readlines()
            i = 0
            footprint = {}
            while i < len(lines):
                property_name = ""
                value = ""
                property_data = {
                    "Value": "",
                    "Layer": "",
                    "Size": "",
                    "Thickness": ""
                }
                if lines[i].startswith("(footprint "):
                    property_name = "Name"
                    value = lines[i].strip()[11:].strip('"')
                elif lines[i].startswith("\t(attr "):
                    property_name = "Attributes"
                    value = lines[i].strip().strip(")")[6:].split(" ")
                elif lines[i].startswith("\t(model "):
                    property_name = "Model"
                    value = lines[i].strip()[8:].strip('"')
                elif lines[i].startswith("\t(property "):
                    parts = lines[i].strip()[10:].split('" "')
                    if len(parts) == 2:
                        property_name = parts[0].strip('"')
                        property_data["Value"] = parts[1].strip().strip('"')
                elif lines[i].startswith('\t(fp_text user "${REFERENCE}"'):
                    property_name = "Reference_F.Fab"
                    property_data["Value"] = "${REFERENCE}"
                # Get extra properties
                if property_data["Value"] != "":
                    while i < len(lines):
                        if lines[i].startswith("\t)"):
                            break
                        if lines[i].startswith("\t\t(layer "):
                            property_data["Layer"] = lines[i].strip().strip(")")[7:].strip('"')
                        elif lines[i].startswith("\t\t\t\t(size "):
                            property_data["Size"] = lines[i].strip().strip(")")[6:].strip('"')
                        elif lines[i].startswith("\t\t\t\t(thickness "):
                            property_data["Thickness"] = lines[i].strip().strip(")")[11:].strip('"')
                        i += 1
                    value = property_data
                # Add property if we found any
                if property_name != "":
                    footprint[property_name] = value
                    if property_name not in fields:
                        fields.append(property_name)
                i += 1
            footprints.append(footprint)
        # Make sure all footprints have the same fields
        for footprint in footprints:
            for field in fields:
                if field not in footprint:
                    footprint[field] = ""
        return footprints


if __name__ == "__main__":

    _symbols = LibParser.get_symbols()
    print("Symbols:", len(_symbols))
    if len(_symbols) > 0:
        print("Showing max 10 symbols:")
        for _symbol in _symbols[:10]:
            print(_symbol)

    _footprints = LibParser.get_footprints()
    print("\nFootprints:", len(_footprints))
    if len(_footprints) > 0:
        print("Showing max 10 footprints:")
        for _footprint in _footprints[:10]:
            print(_footprint)
