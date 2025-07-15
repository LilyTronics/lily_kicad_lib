"""
Build all the executables for the tool box.
"""

import os
import PyInstaller.__main__
import shutil

from app_data import AppData


def _clean_output_folder(output_folder):
    print("Clean output folder . . .")
    if os.path.isdir(output_folder):
        for item in os.listdir(output_folder):
            full_path = os.path.join(output_folder, item)
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
    else:
        os.makedirs(output_folder)


def _create_version_file(tool_box_path, version_file, version_tuple, version_string):
    version_template = os.path.join(tool_box_path, "templates", "app_version.template")

    print("Create version info file . . .")
    with open(version_template, "r", encoding="latin-1") as fp:
        version_template = fp.read()
        version_template = version_template.replace("{app_name}", AppData.APP_NAME)
        version_template = version_template.replace("{version_tuple}", str(version_tuple))
        version_template = version_template.replace("{version_string}", version_string)
        version_template = version_template.replace("{exe_name}", AppData.EXE_NAME)
        version_template = version_template.replace("{company_name}", AppData.COMPANY)

    with open(version_file, "w", encoding="latin-1") as fp:
        fp.write(version_template)


def create_executable():
    tool_box_path = os.path.dirname(__file__)

    lib_path = os.path.join(tool_box_path, "lib")
    output_folder = os.path.join(tool_box_path, "build_output")
    init_file = os.path.join(tool_box_path, "run_toolbox.py")
    icon_file = os.path.join(tool_box_path, "toolbox.ico")
    version_file = os.path.join(output_folder, "app.version")

    if os.path.isdir(lib_path):
        shutil.rmtree(lib_path)

    version_tuple = list(map(int, AppData.VERSION.split(".")))
    while len(version_tuple) < 4:
        version_tuple.append(0)

    _clean_output_folder(output_folder)
    _create_version_file(tool_box_path, version_file, version_tuple, AppData.VERSION)

    print("\nBuild tool:")
    print("Init file   :", init_file)
    print("Icon file   :", icon_file)
    print("Build folder:", output_folder)

    work_path = os.path.join(output_folder, "work")
    spec_path = os.path.join(output_folder, "spec")
    dist_path = os.path.join(output_folder, "dist")
    PyInstaller.__main__.run([
        init_file,
        "--clean",
        "--onedir",
        "--noconsole",
        f"--name={AppData.EXE_NAME}",
        f"--icon={icon_file}",
        f"--version-file={version_file}",
        "--contents=lib",
        f"--workpath={work_path}",
        f"--specpath={spec_path}",
        f"--distpath={dist_path}"
    ])

    # Copy lib and executable
    dist_lib_path = os.path.join(dist_path, AppData.EXE_NAME, "lib")
    exe_file = os.path.join(dist_path, AppData.EXE_NAME, f"{AppData.EXE_NAME}.exe")
    if os.path.isdir(dist_lib_path):
        shutil.copytree(dist_lib_path, lib_path, dirs_exist_ok=True)
    if os.path.isfile(exe_file):
        target = os.path.join(tool_box_path, f"{AppData.EXE_NAME}.exe")
        shutil.copy2(exe_file, target)

    # Remove build output
    shutil.rmtree(output_folder)


if __name__ == "__main__":

    create_executable()
