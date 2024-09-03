"""
Checks the projects to the library.
"""

import os

from scripts.models.design_parser import DesignParser
from scripts.models.lib_parser import LibParser


class ProjectsChecker:

    SCRIPT_PATH = os.path.dirname(__file__)
    PROJECTS_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, "..", "..", "projects"))

    PART_MANDATORY_FIELDS = ["Status", "Manufacturer", "Manufacturer_ID", "Lily_ID", "JLCPCB_ID", "JLCPCB_STATUS"]
    SKIP_SYMBOL_FIELDS = ["Name", "Extends"]

    @classmethod
    def run(cls):
        designs = {}
        # Get symbols and footprints for the projects
        for project_folder in os.listdir(cls.PROJECTS_PATH):
            full_path = os.path.join(cls.PROJECTS_PATH, project_folder)
            if os.path.isdir(full_path):
                designs[project_folder] = {
                    "symbols": DesignParser.get_symbols(full_path),
                    "footprints": DesignParser.get_footprints(full_path)
                }
        lib_symbols = LibParser.get_symbols()
        lib_footprints = LibParser.get_footprints()

        report_messages = []
        cls._check_if_symbols_in_designs(lib_symbols, designs, report_messages)
        # cls._check_if_symbols_not_in_library()
        cls._check_if_footprints_in_designs(lib_footprints, designs, report_messages)
        # cls._check_if_footprints_not_in_library()
        cls._check_symbols_properties(designs, lib_symbols, report_messages)
        # cls._check_footprint_properties(designs, lib_footprints, report_messages)
        cls._check_symbols_vs_footprints(designs, report_messages)

        return report_messages

    @classmethod
    def _check_if_symbols_in_designs(cls, lib_symbols, designs, report_messages):
        for lib_symbol in lib_symbols:
            should_be_used = (
                lib_symbol["Extends"] != "" or  # Parts should be used in designs
                lib_symbol["Reference"] == "#PWR" or  # Power symbols should be used in designs
                lib_symbol["Name"].startswith("logo_")  # Logos should be used in designs
            )

            is_used = False
            for design in designs:
                matches = list(filter(lambda x: x["lib_id"] == f"lily_symbols:{lib_symbol["Name"]}",
                                      designs[design]["symbols"]))
                if len(matches) > 0:
                    is_used = True

                if len(matches) > 0 and not should_be_used:
                    report_messages.append({
                        "item": lib_symbol["Name"],
                        "message": f"symbol should not be in the project {design}"
                    })

            if should_be_used and not is_used:
                report_messages.append({
                    "item": lib_symbol["Name"],
                    "message": "symbol is not in one of the projects"
                })

    @classmethod
    def _check_symbols_properties(cls, designs, lib_symbols, report_messages):
        for design in designs:
            for design_symbol in designs[design]["symbols"]:
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
                            "item": f"{design_symbol["Reference"]} ({design}, {lib_name})",
                            "message": f"symbol has extra fields that are not in the library: {", ".join(diff)}"
                        })
                    # Fields missing in the design symbol
                    diff = list(set(lib_symbol.keys()) - set(design_symbol.keys()))
                    diff.remove("Name")
                    diff.remove("Extends")
                    if "Notes" in diff:
                        diff.remove("Notes")
                    # Special parts
                    if ("_do_not_populate_" in lib_name or lib_name.startswith("logo_") or
                            design_symbol["Reference"].startswith("#PWR") or lib_name.startswith("test_point_")):
                        i = 0
                        while i < len(diff):
                            if diff[i] in cls.PART_MANDATORY_FIELDS:
                                diff.pop(i)
                                i = 0
                            else:
                                i += 1
                    if len(diff) > 0:
                        report_messages.append({
                            "item": f"{design_symbol["Reference"]} ({design}, {lib_name})",
                            "message": f"symbol has missing fields: {", ".join(diff)}"
                        })
                    # Check property values
                    for field in filter(lambda x: x not in cls.SKIP_SYMBOL_FIELDS, lib_symbol):
                        lib_value = lib_symbol[field]
                        design_value = design_symbol.get(field, None)
                        if field in cls.PART_MANDATORY_FIELDS and design_value is None:
                            design_value = lib_value
                        elif field == "Notes" and lib_value == "":
                            design_value = lib_value
                        elif field == "Reference":
                            reference = design_value[:len(lib_value)]
                            number = design_value[len(lib_value):]
                            if lib_value != reference:
                                report_messages.append({
                                    "item": f"{design_symbol["Reference"]} ({design}, {lib_name})",
                                    "message": f"reference field does not start with '{lib_value}'"
                                })
                            try:
                                int(number)
                            except ValueError:
                                report_messages.append({
                                    "item": f"{design_symbol["Reference"]} ({design}, {lib_name})",
                                    "message": f"numeric part of reference field is not numeric '{number}'"
                                })
                            # Prevent other messages for reference field
                            design_value = lib_value
                        if lib_value != design_value:
                            report_messages.append({
                                "item": f"{design_symbol["Reference"]} ({design}, {lib_name})",
                                "message": f"field value for field {field} not correct: '{design_value}'"
                            })

    @classmethod
    def _check_if_footprints_in_designs(cls, lib_footprints, designs, report_messages):
        for lib_footprint in lib_footprints:
            for design in designs:
                matches = list(filter(lambda x: x["Footprint"] == f"lily_footprints:{lib_footprint["Name"]}",
                                      designs[design]["footprints"]))
                if len(matches) > 0:
                    break
            else:
                report_messages.append({
                    "item": lib_footprint["Name"],
                    "message": "footprint is not in one of the projects"
                })

    @classmethod
    def _check_symbols_vs_footprints(cls, designs, report_messages):
        for design in designs:
            for design_symbol in designs[design]["symbols"]:
                if design_symbol["Reference"].startswith("#PWR"):
                    continue
                matches = list(filter(lambda x: x["Reference"] == design_symbol["Reference"],
                                      designs[design]["footprints"]))
                if len(matches) == 0:
                    report_messages.append({
                        "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                        "message": f"symbol has no matching footprint in the PCB design"
                    })
                else:
                    design_footprint = matches[0]
                    # print(design_symbol)
                    # print(design_footprint)
                    # Fields in the symbol but not in the footprint
                    diff = list(set(design_symbol.keys()) - set(design_footprint.keys()))
                    diff.remove("lib_id")
                    if len(diff) > 0:
                        report_messages.append({
                            "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                            "message": f"symbol has extra fields that are not in the footprint: {", ".join(diff)}"
                        })
                    # Fields in the footprint but not in the symbol
                    diff = list(set(design_footprint.keys()) - set(design_symbol.keys()))
                    if "Model" in diff:
                        diff.remove("Model")
                    if len(diff) > 0:
                        report_messages.append({
                            "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                            "message": f"footprint has extra fields that are not in the symbol: {", ".join(diff)}"
                        })
                    for field in filter(lambda x: x != "lib_id", design_symbol):
                        symbol_value = design_symbol[field]
                        footprint_value = design_footprint.get(field, None)
                        if symbol_value != footprint_value:
                            report_messages.append({
                                "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                                "message": f"value for field {field} in symbol is not matching with footprint"
                            })

            for design_footprint in designs[design]["footprints"]:
                matches = list(filter(lambda x: x["Reference"] == design_footprint["Reference"],
                                      designs[design]["symbols"]))
                if len(matches) == 0:
                    report_messages.append({
                        "item": f"{design_footprint["Reference"]} ({design_footprint["Footprint"]})",
                        "message": f"footprint has no matching symbol in the schematics design"
                    })


if __name__ == "__main__":

    _messages = ProjectsChecker.run()
    print(f"{len(_messages)} messages")
    for _message in _messages:
        print(_message)
