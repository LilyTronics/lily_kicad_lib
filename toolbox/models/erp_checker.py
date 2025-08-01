"""
Class that checks the library against the ERP database
"""

from toolbox.models.erp_connect import get_components_from_erp
from toolbox.models.lib_parser import LibParser


class ErpChecker:

    stdout = print

    @staticmethod
    def lib_filter(comp):
        return (
            comp["Lily_ID"] != "NO_ID" and
            comp["Reference"] != "#PWR" and
            comp["Extends"] != "" and
            comp["Value"] not in ["dnp", "test_point"] and
            "_cable_to_pcb_" not in comp["Value"] and
            not comp["Value"].startswith("mec_hole_")
        )

    @classmethod
    def run(cls):
        cls.stdout("Check ERP components against library components")
        report_messages = []
        erp_components = []
        result = get_components_from_erp(cls.stdout)
        if result[0]:
            erp_components = result[1]
        lib_components = list(filter(lambda c: cls.lib_filter(c), LibParser.get_symbols()))
        # Make name format in library components same as the name in the ERP database
        lib_components = [{**c, "Name": c["Name"].replace("_", " ")} for c in lib_components]
        cls.stdout(f"Checking {len(erp_components)} ERP components")
        cls.stdout(f"Checking {len(lib_components)} library components")
        cls._check_lib_to_erp(lib_components, erp_components, report_messages)
        cls._check_erp_to_lib(erp_components, lib_components, report_messages)
        return report_messages

    @classmethod
    def _check_lib_to_erp(cls, lib_components, erp_components, report_messages):
        caller = f"({cls.__name__}._check_lib_to_erp)"
        # Check if library component is available in the ERP database
        for lib_comp in lib_components:
            # Check by ID
            matches = list(filter(lambda c: c["default_code"] == lib_comp["Lily_ID"], erp_components))
            if len(matches) > 1:
                # Duplicate ID
                report_messages.append({
                    "item": lib_comp["Lily_ID"],
                    "message": f"multiple components in the ERP database for this ID {caller}"
                })
                for match in matches:
                    report_messages.append({
                        "item": "",
                        "message": f" - {match}"
                    })
            elif len(matches) == 1:
                # Check if name is correct
                if lib_comp["Name"] != matches[0]["name"]:
                    report_messages.append({
                        "item": lib_comp["Lily_ID"],
                        "message": f"the name of component is not matching {caller}"
                    })
                    report_messages.append({
                        "item": "",
                        "message": f" - name in lib: {lib_comp["Name"]}"
                    })
                    report_messages.append({
                        "item": "",
                        "message": f" - name in ERP: {matches[0]["name"]}"
                    })
            else:
                # ID not found, try to find by name
                matches = list(filter(lambda c: c["name"] == lib_comp["Name"], erp_components))
                if len(matches) > 1:
                    # Multiple components with the same name found
                    report_messages.append({
                        "item": lib_comp["Name"],
                        "message": f"multiple components in the ERP database for this name {caller}"
                    })
                    for match in matches:
                        report_messages.append({
                            "item": "",
                            "message": f" - {match}"
                        })
                elif len(matches) == 1:
                    # Check ID
                    if lib_comp["Lily_ID"] != matches[0]["default_code"]:
                        report_messages.append({
                            "item": lib_comp["Name"],
                            "message": f"the ID of the component is not matching {caller}"
                        })
                        report_messages.append({
                            "item": "",
                            "message": f" - ID in lib: {lib_comp["Lily_ID"]}"
                        })
                        report_messages.append({
                            "item": "",
                            "message": f" - ID in ERP: {matches[0]["default_code"]}"
                        })
                else:
                    # No match
                    report_messages.append({
                        "item": lib_comp["Name"],
                        "message": f"no match for this component {caller}"
                    })

    @classmethod
    def _check_erp_to_lib(cls, erp_components, lib_components, report_messages):
        caller = f"({cls.__name__}._check_erp_to_lib)"
        # Check if ERP components are missing in the library
        for erp_comp in erp_components:
            # Check by ID
            matches = list(filter(lambda c: c["Lily_ID"] == erp_comp["default_code"], lib_components))
            if len(matches) > 1:
                # Duplicate ID
                report_messages.append({
                    "item": erp_comp["default_code"],
                    "message": f"multiple components in the library for this ID {caller}"
                })
                for match in matches:
                    report_messages.append({
                        "item": "",
                        "message": f" - {match}"
                    })
            elif len(matches) < 1:
                # ID not found, try to find by name
                matches = list(filter(lambda c: c["Name"] == erp_comp["name"], lib_components))
                if len(matches) > 1:
                    # Multiple components with the same name found
                    report_messages.append({
                        "item": erp_comp["name"],
                        "message": f"multiple components in the library for this name {caller}"
                    })
                    for match in matches:
                        report_messages.append({
                            "item": "",
                            "message": f" - {match}"
                        })
                elif len(matches) == 1:
                    # Check ID
                    if erp_comp["default_code"] != matches[0]["Lily_ID"]:
                        report_messages.append({
                            "item": erp_comp["name"],
                            "message": f"the ID of the component is not matching {caller}"
                        })
                        report_messages.append({
                            "item": "",
                            "message": f" - ID in ERP: {erp_comp["default_code"]}"
                        })
                        report_messages.append({
                            "item": "",
                            "message": f" - ID in lib: {matches[0]["Lily_ID"]}"
                        })
                else:
                    # No match
                    report_messages.append({
                        "item": erp_comp["name"],
                        "message": f"no match for this component {caller}"
                    })


if __name__ == "__main__":

    messages = ErpChecker.run()
    print(f"{len(messages)} messages")
    for message in messages:
        print(message)
