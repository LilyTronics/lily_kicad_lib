"""
Checks the projects to the library.
"""

import os

from toolbox.app_data import AppData
from toolbox.models.parsers.design_parser import DesignParser
from toolbox.models.parsers.lib_parser import LibParser


class ProjectsChecker:

    stdout = print

    PROJECTS_PATH = os.path.join(AppData.APP_PATH, "projects")

    PART_MANDATORY_FIELDS = ["Status", "Manufacturer", "Manufacturer_ID", "Lily_ID", "JLCPCB_ID"]
    SKIP_SYMBOL_FIELDS = ["Name", "Extends"]
    # SKIP_LAYOUT_FIELDS = [] # ["Name", "Reference", "Value", "Footprint", "Datasheet"]

    @classmethod
    def run(cls):
        DesignParser.stdout = cls.stdout
        LibParser.stdout = cls.stdout

        project_folders = []
        report_messages = []
        for current_folder, sub_folders, filenames in os.walk(cls.PROJECTS_PATH):
            sub_folders.sort()
            matches = list(filter(lambda x: x.endswith(".kicad_pro"), filenames))
            if len(matches) == 1:
                project_folders.append(current_folder)

        report_messages.extend(cls.check_project(project_folders, True))

        return report_messages

    @classmethod
    def check_project(cls, project_folder, is_test_project=False):
        DesignParser.stdout = cls.stdout
        LibParser.stdout = cls.stdout
        cls.stdout("Check project against library")
        if isinstance(project_folder, str):
            project_folder = [project_folder]
        designs = {}
        for folder in project_folder:
            designs[folder[len(cls.PROJECTS_PATH) + 1:]] = {
                "symbols": DesignParser.get_symbols(folder),
                "footprints": DesignParser.get_footprints(folder)
            }

        lib_symbols = LibParser.get_symbols()
        lib_footprints = LibParser.get_footprints()

        report_messages = []

        # Test projects
        if is_test_project:
            cls._check_if_symbols_in_designs(lib_symbols, designs, report_messages)
            cls._check_if_footprints_in_designs(lib_footprints, designs, report_messages)

        # Regular projects
        cls._check_if_symbols_not_in_library(designs, lib_symbols, report_messages)
        cls._check_symbols_properties(designs, lib_symbols, report_messages)
        cls._check_if_footprints_not_in_library(designs, lib_footprints, report_messages)
        cls._check_footprint_properties(designs, lib_footprints, report_messages)
        cls._check_symbols_vs_footprints(designs, report_messages)

        return report_messages

    @classmethod
    def _check_if_symbols_in_designs(cls, lib_symbols, designs, report_messages):
        caller = f"({cls.__name__}._check_if_symbols_in_designs)"
        for lib_symbol in lib_symbols:
            should_be_used = (
                lib_symbol.get("Extends", None) is not None or      # Parts should be used in designs
                lib_symbol["Reference"] == "#PWR" or                # Power symbols should be used in designs
                lib_symbol["Name"].startswith("doc_") or            # Doc symbols should be used in designs
                lib_symbol["Name"] == "con_TC2030-IDC_lock"         # Specific symbol
            )

            is_used = False
            for design in designs:
                matches = list(filter(lambda x: x["lib_id"] == f"lily_symbols:{lib_symbol["Name"]}",
                                      designs[design]["symbols"]))

                # Only count if it is used if it is in one of the test designs
                if design.startswith("lib_test\\") and len(matches) > 0:
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
                    if "Extends" in diff:
                        diff.remove("Extends")
                    if "Notes" in diff:
                        diff.remove("Notes")
                    # Special parts, no mandatory fields
                    # Do not populate
                    if ("_do_not_populate_" in lib_name or
                            # Logos
                            lib_name.startswith("doc_logo_") or
                            # Power symbols
                            design_symbol["Reference"].startswith("#PWR") or
                            # Test points
                            lib_name.startswith("test_point_") or
                            # Cable to PCB connectors, footprint only, no physical component
                            (lib_name.startswith("con_") and "cable_to_pcb" in lib_name) or
                            # Programming cable TC2030, footprint only no physical component
                            lib_name.startswith("con_TC2030") or
                            # Mechanical holes
                            lib_name.startswith("mec_hole_") or
                            # Fiducials
                            lib_name.startswith("mec_fiducial")):
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
                        elif field == "Value":
                            # Values can be different in some cases
                            if lib_value == "Vxx" or lib_value.startswith("con_"):
                                lib_value = design_value
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
                    lib_footprint = matches[0]
                    lib_keys = list(lib_footprint.keys())
                    lib_keys.remove("Name")
                    design_keys = list(design_footprint.keys())
                    if "Footprint" in design_keys:
                        design_keys.remove("Footprint")
                    for field in cls.PART_MANDATORY_FIELDS:
                        if field in design_keys:
                            design_keys.remove(field)
                    # Fields in the lib but not in the design
                    diff = list(set(lib_keys) - set(design_keys))
                    if len(diff) > 0:
                        report_messages.append({
                            "item": f"{design_footprint["Reference"]["Value"]} ({design}, {lib_name})",
                            "message": f"footprint has missing fields: {", ".join(diff)} {caller}"
                        })
                    # Fields in the design but not in the lib
                    diff = list(set(design_keys) - set(lib_keys))
                    if len(diff) > 0:
                        report_messages.append({
                            "item": f"{design_footprint["Reference"]["Value"]} ({design}, {lib_name})",
                            "message": f"footprint has fields that are not in the library: {", ".join(diff)} {caller}"
                        })

                    # Check values
                    for property in lib_keys:
                        lib_value = lib_footprint[property]
                        design_value = design_footprint[property]
                        lib_instance = type(lib_value)
                        design_instance = type(design_value)
                        if lib_instance != design_instance:
                            report_messages.append({
                                "item": f"{design_footprint["Reference"]["Value"]} ({design}, {lib_name})",
                                "message": f"values are not of the same type: {design_instance}, expected {lib_instance} {caller}"
                            })
                        else:
                            if isinstance(lib_value, dict):
                                diff = {k: (lib_value[k], design_value[k]) for k in lib_value if lib_value[k] != design_value[k]}
                                # Value field is always different from library
                                for key in filter(lambda k: k not in ["Value"], diff):
                                    report_messages.append({
                                        "item": f"{design_footprint["Reference"]["Value"]} ({design}, {lib_name})",
                                        "message": f"property {property} has a different value for {key}: {diff[key]} {caller}"
                                    })
                            else:
                                if lib_value != design_value:
                                    report_messages.append({
                                        "item": f"{design_footprint["Reference"]["Value"]} ({design}, {lib_name})",
                                        "message": f"property {property} has a different value: {design_value}, expected: {lib_value} {caller}"
                                    })


    @classmethod
    def _check_symbols_vs_footprints(cls, designs, report_messages):
        caller = f"({cls.__name__}._check_symbols_vs_footprints)"
        for design in designs:
            for design_symbol in designs[design]["symbols"]:
                if design_symbol["Reference"].startswith("#PWR"):
                    continue
                matches = list(filter(lambda x: x["Reference"]["Value"] == design_symbol["Reference"],
                                      designs[design]["footprints"]))
                if len(matches) == 0:
                    report_messages.append({
                        "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                        "message": f"symbol has no matching footprint in the PCB design {caller}"
                    })
                else:
                    design_footprint = matches[0]
                    symbol_keys = list(design_symbol.keys())
                    symbol_keys.remove("lib_id")
                    footprint_keys = list(design_footprint.keys())
                    footprint_keys.remove("Reference_F.Fab")
                    footprint_keys.remove("Attributes")
                    if "Model" in footprint_keys:
                        footprint_keys.remove("Model")
                    if "Pin_1_mark" in footprint_keys:
                        footprint_keys.remove("Pin_1_mark")

                    # Fields in the symbol but not in the footprint
                    diff = list(set(symbol_keys) - set(footprint_keys))
                    if len(diff) > 0:
                        report_messages.append({
                            "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                            "message": f"symbol has fields that are not in the footprint: {", ".join(diff)} {caller}"
                        })
                    # Fields in the footprint but not in the symbol
                    diff = list(set(footprint_keys) - set(symbol_keys))
                    if len(diff) > 0:
                        report_messages.append({
                            "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                            "message": f"footprint has fields that are not in the symbol: {", ".join(diff)} {caller}"
                        })

                    # Check values
                    for property in symbol_keys:
                        symbol_value = design_symbol[property]
                        footprint_value = design_footprint[property]
                        if isinstance(footprint_value, dict):
                            footprint_value = footprint_value.get("Value", None)
                        if symbol_value != footprint_value:
                            report_messages.append({
                                "item": f"{design_symbol["Reference"]} ({design_symbol["lib_id"]})",
                                "message": f"value for field {property} in symbol is not matching with footprint: {footprint_value}, expected {symbol_value} {caller}"
                            })

            for design_footprint in designs[design]["footprints"]:
                if design_footprint["Reference"]["Value"] == "REF**":
                    continue
                matches = list(filter(lambda x: x["Reference"] == design_footprint["Reference"]["Value"],
                                      designs[design]["symbols"]))
                if len(matches) == 0:
                    report_messages.append({
                        "item": f"{design_footprint["Reference"]["Value"]} ({design_footprint["Footprint"]})",
                        "message": f"footprint has no matching symbol in the schematics design {caller}"
                    })


if __name__ == "__main__":

    from show_messages import show_messages

    show_messages(ProjectsChecker.run())
