"""
Process context class.
"""

import os
import shutil

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path

import toolbox.common.toolbox_data as ToolboxData


@dataclass
class ProcessContext:
    timestamp: str
    project_folder: str = ''
    design_name: str = ''
    sch_filename: str = ''
    pcb_filename: str = ''
    pca_folder: str = ''
    output_folder: str = ''
    outputs: tuple = field(default_factory=tuple)
    bom_options: tuple = field(default_factory=tuple)


def test_context():
    design_filename = os.path.join(
        ToolboxData.TEST_PROJECTS_PATH, 'lib_test', 'design_blocks', 'design_blocks.kicad_pro'
    )

    context = ProcessContext(timestamp=datetime.now().strftime("%Y%m%d"))
    context.sch_filename = design_filename.replace('.kicad_pro', '.kicad_sch')
    context.pcb_filename = design_filename.replace('.kicad_pro', '.kicad_pcb')
    context.project_folder = os.path.dirname(design_filename)
    context.pca_folder = os.path.join(context.project_folder, 'PCA_TEST')
    context.output_folder = os.path.join(context.pca_folder, 'output')
    context.design_name = os.path.basename(design_filename).replace('.kicad_pro', '')
    context.outputs = ('Schematics to PDF', 'Bill of materials (BOM)', 'Gerbers and drill data',
                       'Position data', 'PCB placement to PDF', 'ODB+', 'PCB 3D model (step)')
    context.bom_options = ('General', 'LilyTronics ERP', 'JLCPCB')

    if not os.path.exists(context.pca_folder):
        os.makedirs(context.pca_folder)
    else:
        # Clear PCA folder
        for item in Path(context.pca_folder).iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    if not os.path.exists(context.output_folder):
        os.makedirs(context.output_folder)

    return context
