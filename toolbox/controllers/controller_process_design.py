"""
Process design for manufacturing.
"""

import glob
import os
import shutil
import wx

from datetime import datetime

from toolbox.controllers.controller_base import ControllerBase
from toolbox.models.id_manager import IdManager
from toolbox.models.process_design import ProcessDesign
from toolbox.models.projects_checker import ProjectsChecker
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

        project_folder = os.path.dirname(design_filename)
        timestamp = datetime.now().strftime("%Y%m%d")
        pca_folder = os.path.join(project_folder, f"PCA_{timestamp}")
        output_folder = os.path.join(pca_folder, "output")

        process = None
        report = ""

        self._main_view.add_to_console("Check design to library:")
        ProjectsChecker.stdout = self._main_view.add_to_console
        messages = ProjectsChecker.check_project(project_folder)
        if len(messages) > 0:
            for message in messages:
                self._main_view.add_to_console(f"{message["item"]}: {message["message"]}")
            error = "The project checker reported errors"

        if error == "":
            self._main_view.add_to_console(f"Create output folder: {pca_folder}")
            try:
                if os.path.exists(pca_folder):
                    shutil.rmtree(pca_folder)
                os.makedirs(output_folder)
            except Exception as e:
                error = str(e)

        if error == "":
            try:
                process = ProcessDesign(timestamp, design_name, output_folder)
                version = "KiCad version: %s" % process.get_kicad_version()
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
                        message = process.schematics_to_pdf(sch_filename)

                    elif output == "Bill of materials (BOM)":
                        options = self._view.get_bom_options()
                        pca_id = self._view.get_pca_id()
                        message = process.create_bom(sch_filename, options, pca_id)

                    elif output == "Gerbers and drill data":
                        n_layers = self._view.get_layers()
                        message = process.create_gerbers_and_drill(pcb_filename, n_layers)

                    elif output == "Position data":
                        message = process.create_position_file(pcb_filename)

                    elif output == "PCB placement to PDF":
                        has_comp_bot = self._view.get_option_comp_bot()
                        message = process.pcb_to_pdf(pcb_filename, has_comp_bot)

                    elif output == "ODB+":
                        message = process.create_odb(pcb_filename)

                    elif output == "PCB 3D model (step)":
                        message = process.create_3d_model(pcb_filename)

                    else:
                        raise Exception(f"Output '{output}' is not defined")

                except Exception as e:
                    message = f"WARNING: {e}"
                report += f"{message}\n"

            # Copy design
            try:
                self._main_view.add_to_console("Copy design files")
                report += "\nCopy design files\n"
                # Copy project file
                target = os.path.join(pca_folder, os.path.basename(design_filename))
                report += f"Copy: {design_filename}\n"
                report += f"To  : {target}\n"
                shutil.copy2(design_filename, target)
                # Copy schematics
                for item in glob.glob(os.path.join(project_folder, "*.kicad_sch")):
                    target = os.path.join(pca_folder, os.path.basename(item))
                    report += f"Copy: {item}\n"
                    report += f"To  : {target}\n"
                    shutil.copy2(item, target)
                # Copy layout
                for item in glob.glob(os.path.join(project_folder, "*.kicad_pcb")):
                    target = os.path.join(pca_folder, os.path.basename(item))
                    report += f"Copy: {item}\n"
                    report += f"To  : {target}\n"
                    shutil.copy2(item, target)
                # Special files if they exist
                # Design rules
                item = design_filename.replace(".kicad_pro", ".kicad_dru")
                if os.path.isfile(item):
                    target = os.path.join(pca_folder, os.path.basename(item))
                    report += f"Copy: {item}\n"
                    report += f"To  : {target}\n"
                    shutil.copy2(item, target)
                # Custom symbol library table
                item = os.path.join(project_folder, "sym-lib-table")
                if os.path.isfile(item):
                    target = os.path.join(pca_folder, os.path.basename(item))
                    report += f"Copy: {item}\n"
                    report += f"To  : {target}\n"
                    shutil.copy2(item, target)
                # Custom footprint library table
                item = os.path.join(project_folder, "fp-lib-table")
                if os.path.isfile(item):
                    target = os.path.join(pca_folder, os.path.basename(item))
                    report += f"Copy: {item}\n"
                    report += f"To  : {target}\n"
                    shutil.copy2(item, target)
            except Exception as e:
                self._main_view.add_to_console(f"Error: {e}")

            report_filename = os.path.join(pca_folder, f"{timestamp}_process_report.txt")
            with open(report_filename, "w") as fp:
                fp.write(report)
            self._main_view.add_to_console(f"Result are written to: {report_filename}")

        if error == "" and "WARNING" in report:
            error = "The report contains warnings."

        if error != "":
            dlg = wx.MessageDialog(self._view, error, "Process design", style=wx.OK | wx.ICON_EXCLAMATION)
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
