"""
Process design for manufacturing.
"""

import os
import shutil
import wx

from datetime import datetime

from toolbox.controllers.controller_base import ControllerBase
from toolbox.models.id_manager import IdManager
from toolbox.models.kicad_cli import KiCadCli
from toolbox.views.view_process_design import ViewProcessDesign


class ControllerProcessDesign(ControllerBase):

    name = "Process design"

    _OUTPUTS = [
        "Schematics to PDF",
        "Bill of materials (BOM)",
        "Gerbers and drill data",
        "Position data",
        "PCB placement to PDF",
        "ODB+",
        "PCB 3D model (step)"
    ]

    _BOM_OPTIONS = [
        "General",
        "LilyTronics ERP",
        "JLCPCB"
    ]

    def __init__(self, main_view, notebook):
        super().__init__(main_view, ViewProcessDesign(notebook))
        self._view.init_outputs(self._OUTPUTS)
        self._view.init_bom_options(self._BOM_OPTIONS)
        self.bind(wx.EVT_BUTTON, self._on_process_click, IdManager.ID_BTN_PROCESS)

    ###########
    # Private #
    ###########

    def _process_design(self):
        error = ""
        design_filename = self._view.get_design_file()
        sch_filename = design_filename.replace(".kicad_pro", ".kicad_sch")
        pcb_filename = design_filename.replace(".kicad_pro", ".kicad_pcb")
        if not os.path.isfile(design_filename):
            error = f"The file '{design_filename}' does not exist"
        if error == "" and not os.path.isfile(sch_filename):
            error = f"The file '{sch_filename}' does not exist"
        if error == "" and not os.path.isfile(pcb_filename):
            error = f"The file '{pcb_filename}' does not exist"

        design_name = os.path.basename(design_filename).replace(".kicad_pro", "")
        self._main_view.add_to_console("Processing files:")
        self._main_view.add_to_console(sch_filename)
        self._main_view.add_to_console(pcb_filename)
        self._main_view.add_to_console(f"Using design name: {design_name}")

        output_folder = os.path.join(os.path.dirname(design_filename), "output")
        self._main_view.add_to_console(f"Create output folder: {output_folder}")
        try:
            if os.path.exists(output_folder):
                shutil.rmtree(output_folder)
            os.makedirs(output_folder)
        except Exception as e:
            error = str(e)

        cli = None
        report = ""
        timestamp = datetime.now().strftime("%Y%m%d")
        if error == "":
            try:
                cli = KiCadCli()
                version = "KiCad version: %s" % cli.get_version()
                self._main_view.add_to_console(version)
                report += f"{version}\n"
            except Exception as e:
                error = str(e)

        if error == "":
            for output in self._view.get_outputs():
                message = f"Generate {output}"
                self._main_view.add_to_console(f"Generate {output}")
                report += f"\n{message}\n"
                try:
                    if output == "Schematics to PDF":
                        output_filename = f"{timestamp}_{design_name}_schematics.pdf"
                        output_filename = os.path.join(output_folder, output_filename)
                        message = cli.generate_schematics_pdf(sch_filename, output_filename)

                    elif output == "Bill of materials (BOM)":
                        options = self._view.get_bom_options()
                        for option in options:
                            report += f"Generate BOM: {option}\n"
                            if option == "General":
                                output_filename = f"{timestamp}_{design_name}_bom_general.tsv"
                                output_filename = os.path.join(output_folder, output_filename)
                                message = cli.generate_bill_of_materials(sch_filename, output_filename)
                                report += f"{message}\n"
                            elif option == "LilyTronics ERP":
                                output_filename = f"{timestamp}_{design_name}_bom_lily_erp.csv"
                                output_filename = os.path.join(output_folder, output_filename)
                                message = cli.generate_bill_of_materials(sch_filename, output_filename, "lily_erp")
                                report += f"{message}\n"
                            elif option == "JLCPCB":
                                output_filename = f"{timestamp}_{design_name}_bom_jlcpcb.csv"
                                output_filename = os.path.join(output_folder, output_filename)
                                message = cli.generate_bill_of_materials(sch_filename, output_filename, "jlcpcb")
                                report += f"{message}\n"
                            else:
                                raise Exception(f"BOM option '{option}' is not defined")
                        message = ""

                    elif output == "Gerbers and drill data":
                        gerber_output_folder = os.path.join(output_folder, f"{timestamp}_gerbers")
                        zip_filename = os.path.join(output_folder, f"{timestamp}_{design_name}_gerbers.zip")
                        n_layers = self._view.get_layers()
                        message = f"Number of copper layers: {n_layers}\n"
                        message += cli.generate_gerbers(pcb_filename, gerber_output_folder, zip_filename, n_layers)

                    elif output == "Position data":
                        output_filename = f"{timestamp}_{design_name}_position.csv"
                        output_filename = os.path.join(output_folder, output_filename)
                        message = cli.generate_position_file(pcb_filename, output_filename)

                    elif output == "PCB placement to PDF":
                        has_comp_bot = self._view.get_option_comp_bot()
                        output_filename = f"{timestamp}_{design_name}_pcb_placement.pdf"
                        output_filename = os.path.join(output_folder, output_filename)
                        message = cli.generate_pcb_pdf(pcb_filename, output_filename, has_comp_bot)

                    elif output == "ODB+":
                        output_filename = f"{timestamp}_{design_name}_odb.zip"
                        output_filename = os.path.join(output_folder, output_filename)
                        message = cli.generate_odb(pcb_filename, output_filename)

                    elif output == "PCB 3D model (step)":
                        output_filename = f"{timestamp}_{design_name}_pcb.step"
                        output_filename = os.path.join(output_folder, output_filename)
                        message = cli.generate_step(pcb_filename, output_filename)

                    else:
                        raise Exception(f"Output '{output}' is not defined")

                except Exception as e:
                    message = e
                report += f"{message}\n"

            report_filename = os.path.join(output_folder, f"{timestamp}_process_report.txt")
            with open(report_filename, "w") as fp:
                fp.write(report)
            self._main_view.add_to_console(f"Result are written to: {report_filename}")

        if error != "":
            dlg = wx.MessageDialog(self._view, error, "Generate product ID", style=wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()

    ##################
    # Event handlers #
    ##################

    def _on_process_click(self, _event):
        self._main_view.clear_console()
        wx.CallAfter(self._process_design)


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(2)
