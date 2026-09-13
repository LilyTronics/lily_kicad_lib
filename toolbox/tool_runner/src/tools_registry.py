"""
Registry for the tools.
"""

import os

from importlib.util import module_from_spec
from importlib.util import spec_from_file_location

import toolbox.tool_runner.app_data as AppData


class ToolsRegistry:

    _tools = []

    _EXCLUDED_FILES = []

    def __init__(self):
        raise Exception("This class should not be instantiated")

    ###########
    # Private #
    ###########

    # Dummy callback in case the progress callback is None
    @staticmethod
    def _callback(*_):
        pass

    ##########
    # Public #
    ##########

    @classmethod
    def load(cls, progress_callback=None):
        if progress_callback is None:
            progress_callback = cls._callback
        del cls._tools[:]
        files = []
        progress_callback(-1, f"Load tools from: {AppData.TOOLS_PATH}")
        for current_path, subfolders, filenames in os.walk(AppData.TOOLS_PATH):
            if "__pycache__" in current_path:
                continue
            if not AppData.SHOW_TEMPLATE and "tool_template" in current_path:
                continue
            subfolders.sort()
            for filename in filenames:
                if filename == "tool_info.py":
                    full_path = os.path.join(current_path, filename)
                    files.append(full_path)
        total = len(files)
        progress_callback(-1, f"Load {total} tools")
        if total > 0:
            i = 0
            exceptions = []
            for i, filename in enumerate(files):
                rel_path = filename[len(AppData.TOOLS_PATH) + 1:]
                progress_callback(100 * i / total,
                                    f"Load tool from: {rel_path} ({i + 1}/{total})")
                name = os.path.basename(filename).split(".")[0]
                try:
                    spec = spec_from_file_location(name, str(filename))
                    module = module_from_spec(spec)
                    spec.loader.exec_module(module)
                    tool_info = getattr(module, "ToolInfo")
                    tool_info.path = os.path.dirname(filename)
                    cls._tools.append(tool_info)
                except Exception as e:
                    exceptions.append((rel_path, str(e)))
            progress_callback(100 * (i + 1) / total, f"Tools loaded ({i + 1}/{total})")
            if len(exceptions) > 0:
                message = "One or more tools are not loaded due to errors:"
                for path, error in exceptions:
                    message += f"\n{path}: {error}"
                raise Exception(message)

    @classmethod
    def get_tools(cls):
        return cls._tools


if __name__ == "__main__":

    ToolsRegistry.load(progress_callback=print)
    for tool in ToolsRegistry.get_tools():
        print(tool.name, tool.image, tool.path)
