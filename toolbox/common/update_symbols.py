"""
Update a symbol.
"""

import os
import re

import toolbox.common.toolbox_data as ToolboxData


def update_symbol_property(name, param, value):
    filename = os.path.join(ToolboxData.SYMBOLS_LIB_PATH)
    with open(filename, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith('\t(symbol ') and f'"{name}"' in lines[i]:
            while i < len(lines):
                i += 1
                if f'\t\t(property "{param}"' in lines[i]:
                    lines[i] = re.sub(
                        r'(\(property\s+"[^"]+"\s+)"[^"]*"',
                        rf'\1"{value}"',
                        lines[i]
                    )
                if lines[i].startswith('\t)'):
                    break
        i += 1
    with open(filename, 'w', encoding='utf-8') as fp:
        fp.writelines(lines)


if __name__ == '__main__':

    update_symbol_property('bjt_npn_BC850B_sot23', 'Lily_ID', '1234-12345')
