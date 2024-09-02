"""
Parses the test design.
"""

import glob
import os


class DesignParser:

    SCRIPT_PATH = os.path.dirname(__file__)
    TEST_DESIGN_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, "..", "..", "lib_test"))

    @classmethod
    def get_symbols(cls, project_folder):
        print(f"Read schematics from: {project_folder}")
        lines = []
        for item in glob.glob(os.path.join(project_folder, "*.kicad_sch")):
            with open(item, "r") as fp:
                lines.extend(fp.readlines())
        symbols = []
        i = 0
        while i < len(lines):
            if lines[i].startswith("\t(symbol"):
                symbol = {}
                while i < len(lines):
                    i += 1
                    if lines[i].startswith("\t)"):
                        break
                    if lines[i].startswith("\t\t(lib_id "):
                        symbol["lib_id"] = lines[i].strip()[8:].strip(")").strip('"')
                    if lines[i].startswith("\t\t(property "):
                        parts = lines[i].strip()[10:].split('" "')
                        if len(parts) == 2:
                            symbol[parts[0].strip('"')] = parts[1].strip().strip('"')
                symbols.append(symbol)
            i += 1
        return symbols

    @classmethod
    def get_footprints(cls, project_folder):
        footprints = []
        items = glob.glob(os.path.join(project_folder, "*.kicad_pcb"))
        if len(items) == 1:
            pcb_filename = items[0]
            print(f"Read layout from: {pcb_filename}")
            with open(pcb_filename, "r") as fp:
                lines = fp.readlines()
            i = 0
            while i < len(lines):
                if lines[i].startswith("\t(footprint "):
                    footprint = {
                        "Footprint": lines[i].strip()[11:].strip(")").strip('"')
                    }
                    while i < len(lines):
                        i += 1
                        if lines[i].startswith("\t)"):
                            break
                        if lines[i].startswith("\t\t(property "):
                            parts = lines[i].strip()[10:].split('" "')
                            if len(parts) == 2:
                                footprint[parts[0].strip('"')] = parts[1].strip().strip('"')
                        if lines[i].startswith("\t\t(model "):
                            footprint["Model"] = lines[i].strip()[7:].strip(")").strip('"')
                    footprints.append(footprint)
                i += 1
        return footprints


if __name__ == "__main__":

    _test_project_folder = "..\\..\\projects\\lib_test"
    _symbols = DesignParser.get_symbols(_test_project_folder)
    print("Symbols:", len(_symbols))
    if len(_symbols) > 0:
        print("Showing max 10 symbols:")
        for _symbol in _symbols[:10]:
            print(_symbol)

    _footprints = DesignParser.get_footprints(_test_project_folder)
    print("\nFootprints:", len(_footprints))
    if len(_footprints) > 0:
        print("Showing max 10 footprints:")
        for _footprint in _footprints[:10]:
            print(_footprint)
