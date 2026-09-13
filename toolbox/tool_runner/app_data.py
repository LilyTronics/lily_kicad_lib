"""
Application data.
"""

import os
import sys

from toolbox.tool_runner.src.os_specifics import get_user_data_dir


APP_NAME = "Lily KiCad Toolbox"
APP_VERSION = "4.0"
EXE_NAME = "LilyKiCadToolbox"
COMPANY  = "LilyTronics"
SHOW_TEMPLATE = False

# Application path depends on if run from script or from the executable
if EXE_NAME in sys.executable:
    APP_PATH = os.path.dirname(sys.executable)
    # We must add the application path for import tools in the executable
    sys.path.insert(0, str(APP_PATH))
else:
    APP_PATH = os.path.dirname(os.path.dirname(__file__))
    # Show the template tool when run from IDE
    SHOW_TEMPLATE = True

SETTINGS_FILE = os.path.join(get_user_data_dir(), EXE_NAME, f"{EXE_NAME}.json")
TOOLS_PATH = os.path.join(APP_PATH, "tools")
LOG_FILENAME = os.path.join(APP_PATH, f"{EXE_NAME}.log")


if __name__ == "__main__":

    print("App path     :", APP_PATH)
    print("Settings file:", SETTINGS_FILE)
    print("Tools path   :", TOOLS_PATH)
    print("Log filename :", LOG_FILENAME)
    print("Show template:", SHOW_TEMPLATE)
