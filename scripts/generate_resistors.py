"""
Generate resistor ranges from 1R to 9M1.
"""

import os

template_fie = os.path.join(os.path.dirname(__file__), "resistor_template.kicad_sym")
output_file = os.path.join(os.path.dirname(__file__), "output.txt")

package_id = "1"
package_name = "0805"
power = "125mW"
footprint = "res_0805"

values = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
]

factors = [
    {"unit": "R", "factor": 1,   "power_of_ten": "0"},
    {"unit": "R", "factor": 10,  "power_of_ten": "1"},
    {"unit": "R", "factor": 100, "power_of_ten": "2"},
    {"unit": "k", "factor": 1,   "power_of_ten": "3"},
    {"unit": "k", "factor": 10,  "power_of_ten": "4"},
    {"unit": "k", "factor": 100, "power_of_ten": "5"},
    {"unit": "M", "factor": 1,   "power_of_ten": "6"}
]


with open(template_fie, "r") as fp:
    template = fp.read()

total = 0
with open(output_file, "w") as fp:
    for factor in factors:
        for value in values:
            value = "{:.1f}".format(value * factor["factor"])
            res_value = value.replace(".", "")[:3]
            if len(res_value) < 3:
                res_value += "0"
            lily_id = package_id + res_value + factor["power_of_ten"]
            if len(value) > 3:
                value = value.replace(".0", "")
            if "." in value:
                value = value.replace(".", factor["unit"])
            else:
                value += factor["unit"]
            print(f"Write: {value} {power} {package_name} {footprint} {lily_id}")
            output = template.format(
                value=value,
                power=power,
                package=package_name,
                footprint=footprint,
                lily_id=lily_id
            )
            fp.write(f"{output.rstrip()}\n")
            total += 1

print(f"Generated {total} symbols")
