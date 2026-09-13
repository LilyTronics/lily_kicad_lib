"""
We cannot have cross imports between the tool runner and the tools.
This wil break the application.
"""

import os


def check_imports():
    n_cross_imports = 0
    for cross_name in ("tools", "tool_runner"):
        cross_name = f"toolbox.{cross_name}"
        print(f"Check for imports from: {cross_name}")
        files = _get_files(cross_name)
        for file in files:
            n_cross_imports += _check_for_cross_imports(file, cross_name)
        print()
    print(f"Cross imports found: {n_cross_imports}")

def _get_files(folder_name):
    files = []
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 2, folder_name))
    print(f"Get files from: {path}")
    for current_dir, sub_folders, filenames in os.walk(path):
        if "__pycache__" in current_dir:
            continue
        sub_folders.sort()
        for filename in [f for f in filenames if f.endswith(".py")]:
            files.append(os.path.join(current_dir, filename))
    return files

def _check_for_cross_imports(filename, cross_name):
    cross_imports = []
    with open(filename, "r", encoding="utf-8") as fp:
        for line in fp.readlines():
            if line.lstrip().startswith("#"):
                continue
            if f"import {cross_name}" in line or f"from {cross_name}" in line:
                cross_imports.append(line.strip())
    if len(cross_imports) > 0:
        print(f"File: {filename}")
        for ci in cross_imports:
            print(f"  - {ci}")
    return len(cross_imports)


if __name__ == "__main__":

    check_imports()
