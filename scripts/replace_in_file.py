"""
Replaces a section for another section in the whole file.
"""


search = ''''''

replace = ''''''

filename = "../symbols/lily_symbols.kicad_sym"

with open(filename, "r") as fp:
    content = fp.read()

with open(filename, "w") as fp:
    fp.write(content.replace(search, replace))
