"""
Class that checks the test design.
"""

from scripts.models.lib_parser import LibParser
from scripts.models.test_design_parser import TestDesignParser


class TestDesignChecker:

    @classmethod
    def run(cls):
        report_messages = []
        lib_symbols = LibParser.get_symbols()
        lib_footprints = LibParser.get_footprints()
        design_symbols = TestDesignParser.get_symbols()
        design_footprints = TestDesignParser.get_footprints()
        cls._check_if_symbols_in_design(lib_symbols, design_symbols, report_messages)
        cls._check_if_footprints_in_design(design_symbols, lib_footprints, design_footprints, report_messages)
        cls._check_symbols_properties(design_symbols, lib_symbols, report_messages)
        return report_messages

    @classmethod
    def _check_if_symbols_in_design(cls, lib_symbols, design_symbols, report_messages):
        # Check if lib symbols are in the design
        for lib_symbol in lib_symbols:
            matches = list(filter(lambda x: x["lib_id"] == f"lily_symbols:{lib_symbol["Name"]}", design_symbols))
            # Parts must be in design
            # Generic symbols should not be in the design, except power symbols and logos
            if (lib_symbol["Extends"] != "" or lib_symbol["Reference"] == "#PWR" or
                    lib_symbol["Name"].startswith("logo_")):
                if len(matches) == 0:
                    report_messages.append({
                        "item": lib_symbol["Name"],
                        "message": "symbol is not in the test design"
                    })
            else:
                if len(matches) > 0:
                    report_messages.append({
                        "item": lib_symbol["Name"],
                        "message": "symbol should not be in the test design"
                    })

        # Check if there are symbols in the design, not in the lib (old symbols)
        for design_symbol in design_symbols:
            lib_name = design_symbol["lib_id"].split(":")[1]
            matches = list(filter(lambda x: x["Name"] == lib_name, lib_symbols))
            if len(matches) == 0:
                report_messages.append({
                    "item": design_symbol["Reference"],
                    "message": f"symbol is not in the library {lib_name}"
                })

    @classmethod
    def _check_if_footprints_in_design(cls, design_symbols, lib_footprints, design_footprints, report_messages):
        # Check if lib footprints are in the design
        for lib_footprint in lib_footprints:
            # Only check footprints that are used in the test design symbols
            matches = list(filter(lambda x: x["Footprint"] == f"lily_footprints:{lib_footprint["Name"]}",
                                  design_symbols))
            if len(matches) == 0:
                continue
            matches = list(filter(lambda x: x["Footprint"] == f"lily_footprints:{lib_footprint["Name"]}",
                                  design_footprints))
            if len(matches) == 0:
                report_messages.append({
                    "item": lib_footprint["Name"],
                    "message": "footprint is not in the test design"
                })

        # Check if there are footprints in the design, not in the lib (old footprints)
        for design_footprint in design_footprints:
            lib_name = design_footprint["Footprint"].split(":")[1]
            matches = list(filter(lambda x: x["Name"] == lib_name, lib_footprints))
            if len(matches) == 0:
                report_messages.append({
                    "item": design_footprint["Reference"],
                    "message": f"footprint is not in the library {lib_name}"
                })

    @classmethod
    def _check_symbols_properties(cls, design_symbols, lib_symbols, report_messages):
        for design_symbol in design_symbols:
            lib_name = design_symbol["lib_id"].split(":")[1]
            matches = list(filter(lambda x: x["Name"] == lib_name, lib_symbols))
            if len(matches) > 0:
                lib_symbol = matches[0]
                # Check if keys are same
                # Fields in the design but not in the lib
                diff = list(set(design_symbol.keys()) - set(lib_symbol.keys()))
                diff.remove("lib_id")
                if len(diff) > 0:
                    report_messages.append({
                        "item": design_symbol["Reference"],
                        "message": f"symbol has extra fields that are not in the library: {", ".join(diff)}"
                    })
                # Fields missing in the design symbol
                diff = list(set(lib_symbol.keys()) - set(design_symbol.keys()))
                diff.remove("Name")
                diff.remove("Extends")
                diff.remove("Notes")
                if len(diff) > 0:
                    report_messages.append({
                        "item": design_symbol["Reference"],
                        "message": f"symbol has missing fields: {", ".join(diff)}"
                    })


if __name__ == "__main__":

    messages = TestDesignChecker.run()
    print(f"{len(messages)} messages")
    for message in messages:
        print(message)
