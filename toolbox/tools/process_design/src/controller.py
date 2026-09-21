"""
Controller for process design tool.
"""

import os
import traceback
import wx

from datetime import datetime
from toolbox.tools.common.controller_base import ControllerBase
from toolbox.tools.process_design.src.process_context import ProcessContext
from toolbox.tools.process_design.src.process_design import process_design


class Controller(ControllerBase):

    _OUTPUTS = [
        'Schematics to PDF',
        'Bill of materials (BOM)',
        'Gerbers and drill data',
        'Position data',
        'PCB placement to PDF',
        'ODB+',
        'PCB 3D model (step)'
    ]

    _BOM_OPTIONS = [
        'General',
        'LilyTronics ERP',
        'JLCPCB'
    ]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tool_view.Bind(wx.EVT_BUTTON, self._on_process_click, self.tool_view.ID_BTN_PROCESS)

        self.tool_view.init_outputs(self._OUTPUTS)
        self.tool_view.init_bom_options(self._BOM_OPTIONS)

    ###########
    # Private #
    ###########

    def _write_report(self, messages, context: ProcessContext):
        report_filename = os.path.join(context.pca_folder, f"{context.timestamp}_process_report.txt")
        with open(report_filename, 'w', encoding='utf-8') as fp:
            fp.write('\n'.join(messages) + '\n')
        self.logger.add_to_console(f'Result are written to: {report_filename}')

    #################
    # Event handler #
    #################

    def _on_process_click(self, event):
        report = []
        context = ProcessContext(timestamp=datetime.now().strftime("%Y%m%d"))
        try:
            design_filename = self.tool_view.get_design_file()
            context.sch_filename = design_filename.replace('.kicad_pro', '.kicad_sch')
            context.pcb_filename = design_filename.replace('.kicad_pro', '.kicad_pcb')
            if not os.path.isfile(design_filename):
                raise Exception(f"The file '{design_filename}' does not exist")
            if not os.path.isfile(context.sch_filename):
                raise Exception(f"The file '{context.sch_filename}' does not exist")
            if not os.path.isfile(context.pcb_filename):
                raise Exception(f"The file '{context.pcb_filename}' does not exist")

            context.project_folder = os.path.dirname(design_filename)
            context.pca_folder = os.path.join(context.project_folder, f'PCA_{context.timestamp}')
            if not os.path.exists(context.pca_folder):
                os.makedirs(context.pca_folder)

            context.design_name = os.path.basename(design_filename).replace('.kicad_pro', '')

            self.logger.add_to_console(f'Process design   : {context.design_name}')
            self.logger.add_to_console(f'SCH root file    : {context.sch_filename}')
            self.logger.add_to_console(f'PCB file         : {context.pcb_filename}')
            self.logger.add_to_console(f'PCA output folder: {context.pca_folder}')
            report.append(f'Process design   : {context.design_name}')
            report.append(f'SCH root file    : {context.sch_filename}')
            report.append(f'PCB file         : {context.pcb_filename}')
            report.append(f'PCA output folder: {context.pca_folder}')

            context.outputs = self.tool_view.get_outputs()
            context.bom_options = self.tool_view.get_bom_options()

            process_design(context, report, self.logger.add_to_console)

        except Exception as e:
            message = f'Error: {type(e).__name__}: {e}'
            with wx.MessageDialog(
                    self.tool_view, message, 'Process design',
                    style=wx.OK | wx.ICON_EXCLAMATION
                ) as dlg:
                dlg.ShowModal()
            if len(report) > 0:
                report.append(f'\n{message}')
                report.append(traceback.format_exc().strip())

        event.Skip()

        if len(report) > 0:
            self._write_report(report, context)


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.process_design.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
