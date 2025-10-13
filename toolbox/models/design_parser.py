"""
Parses a KiCad design.
"""

import glob
import os


class DesignParser:

    stdout = print

    @classmethod
    def _read_schematics(cls, project_folder):
        cls.stdout(f"Read schematics from: {project_folder}")
        lines = []
        for item in glob.glob(os.path.join(project_folder, "*.kicad_sch")):
            with open(item, "r") as fp:
                lines.extend(fp.readlines())
        return lines

    @classmethod
    def _read_pcb(cls, project_folder):
        lines = []
        items = glob.glob(os.path.join(project_folder, "*.kicad_pcb"))
        if len(items) == 1:
            cls.stdout(f"Read layout from: {items[0]}")
            with open(items[0], "r") as fp:
                lines = fp.readlines()
        return lines

    @classmethod
    def get_symbols(cls, project_folder):
        lines = cls._read_schematics(project_folder)
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
    def get_schematics_properties(cls, project_folder):
        properties = {
            "design_name": "",
            "date": "",
            "revision": "",
            "pca_id": "",
            "pcb_id": ""
        }
        lines = cls._read_schematics(project_folder)
        i = 0
        while i < len(lines):
            if lines[i] == "\t(title_block\n":
                while i < len(lines):
                    if lines[i].startswith("\t\t(title \""):
                        properties["design_name"] = lines[i].strip()[7:].strip(")").strip("\"")
                    if lines[i].startswith("\t\t(date \""):
                        properties["date"] = lines[i].strip()[6:].strip(")").strip("\"")
                    if lines[i].startswith("\t\t(rev \""):
                        properties["revision"] = lines[i].strip()[5:].strip(")").strip("\"")
                    if lines[i].startswith("\t\t(comment 1 \""):
                        properties["pca_id"] = lines[i].strip()[11:].strip(")").strip("\"")
                    if lines[i].startswith("\t\t(comment 2 \""):
                        properties["pcb_id"] = lines[i].strip()[11:].strip(")").strip("\"")
                    if lines[i] == "\t)\n":
                        break
                    i += 1
            i += 1
        return properties

    @classmethod
    def get_footprints(cls, project_folder):
        lines = cls._read_pcb(project_folder)
        i = 0
        footprints = []
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

    @classmethod
    def get_pcb_properties(cls, project_folder):
        properties = {
            "design_name": "",
            "date": "",
            "revision": "",
            "pca_id": "",
            "pcb_id": "",
            "n_layers": 0,
            "has_comp_bot": False
        }
        lines = cls._read_pcb(project_folder)
        i = 0
        while i < len(lines):
            if lines[i] == "\t(title_block\n":
                while i < len(lines):
                    if lines[i].startswith("\t\t(title \""):
                        properties["design_name"] = lines[i].strip()[7:].strip(")").strip("\"")
                    if lines[i].startswith("\t\t(date \""):
                        properties["date"] = lines[i].strip()[6:].strip(")").strip("\"")
                    if lines[i].startswith("\t\t(rev \""):
                        properties["revision"] = lines[i].strip()[5:].strip(")").strip("\"")
                    if lines[i].startswith("\t\t(comment 1 \""):
                        properties["pca_id"] = lines[i].strip()[11:].strip(")").strip("\"")
                    if lines[i].startswith("\t\t(comment 2 \""):
                        properties["pcb_id"] = lines[i].strip()[11:].strip(")").strip("\"")
                    if lines[i] == "\t)\n":
                        break
                    i += 1
            if lines[i] == "\t(layers\n":
                while i < len(lines):
                    if ".Cu\"" in lines[i]:
                        properties["n_layers"] += 1
                    if lines[i] == "\t)\n":
                        break
                    i += 1
            if lines[i].startswith("\t(footprint \""):
                while i < len(lines):
                    if lines[i] == "\t\t(layer \"B.Cu\")\n":
                        properties["has_comp_bot"] = True
                    if lines[i] == "\t)\n":
                        break
                    i += 1
            i += 1
        return properties

if __name__ == "__main__":

    _test_project_folder = "..\\..\\projects\\arduino_base"
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

    print("\nSchematics properties")
    print(DesignParser.get_schematics_properties(_test_project_folder))

    print("\nPCB properties")
    print(DesignParser.get_pcb_properties(_test_project_folder))
