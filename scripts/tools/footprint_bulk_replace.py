"""
Replace stuff in all footprints.
Use with caution and check carefully.
"""

import glob
import os


query = "(thickness 0.15)"
replace_with = "(thickness 0.16)"

footprints_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lily_footprints.pretty"))

print(f"Path: {footprints_path}")

for filename in glob.glob(os.path.join(footprints_path, "*.kicad_mod")):
    print(f"Replace in {os.path.basename(filename)}")
    with open(filename, "r") as fp:
        content = fp.read()
    with open(filename, "w") as fp:
        fp.write(content.replace(query, replace_with))
