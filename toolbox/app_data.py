"""
Application data
"""

import os
import sys


class AppData:
    APP_NAME = "Lily KiCad Toolbox"
    VERSION = "2.4"
    EXE_NAME = "LilyKiCadToolbox"
    COMPANY = "LilyTronics"
    # Application path depends on if run from script or from the executable
    if EXE_NAME in sys.executable:
        APP_PATH = os.path.dirname(sys.executable)
    else:
        APP_PATH = os.path.dirname(__file__)
    APP_PATH = os.path.dirname(APP_PATH)


if __name__ == "__main__":

    print("App name   :", AppData.APP_NAME)
    print("App version:", AppData.VERSION)
    print("Exe name   :", AppData.EXE_NAME)
    print("App folder :", AppData.APP_PATH)
