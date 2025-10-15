"""
Process design for manufacturing.
"""

import glob
import os
import traceback
import shutil
import wx

from datetime import datetime

from toolbox.controllers.controller_base import ControllerBase
from toolbox.models.design_parser import DesignParser
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
        timestamp = datetime.now().strftime("%Y%m%d")
        report = []
        pca_folder = ""
        dialog_message = ""
        try:
            design_filename = self._view.get_design_file()
            sch_filename = design_filename.replace(".kicad_pro", ".kicad_sch")
            pcb_filename = design_filename.replace(".kicad_pro", ".kicad_pcb")
            if not os.path.isfile(design_filename):
                raise Exception(f"The file '{design_filename}' does not exist")
            if not os.path.isfile(sch_filename):
                raise Exception(f"The file '{sch_filename}' does not exist")
            if not os.path.isfile(pcb_filename):
                raise Exception(f"The file '{pcb_filename}' does not exist")

            project_folder = os.path.dirname(design_filename)
            pca_folder = os.path.join(project_folder, f"PCA_{timestamp}")
            output_folder = os.path.join(pca_folder, "output")

            self._main_view.add_to_console(f"Create output folder: {pca_folder}")
            if os.path.exists(pca_folder):
                shutil.rmtree(pca_folder)
            os.makedirs(output_folder)

            report.append("{timestamp} Process design: {design_filename}")
            report.append(f"Output folder: {pca_folder}")

            design_name = os.path.basename(design_filename).replace(".kicad_pro", "")
            self._main_view.add_to_console("Processing files:")
            self._main_view.add_to_console(sch_filename)
            self._main_view.add_to_console(pcb_filename)
            self._main_view.add_to_console(f"Design name: {design_name}")

            report.append(f"SCH: {sch_filename}")
            report.append(f"PCB: {sch_filename}")
            report.append(f"Design name: {design_name}")

            process = ProcessDesign(timestamp, design_name, output_folder)
            version = "KiCad version: %s" % process.get_kicad_version()
            self._main_view.add_to_console(version)
            report.append(f"{version}")

            properties = self._check_design(project_folder, report)
            self._generate_outputs(process, sch_filename, pcb_filename, properties, report)
            self._copy_design(pca_folder, design_filename, project_folder, report)

            report.append("\nProcess finished")
        except Exception as e:
            dialog_message = f"{str(e)}\n"
            if len(report) == 0:
                dialog_message += traceback.format_exc().strip()
            else:
                report.append(f"\n{dialog_message}")
                report.append(traceback.format_exc().strip())

        if dialog_message != "":
            dlg = wx.MessageDialog(self._view, dialog_message, "Process design", style=wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()

        if len(report) > 0:
            report_filename = os.path.join(pca_folder, f"{timestamp}_process_report.txt")
            with open(report_filename, "w") as fp:
                fp.write("\n".join(report) + "\n")
            self._main_view.add_to_console(f"Result are written to: {report_filename}")

    def _check_design(self, project_folder, report):
        self._main_view.add_to_console("Check design to library")
        report.append("\nCheck design to library")
        ProjectsChecker.stdout = self._main_view.add_to_console
        messages = ProjectsChecker.check_project(project_folder)
        if len(messages) > 0:
            for message in messages:
                report.append(f"ERROR: {message["item"]}: {message["message"]}")
            self._main_view.add_to_console("The project checker reported errors")
            raise Exception("The project checker reported errors")

        self._main_view.add_to_console("Check design properties")
        sch_props = DesignParser.get_schematics_properties(project_folder)
        report.append("\nSchematics properties:")
        for key in sch_props:
            report.append(f"{key}: {sch_props[key]}")
        pcb_props = DesignParser.get_pcb_properties(project_folder)
        report.append("\nPCB properties:")
        for key in pcb_props:
            report.append(f"{key}: {pcb_props[key]}")

        # Test properties
        for prop in ["design_name", "date", "revision", "pca_id", "pcb_id"]:
            if sch_props[prop] != pcb_props[prop]:
                raise Exception(f"The {prop.replace("_", " ")} is not equal between the schematics and the PCB")

        return pcb_props

    def _generate_outputs(self, process, sch_filename, pcb_filename, properties, report):
        for output in self._view.get_outputs():
            self._main_view.add_to_console(f"Generate {output}")
            report.append(f"\nGenerate {output}")

            if output == "Schematics to PDF":
                report.append(process.schematics_to_pdf(sch_filename))

            elif output == "Bill of materials (BOM)":
                options = self._view.get_bom_options()
                report.append(process.create_bom(sch_filename, options, properties["pca_id"]))

            elif output == "Gerbers and drill data":
                report.append(process.create_gerbers_and_drill(pcb_filename, properties["n_layers"]))

            elif output == "Position data":
                report.append(process.create_position_file(pcb_filename))

            elif output == "PCB placement to PDF":
                report.append(process.pcb_to_pdf(pcb_filename, properties["has_comp_bot"]))

            elif output == "ODB+":
                report.append(process.create_odb(pcb_filename))

            elif output == "PCB 3D model (step)":
                report.append(process.create_3d_model(pcb_filename))

            else:
                raise Exception(f"Output '{output}' is not defined")

    def _copy_design(self, pca_folder, design_filename, project_folder, report):
        self._main_view.add_to_console("Copy design files")
        report.append("\nCopy design files")
        # Copy project file
        target = str(os.path.join(pca_folder, os.path.basename(design_filename)))
        report.append(f"Copy: {design_filename}")
        report.append(f"To  : {target}")
        shutil.copy2(design_filename, target)
        # Copy schematics
        for item in glob.glob(os.path.join(project_folder, "*.kicad_sch")):
            target = str(os.path.join(pca_folder, os.path.basename(item)))
            report.append(f"Copy: {item}")
            report.append(f"To  : {target}")
            shutil.copy2(item, target)
        # Copy layout
        for item in glob.glob(os.path.join(project_folder, "*.kicad_pcb")):
            target = str(os.path.join(pca_folder, os.path.basename(item)))
            report.append(f"Copy: {item}")
            report.append(f"To  : {target}")
            shutil.copy2(item, target)
        # Special files if they exist
        # Design rules
        item = design_filename.replace(".kicad_pro", ".kicad_dru")
        if os.path.isfile(item):
            target = str(os.path.join(pca_folder, os.path.basename(item)))
            report.append(f"Copy: {item}")
            report.append(f"To  : {target}")
            shutil.copy2(item, target)
        # Custom symbol library table
        item = os.path.join(project_folder, "sym-lib-table")
        if os.path.isfile(item):
            target = str(os.path.join(pca_folder, os.path.basename(item)))
            report.append(f"Copy: {item}")
            report.append(f"To  : {target}")
            shutil.copy2(item, target)
        # Custom footprint library table
        item = os.path.join(project_folder, "fp-lib-table")
        if os.path.isfile(item):
            target = str(os.path.join(pca_folder, os.path.basename(item)))
            report.append(f"Copy: {item}")
            report.append(f"To  : {target}")
            shutil.copy2(item, target)

    ##################
    # Event handlers #
    ##################

    def _on_process_click(self, _event):
        self._main_view.clear_console()
        wx.CallAfter(self._process_design)


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(2)
