"""
ERP product categories
"""


class Category():

    def __init__(self, name, product_id, series=None):
        self.name = name
        self.product_id = product_id
        self.series = [] if series is None else series


class ProductCategories:

    _CAPACITOR_SERIES = [
        '1, 0805 X7R 10%',
        '2, 1206 X7R 10%',
        '3, 0805 C0G/NP0 5%'
    ]

    _RESISTOR_SERIES = [
        '1, 0805 1% 125mW',
        '2, MF25 1% 150mW',
        '9, specials'
    ]

    _PRODUCT_CATEGORIES = [
        Category( 'connectors',             '1910-1xxxx'                    ),
        Category( 'diodes',                 '1911-1xxxx'                    ),
        Category( 'capacitors',             '1912-value', _CAPACITOR_SERIES ),
        Category( 'resistors',              '1913-value', _RESISTOR_SERIES  ),
        Category( 'integrated circuits',    '1914-1xxxx'                    ),
        Category( 'LEDs',                   '1915-1xxxx'                    ),
        Category( 'inductors',              '1916-1xxxx'                    ),
        Category( 'crystals / resonators',  '1917-1xxxx'                    ),
        Category( 'transistors',            '1918-1xxxx'                    ),
        Category( 'potmeters',              '1919-1xxxx'                    ),
        Category( 'switches',               '1920-1xxxx'                    )
    ]


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
        dash_index = category.product_id.index('-') + 1
        if category.product_id.endswith('1xxxx'):
            # Simple sequence
            for i in range(10001, 100000):
                next_id = f'{category.product_id[:dash_index]}{i:05d}'
                if next_id not in existing_codes:
                    next_code = next_id
                    break
        if category.product_id.endswith('1xxyy'):
            # Sequence with version number
            for i in range(101, 1000):
                next_id = f'{category.product_id[:dash_index]}{i:03d}01'
                if next_id not in existing_codes:
                    next_code = next_id
                    break
        if 'value' in category.product_id:
            # Generate product code based on series and value
            if ',' in series:
                series = series.split(',')[0]
            else:
                series = '0'
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
            next_code = f'{category.product_id[:dash_index]}{series}{value}'
        return next_code if next_code not in existing_codes else 'already exist'


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
    _SERIES = '1,0805 X7R 10%'
    _VALUE = '1n'
    _test_codes = {
        1: ['1911-10001', '1911-10002', '1911-10004'],
        2: ['1912-11003', '1912-11004', '1912-11005', '1912-11203'],
        # 23: ['2910-10101', '2910-10102', '2910-10201', '2910-10401'],
    }
    for _key, _value in _test_codes.items():
        _category = ProductCategories.get_category(_categories[_key])
        print(f'{_key}:', ProductCategories.generate_next_code(_category, _value, _SERIES, _VALUE))
