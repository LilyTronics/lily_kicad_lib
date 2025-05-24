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
    SKIP_LAYOUT_FIELDS = ["Name", "Reference", "Value", "Footprint"]

    @classmethod
    def run(cls):
        designs = {}
        for current_folder, sub_folders, filenames in os.walk(cls.PROJECTS_PATH):
            sub_folders.sort()
            matches = list(filter(lambda x: x.endswith(".kicad_pro"), filenames))
            if len(matches) == 1:
                # Get symbols and footprints from the project
                rel_path = current_folder.replace(cls.PROJECTS_PATH, "").strip("\\")
                print(rel_path)
                designs[rel_path] = {
                    "symbols": DesignParser.get_symbols(current_folder),
                    "footprints": DesignParser.get_footprints(current_folder)
                }
        lib_symbols = LibParser.get_symbols()
        lib_footprints = LibParser.get_footprints()

        report_messages = []
        cls._check_if_symbols_in_designs(lib_symbols, designs, report_messages)
        cls._check_if_symbols_not_in_library(designs, lib_symbols, report_messages)
        cls._check_symbols_properties(designs, lib_symbols, report_messages)
        cls._check_if_footprints_in_designs(lib_footprints, designs, report_messages)
        cls._check_if_footprints_not_in_library(designs, lib_footprints, report_messages)
        cls._check_footprint_properties(designs, lib_footprints, report_messages)
        cls._check_symbols_vs_footprints(designs, report_messages)

        return report_messages

    @classmethod
    def _check_if_symbols_in_designs(cls, lib_symbols, designs, report_messages):
        caller = f"({cls.__name__}._check_if_symbols_in_designs)"
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
                        "message": f"symbol should not be in the project {design} {caller}"
                    })

            if should_be_used and not is_used:
                report_messages.append({
                    "item": lib_symbol["Name"],
                    "message": f"symbol is not in one of the projects {caller}"
                })

    @classmethod
    def _check_if_symbols_not_in_library(cls, designs, lib_symbols, report_messages):
        caller = f"({cls.__name__}._check_if_symbols_not_in_library)"
        for design in designs:
            for design_symbol in designs[design]["symbols"]:
                lib_name = design_symbol["lib_id"].split(":")[1]
                matches = list(filter(lambda x: x["Name"] == lib_name, lib_symbols))
                if len(matches) == 0:
                    report_messages.append({
                        "item": lib_name,
                        "message": f"symbol in project {design} is not in the library {caller}"
                    })

    @classmethod
    def _check_symbols_properties(cls, designs, lib_symbols, report_messages):
        caller = f"({cls.__name__}._check_symbols_properties)"
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
                            "message": f"symbol has fields that are not in the library: {", ".join(diff)} {caller}"
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
                            "message": f"symbol has missing fields: {", ".join(diff)} {caller}"
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
                                    "message": f"reference field does not start with '{lib_value}' {caller}"
                                })
                            try:
                                int(number)
                            except ValueError:
                                report_messages.append({
                                    "item": f"{design_symbol["Reference"]} ({design}, {lib_name})",
                                    "message": f"numeric part of reference field is not numeric '{number}' {caller}"
                                })
                            # Prevent other messages for reference field
                            design_value = lib_value
                        if lib_value != design_value:
                            report_messages.append({
                                "item": f"{design_symbol["Reference"]} ({design}, {lib_name})",
                                "message": f"field value for field {field} not correct: '{design_value}' {caller}"
                            })

    @classmethod
    def _check_if_footprints_in_designs(cls, lib_footprints, designs, report_messages):
        caller = f"({cls.__name__}._check_if_footprints_in_designs)"
        for lib_footprint in lib_footprints:
            for design in designs:
                matches = list(filter(lambda x: x["Footprint"] == f"lily_footprints:{lib_footprint["Name"]}",
                                      designs[design]["footprints"]))
                if len(matches) > 0:
                    break
            else:
                report_messages.append({
                    "item": lib_footprint["Name"],
                    "message": f"footprint is not in one of the projects {caller}"
                })

    @classmethod
    def _check_if_footprints_not_in_library(cls, designs, lib_footprints, report_messages):
        caller = f"({cls.__name__}._check_if_footprints_not_in_library)"
        for design in designs:
            for design_footprint in designs[design]["footprints"]:
                lib_name = design_footprint["Footprint"].split(":")[1]
                matches = list(filter(lambda x: x["Name"] == lib_name, lib_footprints))
                if len(matches) == 0:
                    report_messages.append({
                        "item": lib_name,
                        "message": f"footprint in project {design} is not in the library {caller}"
                    })

    @classmethod
    def _check_footprint_properties(cls, designs, lib_footprints, report_messages):
        caller = f"({cls.__name__}._check_footprint_properties)"
        for design in designs:
            for design_footprint in designs[design]["footprints"]:
                lib_name = design_footprint["Footprint"].split(":")[1]
                matches = list(filter(lambda x: x["Name"] == lib_name, lib_footprints))
                if len(matches) > 0:
                    for key in matches[0]:
                        if key in cls.SKIP_LAYOUT_FIELDS:
                            continue
                        lib_value = matches[0].get(key, "invalid lib key")
                        if isinstance(lib_value, dict):
                            lib_value = lib_value.get("Value", "no value key")
                        design_value = design_footprint.get(key, "invalid design key")
                        if design_footprint["Value"].startswith("logo_") and key in ["Model", "Reference_F.Fab"]:
                            design_value = lib_value
                        if lib_value != design_value:
                            report_messages.append({
                                "item": lib_name,
                                "message": f"footprint in project {design} has invalid property: "
                                           f"{key}: '{design_value}' expected '{lib_value}' {caller}"
                            })
                break

    @classmethod
    def _check_symbols_vs_footprints(cls, designs, report_messages):
        caller = f"({cls.__name__}._check_symbols_vs_footprints)"
        for design in designs:
            for design_symbol in designs[design]["symbols"]:
                if design_symbol["Reference"].startswith("#PWR"):
                    continue
                matches = list(filter(lambda x: x["Reference"] == design_symbol["Reference"],
                                      designs[design]["footprints"]))
                if len(matches) == 0:
                    report_messages.append({
                        "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                        "message": f"symbol has no matching footprint in the PCB design {caller}"
                    })
                else:
                    design_footprint = matches[0]
                    # Fields in the symbol but not in the footprint
                    diff = list(set(design_symbol.keys()) - set(design_footprint.keys()))
                    diff.remove("lib_id")
                    if len(diff) > 0:
                        report_messages.append({
                            "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                            "message": f"symbol has fields that are not in the footprint: {", ".join(diff)} {caller}"
                        })
                    # Fields in the footprint but not in the symbol
                    diff = list(set(design_footprint.keys()) - set(design_symbol.keys()))
                    if "Model" in diff:
                        diff.remove("Model")
                    if "Reference_F.Fab" in diff:
                        diff.remove("Reference_F.Fab")
                    if "Attributes" in diff:
                        diff.remove("Attributes")
                    if len(diff) > 0:
                        report_messages.append({
                            "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                            "message": f"footprint has fields that are not in the symbol: {", ".join(diff)} {caller}"
                        })
                    for field in filter(lambda x: x != "lib_id", design_symbol):
                        symbol_value = design_symbol[field]
                        footprint_value = design_footprint.get(field, None)
                        if symbol_value != footprint_value:
                            report_messages.append({
                                "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                                "message": f"value for field {field} in symbol is not matching with footprint {caller}"
                            })

            for design_footprint in designs[design]["footprints"]:
                matches = list(filter(lambda x: x["Reference"] == design_footprint["Reference"],
                                      designs[design]["symbols"]))
                if len(matches) == 0:
                    report_messages.append({
                        "item": f"{design_footprint["Reference"]} ({design_footprint["Footprint"]})",
                        "message": f"footprint has no matching symbol in the schematics design {caller}"
                    })


if __name__ == "__main__":

    _messages = ProjectsChecker.run()
    print(f"{len(_messages)} messages")
    for _message in _messages:
        print(_message)
