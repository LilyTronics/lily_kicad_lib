"""
Process a KiCad design.
"""

import os
import shutil

from pathlib import Path
from toolbox.common.checkers.projects_checker import ProjectsChecker
from toolbox.common.parsers.design_parser import DesignParser
from toolbox.tools.process_design.src.copy_design import copy_design
from toolbox.tools.process_design.src.output_generator import OutputGenerator
from toolbox.tools.process_design.src.process_context import ProcessContext


def process_design(context: ProcessContext, report, logger):
    # Clear PCA folder
    for item in Path(context.pca_folder).iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    # Create output folder
    context.output_folder = os.path.join(context.pca_folder, 'output')
    os.makedirs(context.output_folder)

    # Check design
    ProjectsChecker.stdout = logger
    messages = ProjectsChecker.check_project(context.project_folder)
    report.extend([ f'WARNING: {m['item']} - {m['message']}' for m in messages ])

    # Check properties, TODO: add to new design checker
    sch_props = DesignParser.get_schematics_properties(context.project_folder)
    report.append('\nSchematics properties:')
    for key, value in sch_props.items():
        report.append(f'{key}: {value}')
    pcb_props = DesignParser.get_pcb_properties(context.project_folder)
    report.append('\nPCB properties:')
    for key, value in pcb_props.items():
        report.append(f'{key}: {value}')
    for prop in ['design_name', 'date', 'revision', 'pca_id', 'pcb_id']:
        if sch_props[prop] != pcb_props[prop]:
            report.append(f'WARNING: the {prop.replace('_', ' ')} is not equal between the '
                            'schematics and the PCB')

    # Generate output
    OutputGenerator.run(context, report, logger)

    # Copy design files
    copy_design(context, report, logger)


if __name__ == '__main__':

    from toolbox.tools.process_design.src.process_context import test_context

    _messages = []
    process_design(test_context(), _messages, print)
    for m in _messages:
        print(m)
