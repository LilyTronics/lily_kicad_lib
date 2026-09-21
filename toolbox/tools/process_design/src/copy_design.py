"""
Copy design files.
"""

import glob
import os
import shutil

from toolbox.tools.process_design.src.process_context import ProcessContext


def copy_design(context: ProcessContext, report, logger):
    logger("Copy design files")
    report.append("\nCopy design files")
    # Copy project file
    design_filename = os.path.join(context.project_folder, f'{context.design_name}.kicad_pro')
    target = str(os.path.join(context.pca_folder, os.path.basename(design_filename)))
    report.append(f"Copy: {design_filename}")
    report.append(f"To  : {target}")
    shutil.copy2(design_filename, target)
    # Copy schematics
    for item in glob.glob(os.path.join(context.project_folder, "*.kicad_sch")):
        target = str(os.path.join(context.pca_folder, os.path.basename(item)))
        report.append(f"Copy: {item}")
        report.append(f"To  : {target}")
        shutil.copy2(item, target)
    # Copy layout
    for item in glob.glob(os.path.join(context.project_folder, "*.kicad_pcb")):
        target = str(os.path.join(context.pca_folder, os.path.basename(item)))
        report.append(f"Copy: {item}")
        report.append(f"To  : {target}")
        shutil.copy2(item, target)
    # Special files if they exist
    # Design rules
    item = design_filename.replace(".kicad_pro", ".kicad_dru")
    if os.path.isfile(item):
        target = str(os.path.join(context.pca_folder, os.path.basename(item)))
        report.append(f"Copy: {item}")
        report.append(f"To  : {target}")
        shutil.copy2(item, target)
    # Custom symbol library table
    item = os.path.join(context.project_folder, "sym-lib-table")
    if os.path.isfile(item):
        target = str(os.path.join(context.pca_folder, os.path.basename(item)))
        report.append(f"Copy: {item}")
        report.append(f"To  : {target}")
        shutil.copy2(item, target)
    # Custom footprint library table
    item = os.path.join(context.project_folder, "fp-lib-table")
    if os.path.isfile(item):
        target = str(os.path.join(context.pca_folder, os.path.basename(item)))
        report.append(f"Copy: {item}")
        report.append(f"To  : {target}")
        shutil.copy2(item, target)


if __name__ == '__main__':

    from toolbox.tools.process_design.src.process_context import test_context

    _messages = []
    copy_design(test_context(), _messages, print)
    for m in _messages:
        print(m)
