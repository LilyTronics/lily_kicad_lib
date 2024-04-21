"""
Generate resistor ranges from 1R to 9M1.
"""

import os

template_fie = os.path.join(os.path.dirname(__file__), "capacitor_template.kicad_sym")
output_file = os.path.join(os.path.dirname(__file__), "output.txt")

package_name = "0805"
footprint = "cap_0805"

values = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

factors = [
    {"unit": "p", "factor": 1,   "tolerance": "5",  "type": "C0G", "package_id": "3", "lily_power": "0"},
    {"unit": "p", "factor": 10,  "tolerance": "5",  "type": "C0G", "package_id": "3", "lily_power": "1"},
    {"unit": "p", "factor": 100, "tolerance": "5",  "type": "C0G", "package_id": "3", "lily_power": "2"},
    {"unit": "n", "factor": 1,   "tolerance": "10", "type": "X7R", "package_id": "1", "lily_power": "3"},
    {"unit": "n", "factor": 10,  "tolerance": "10", "type": "X7R", "package_id": "1", "lily_power": "4"},
    {"unit": "n", "factor": 100, "tolerance": "10", "type": "X7R", "package_id": "1", "lily_power": "5"}
]

with open(template_fie, "r") as fp:
    template = fp.read()

total = 0
with open(output_file, "w") as fp:
    for factor in factors:
        for value in values:
            value = "{:.1f}".format(value * factor["factor"])
            cap_value = value.replace(".", "")[:3]
            if len(cap_value) < 3:
                cap_value += "0"
            lily_id = factor["package_id"] + cap_value + factor["lily_power"]
            if len(value) > 3:
                value = value.replace(".0", "")
            if "." in value:
                value = value.replace(".", factor["unit"])
            else:
                value += factor["unit"]
            print(f"Write: {value} {package_name} {footprint} {lily_id}")
            output = template.format(
                value=value,
                tolerance=factor["tolerance"],
                type=factor["type"],
                package=package_name,
                footprint=footprint,
                lily_id=lily_id
            )
            fp.write(f"{output.rstrip()}\n")
            total += 1

print(f"Generated {total} symbols")
