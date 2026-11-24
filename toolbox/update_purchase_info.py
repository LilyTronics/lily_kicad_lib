"""
Update purchase info from KiCad lib.
"""

import sys

from toolbox.common.erp_connect import get_components_from_erp
from toolbox.common.erp_connect import update_record_in_erp
from common.parsers.lib_parser import LibParser


result = get_components_from_erp(print)
print('ERP records:', len(result[1]))
if not result[0]:
    sys.exit(1)

symbols = LibParser.get_symbols()
print('Symbols:', len(symbols))

for part in result[1]:
    matches = [ s for s in symbols if s.get('Lily_ID') == part['default_code'] ]
    if len(matches) != 1:
        continue

    purchase_info = (matches[0].get('Manufacturer'), matches[0].get('Manufacturer_ID'))
    if None in purchase_info:
        continue

    purchase_info = ' - '.join(purchase_info)
    if purchase_info == part['description_purchase']:
        continue

    print(f'Update {part['name']} ({part['default_code']}) with {purchase_info}')
    result = update_record_in_erp(print, part['id'], {'description_purchase': purchase_info})
    print('Result:', result)
