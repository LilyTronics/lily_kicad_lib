"""
Toolbox data container.
"""

import os


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), *['..'] * 2))


if __name__ == '__main__':

    print('Root path:', ROOT_PATH)
