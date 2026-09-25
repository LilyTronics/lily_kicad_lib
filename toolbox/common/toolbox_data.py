"""
Toolbox data container.
"""

import os


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), *['..'] * 2))

FOOTPRINTS_LIB_PATH = os.path.join(ROOT_PATH, 'lily_footprints.pretty')
SYMBOLS_LIB_PATH = os.path.join(ROOT_PATH, 'lily_symbols', 'lily_symbols.kicad_sym')
MODELS_3D_PATH = os.path.join(ROOT_PATH, '3d_models')
TEST_PROJECTS_PATH = os.path.join(ROOT_PATH, 'test_projects')
LIB_TEST_PROJECTS_PATH = os.path.join(TEST_PROJECTS_PATH, 'lib_test')
TEMPLATES_PATH = os.path.join(ROOT_PATH, 'toolbox', 'templates')


if __name__ == '__main__':

    print('Root path             :', ROOT_PATH)
    print('Footprints lib path   :', FOOTPRINTS_LIB_PATH)
    print('Symbols lib path      :', SYMBOLS_LIB_PATH)
    print('3D models path        :', MODELS_3D_PATH)
    print('Test projects path    :', TEST_PROJECTS_PATH)
    print('Lib test projects path:', LIB_TEST_PROJECTS_PATH)
    print('Templates path        :', TEMPLATES_PATH)
