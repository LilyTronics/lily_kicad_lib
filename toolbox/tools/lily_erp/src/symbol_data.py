"""
Model containing symbol data for the ERP tool.
"""

from toolbox.common.parsers.lib_parser import LibParser


def get_erp_parts():
    symbols = LibParser.get_symbols()
    # Filter parts for ERP
    parts = []
    for symbol in symbols:
        if 'Lily_ID' in symbol:
            parts.append(symbol)
    # Firts sort by ID, then by name
    return sorted(parts, key=lambda x: (x["Lily_ID"], x["Name"]))


if __name__ == '__main__':

    for part in get_erp_parts():
        print(part['Lily_ID'], part['Name'])
