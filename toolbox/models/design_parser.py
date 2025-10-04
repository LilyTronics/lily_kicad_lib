"""
Parses the test design.
"""

import glob
import os


class DesignParser:

    stdout = print

    @classmethod
    def get_symbols(cls, project_folder):
        cls.stdout(f"Read schematics from: {project_folder}")
        lines = []
        for item in glob.glob(os.path.join(project_folder, "*.kicad_sch")):
            with open(item, "r") as fp:
                lines.extend(fp.readlines())
        symbols = []
        i = 0
        while i < len(lines):
            if lines[i].startswith("\t(symbol"):
                symbol = {}
                references = []
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
                    if lines[i] == "\t\t(instances\n":
                        # Sheet is used multiple times.
                        while i < len(lines):
                            i += 1
                            if lines[i].startswith("\t\t\t\t\t(reference "):
                                references.append(lines[i].strip()[11:].strip(")").strip('"'))
                            if lines[i] == "\t\t)\n":
                                break

                symbols.append(symbol)
                if len(references) > 1:
                    # Add extra symbols
                    for reference in references:
                        if reference != symbol["Reference"]:
                            extra_symbol = symbol.copy()
                            extra_symbol["Reference"] = reference
                            symbols.append(extra_symbol)

            i += 1
        return symbols

    @classmethod
    def get_footprints(cls, project_folder):
        footprints = []
        items = glob.glob(os.path.join(project_folder, "*.kicad_pcb"))
        if len(items) == 1:
            pcb_filename = items[0]
            cls.stdout(f"Read layout from: {pcb_filename}")
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
                        if lines[i].startswith("\t\t(attr "):
                            footprint["Attributes"] = lines[i].strip()[6:].strip(")").split(" ")
                        if lines[i].startswith("\t\t(model "):
                            footprint["Model"] = lines[i].strip()[7:].strip(")").strip('"')
                        if lines[i].startswith('\t\t(fp_text user "${REFERENCE}"'):
                            footprint["Reference_F.Fab"] = lines[i].strip()[14:].strip('"')
                    footprints.append(footprint)
                i += 1
        return footprints


if __name__ == "__main__":

    _test_project_folder = "..\\..\\projects\\lib_test\\capacitors"
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
