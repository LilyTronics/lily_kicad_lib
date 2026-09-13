"""
Build the executables for the tool runner.
"""

import os
import PyInstaller.__main__
import shutil

import app_data as AppData


def _create_output_folder(output_folder):
    print("Create output folder . . .")
    if os.path.isdir(output_folder):
        for item in os.listdir(output_folder):
            full_path = os.path.join(output_folder, item)
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
    else:
        os.makedirs(output_folder)

def _create_version_file(version_template, version_file):
    version_string = AppData.APP_VERSION
    version_tuple = list(map(int, version_string.split(".")))
    while len(version_tuple) < 4:
        version_tuple.append(0)

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

def _copy_build_output(source, target):
    if os.path.isdir(source):
        for item in os.listdir(source):
            full_path = os.path.join(source, item)
            target_path = os.path.join(target, item)
            if os.path.isfile(full_path):
                shutil.copy2(full_path, target)
            elif os.path.isdir(full_path):
                shutil.copytree(full_path, target_path, dirs_exist_ok=True)

def build_toolbox():
    tool_runner_path = os.path.dirname(__file__)
    toolbox_path = os.path.join(tool_runner_path, "..")
    output_folder = os.path.join(tool_runner_path, "..", "build_output")
    init_file = os.path.join(tool_runner_path, "main.py")
    icon_file = os.path.join(tool_runner_path, "artifacts", "toolbox.ico")
    version_template = os.path.join(tool_runner_path, "artifacts", "app_version.template")
    version_file = os.path.join(output_folder, "app.version")
    work_path = os.path.join(output_folder, "work")
    spec_path = os.path.join(output_folder, "spec")
    dist_path = os.path.join(output_folder, "dist")

    _create_output_folder(output_folder)
    _create_version_file(version_template, version_file)

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
        f"--distpath={dist_path}",
        # Add extra Python lib that are not standard included
        "--collect-submodules=wx"
    ])

    _copy_build_output(os.path.join(dist_path, AppData.EXE_NAME), toolbox_path)

    # Remove build output
    shutil.rmtree(output_folder)


if __name__ == "__main__":

    build_toolbox()
