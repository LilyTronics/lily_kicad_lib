"""
Parsing the library and returns the symbols/footprints.
"""

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
        print(f"\nRead library: {lib_filename}")
        with open(lib_filename, "r") as fp:
            lines = fp.readlines()
        print(f"Read: {len(lines)} lines")
        print("Parsing symbols")
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
                    if property_name != "" and property_name not in fields:
                        fields.append(property_name)
                symbols.append(symbol)
            i += 1
        # Make sure all symbols have the same fields
        for symbol in symbols:
            for field in fields:
                if field not in symbol:
                    symbol[field] = ""
        print(f"Found: {len(symbols)} symbols")
        print()
        return symbols


if __name__ == "__main__":

    _symbols = LibParser.get_symbols()
    print("Symbols:", len(_symbols))
    if len(_symbols) > 0:
        print("Showing max 10 symbols:")
        for _symbol in _symbols[:10]:
            print(_symbol)
