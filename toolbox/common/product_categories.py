"""
ERP product categories
"""

import re


class Category():

    def __init__(self, name, product_id, part_name_matches, series=None):
        self.name = name
        self.product_id = product_id
        self.part_name_matches = part_name_matches
        self.series = [] if series is None else series


class ProductCategories:

    _CAPACITOR_SERIES = [
        '1, 0805 X7R 10%',
        '2, 1206 X7R 10%',
        '3, 0805 C0G 5%',
        '4, 1210 X7R 10%',
        '8, trimmer',
        '9, specials'
    ]

    _RESISTOR_SERIES = [
        '1, 0805 1% 125mW',
        '2, MF25 1% 150mW',
        '9, specials'
    ]

    _PRODUCT_CATEGORIES = [
        Category( 'connectors',             '1910-1xxxx', ( 'con_', )                    ),
        Category( 'diodes',                 '1911-1xxxx', ( 'dio_', )                    ),
        Category( 'capacitors',             '1912-value', ( 'cap_', ), _CAPACITOR_SERIES ),
        Category( 'resistors',              '1913-value', ( 'res_', ), _RESISTOR_SERIES  ),
        Category( 'integrated circuits',    '1914-1xxxx', ( 'ic_',  ),                   ),
        Category( 'LEDs',                   '1915-1xxxx', ( 'dio_led_', )                ),
        Category( 'inductors',              '1916-1xxxx', ( 'ind_', )                    ),
        Category( 'crystals / resonators',  '1917-1xxxx', ( 'crystal_', )                ),
        Category( 'transistors',            '1918-1xxxx', ( 'bjt', 'mosfet' )            ),
        Category( 'potmeters',              '1919-1xxxx', ( 'pot_', )                    ),
        Category( 'switches',               '1920-1xxxx', ( 'switch_', )                 ),
        Category( 'fuses',                  '1921-1xxxx', ( 'fuse_', )                   ),
    ]

    _VALUE_PATTERN = re.compile(r'_([0-9]+(?:[RkMmunp][0-9]*)?)_')

    @classmethod
    def get_categories(cls):
        return [ c.name for c in cls._PRODUCT_CATEGORIES ]

    @classmethod
    def get_category(cls, name):
        matches = [ c for c in cls._PRODUCT_CATEGORIES if c.name == name ]
        return None if len(matches) !=1 else matches[0]

    @staticmethod
    def generate_next_code(category, existing_codes, series, value):
        next_code = ''
        # Get index of series
        if ',' in series:
            series = series.split(',')[0]
        else:
            series = '0'
        product_id = category.product_id
        if series == '9':
            product_id = product_id.split('-')[0] + '-9xxxx'
        dash_index = product_id.index('-') + 1
        if product_id.endswith(('1xxxx', '9xxxx')):
            # Simple sequence
            for i in range(1, 10000):
                next_id = f'{product_id[:dash_index + 1]}{i:04d}'
                if next_id not in existing_codes:
                    next_code = next_id
                    break
        if product_id.endswith('1xxyy'):
            # Sequence with version number
            for i in range(101, 1000):
                next_id = f'{product_id[:dash_index]}{i:03d}01'
                if next_id not in existing_codes:
                    next_code = next_id
                    break
        if 'value' in product_id:
            # Convert value to code
            power = '-1'
            if 'p' in value or 'R' in value:
                value = value.replace('p', '.').replace('R', '.')
                if float(value) >= 1:
                    power = '0'
                if float(value) >= 10:
                    power = '1'
                if float(value) >= 100:
                    power = '2'
            elif 'n' in value or 'k' in value:
                value = value.replace('n', '.').replace('k', '.')
                if float(value) >= 1:
                    power = '3'
                if float(value) >= 10:
                    power = '4'
                if float(value) >= 100:
                    power = '5'
            elif 'u' in value or 'M' in value:
                value = value.replace('u', '.').replace('M', '.')
                if float(value) >= 1:
                    power = '6'
                if float(value) >= 10:
                    power = '7'
                if float(value) >= 100:
                    power = '8'
                if float(value) >= 1000:
                    power = '9'
            value = value.replace('.', '').lstrip('0')
            while len(value) < 3:
                value = f'{value}0'
            if len(value) > 3:
                value = value[:3]
            if power == '-1':
                value = f'0{value}'
            else:
                value = f'{value}{power}'
            next_code = f'{product_id[:dash_index]}{series}{value}'
        return next_code if next_code not in existing_codes else 'already exist'

    @classmethod
    def get_category_for_part(cls, part_name):
        series_name = ''
        value = ''
        matches = [
            (c, p)
            for c in cls._PRODUCT_CATEGORIES
            for p in c.part_name_matches
            if part_name.startswith(p)
        ]
        category = max(matches, key=lambda m: len(m[1]))[0] if matches else None
        if category is not None:
            for serie in category.series:
                parts = serie.split(', ')[-1].split(' ')
                found = 0
                for part in parts:
                    if part in part_name:
                        found += 1
                if found == len(parts):
                    series_name = serie
                    break
            if len(category.series) > 0:
                # We need a value
                m = cls._VALUE_PATTERN.search(part_name)
                if m:
                    value = m.group(1)
        return category, series_name, value


if __name__ == '__main__':

    _categories = ProductCategories.get_categories()
    print('Categories:', _categories)

    print('\nCatgegories:')
    for _name in [_categories[1], _categories[2], 'not_existing_category']:
        _category = ProductCategories.get_category(_name)
        if _category is not None:
            print(f'{_name}:', _category.name, _category.product_id, _category.series)
        else:
            print(f'{_name}:', _category)

    print('\nNext product code')
    _SERIES = '9, 0805 X7R 10%'
    _VALUE = '12n'
    _test_codes = {
        1: ['1911-10001', '1911-10002', '1911-10004'],
        2: ['1912-11003', '1912-11004', '1912-11005', '1912-11203'],
        # 23: ['2910-10101', '2910-10102', '2910-10201', '2910-10401'],
    }
    for _key, _value in _test_codes.items():
        _category = ProductCategories.get_category(_categories[_key])
        print(f'{_key}:', ProductCategories.generate_next_code(_category, _value, _SERIES, _VALUE))

    _test_names = [
        'cap_100n_50V_10%_X7R_0805',
        'dio_1N4148W_sod123',
        'dio_led_blue_KP-2012QBC-D_0805',
        'bjt_npn_BC850B_sot23',
        'mosfet_n_DMG3406L_sot23'
    ]
    for _part in _test_names:
        c, s, v = ProductCategories.get_category_for_part(_part)
        print(f'{_part}:', c.name, s, v)
