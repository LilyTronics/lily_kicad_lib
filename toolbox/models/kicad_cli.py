"""
Module for using the KiCad command line interface (CLI)
"""

import os
import subprocess
import zipfile


class KiCadCli:

    _PATH = "C:\\Program Files\\KiCad"
    _EXE_NAME = "kicad-cli.exe"

    def __init__(self):
        self._cli_exe = self._find_cli_exe()

    ###########
    # Private #
    ###########

    def _find_cli_exe(self):
        for current_folder, sub_folders, filenames in os.walk(self._PATH):
            sub_folders.sort()
            if self._EXE_NAME in filenames:
                return os.path.join(current_folder, self._EXE_NAME)
        raise Exception(f"Executable '{self._EXE_NAME}' not found")

    def _run_command(self, params):
        cmd = [self._cli_exe]
        cmd.extend(params)
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return f"{result.stdout.strip()}\n{result.stderr.strip()}".strip()

    ##########
    # Public #
    ##########

    def get_version(self):
        return self._run_command(["version"])

    def generate_schematics_pdf(self, input_file, output_file):
        cmd = ["sch", "export", "pdf"]
        cmd.extend(["--output", output_file])
        cmd.append(input_file)
        return self._run_command(cmd)

    def generate_bill_of_materials(self, input_file, output_file, option=""):
        cmd = ["sch", "export", "bom"]
        cmd.extend(["--output", output_file])
        if option == "lily_erp":
            cmd.extend(["--fields", "Lily_ID,${QUANTITY}"])
            cmd.extend(["--group-by", "Lily_ID"])
        elif option == "jlcpcb":
            cmd.extend(["--fields", "Reference,Value,Footprint,${QUANTITY},JLCPCB_ID"])
            cmd.extend(["--group-by", "JLCPCB_ID"])
        else:
            # Default
            cmd.extend(["--fields", "Reference,Value,Footprint,${QUANTITY},Manufacturer,Manufacturer_ID,Lily_ID"])
            cmd.extend(["--group-by", "Manufacturer_ID"])
            cmd.extend(["--field-delimiter", "\t"])
        cmd.append(input_file)
        return self._run_command(cmd)

    def generate_gerbers(self, input_file, output_folder, zip_filename, n_layers=2):
        # Generate gerbers
        cmd = ["pcb", "export", "gerbers"]
        cmd.extend(["--output", output_folder])
        layers = "Edge.Cuts,F.Cu,B.Cu"
        for i in range(1, n_layers - 1):
            layers += f",In{i}.Cu"
        layers += ",F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste"
        cmd.extend(["--layers", layers])
        cmd.append("--use-drill-file-origin")
        cmd.append("--no-protel-ext")
        cmd.append(input_file)
        result = self._run_command(cmd)
        # Add drill
        cmd = ["pcb", "export", "drill"]
        cmd.extend(["--output", output_folder])
        cmd.extend(["--drill-origin", "plot"])
        cmd.append("--excellon-separate-th")
        cmd.append(input_file)
        result += "\n" + self._run_command(cmd)
        # Generate ZIP file
        with zipfile.ZipFile(zip_filename, "w", compression=zipfile.ZIP_DEFLATED) as fp:
            for item in os.listdir(output_folder):
                fp.write(os.path.join(output_folder, item), item)
        result += f"\nCreated zip file: {zip_filename}"
        return result

    def generate_position_file(self, input_file, output_file):
        cmd = ["pcb", "export", "pos"]
        cmd.extend(["--output", output_file])
        cmd.extend(["--side", "both"])
        cmd.extend(["--format", "csv"])
        cmd.extend(["--units", "mm"])
        cmd.append("--use-drill-file-origin")
        cmd.append("--exclude-dnp")
        cmd.append(input_file)
        return self._run_command(cmd)

    def generate_pcb_pdf(self, input_file, output_file, bottom=False):
        common = ["--include-border-title", "--crossout-DNP-footprints-on-fab-layers",
                  "--drill-shape-opt", "0", "--mode-single"]
        # Generate top placement
        output_file = output_file.replace(".pdf", "_top.pdf")
        cmd = ["pcb", "export", "pdf"]
        cmd.extend(["--output", output_file])
        cmd.extend(["--layers", "Edge.Cuts,F.Fab,F.Silkscreen"])
        cmd.extend(common)
        cmd.append(input_file)
        result = self._run_command(cmd)
        if bottom:
            # Generate bottom
            output_file = output_file.replace("_top.pdf", "_bot.pdf")
            cmd = ["pcb", "export", "pdf"]
            cmd.extend(["--output", output_file])
            cmd.extend(["--layers", "Edge.Cuts,B.Fab,B.Silkscreen"])
            cmd.extend(common)
            cmd.append("--mirror")
            cmd.append(input_file)
            result += "\n" + self._run_command(cmd)
        return result

    def generate_odb(self, input_file, output_file):
        cmd = ["pcb", "export", "odb"]
        cmd.extend(["--output", output_file])
        cmd.extend(["--compression", "zip"])
        cmd.append(input_file)
        return self._run_command(cmd)

    def generate_step(self, input_file, output_file):
        cmd = ["pcb", "export", "step"]
        cmd.extend(["--output", output_file])
        cmd.append("--no-unspecified")
        cmd.append("--no-dnp")
        cmd.append("--drill-origin")
        cmd.append("--include-pads")
        cmd.append("--include-tracks")
        cmd.append("--include-zones")
        cmd.append("--cut-vias-in-body")
        cmd.append("--include-soldermask")
        cmd.append("--include-silkscreen")
        cmd.append(input_file)
        return self._run_command(cmd)


if __name__ == "__main__":

    import shutil

    project_path = os.path.abspath("../../projects/arduino_base/arduino_base.kicad_pro")
    sch_path = project_path.replace(".kicad_pro", ".kicad_sch")
    pcb_path = project_path.replace(".kicad_pro", ".kicad_pcb")
    output_path = os.path.join(os.path.dirname(project_path), "output")

    print("Project:", project_path)
    print("Schematics:", sch_path)
    print("Layout:", pcb_path)
    print("Output path:", output_path)
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)

    cli = KiCadCli()

    print("\nVersion:", cli.get_version())

    print("\nSchematics to PDF")
    print(cli.generate_schematics_pdf(sch_path, os.path.join(output_path, "schematics.pdf")))
    print("\nSchematics to BOM generic")
    print(cli.generate_bill_of_materials(sch_path, os.path.join(output_path, "bom_generic.csv")))
    print("Schematics to BOM for ERP")
    print(cli.generate_bill_of_materials(sch_path, os.path.join(output_path, "bom_erp.csv"), "lily_erp"))
    print("Schematics to BOM for JLC")
    print(cli.generate_bill_of_materials(sch_path, os.path.join(output_path, "bom_jlc.csv"), "jlc"))

    print("\nPCB to Gerbers")
    zip_fname = os.path.join(output_path, os.path.basename(pcb_path).replace(".kicad_pcb", "_gerbers.zip"))
    print(cli.generate_gerbers(pcb_path, os.path.join(output_path, "gerbers"), zip_fname))
    print("\nPCB to position file")
    print(cli.generate_position_file(pcb_path, os.path.join(output_path, "position.csv")))
    print("\nPCB to PDF")
    print(cli.generate_pcb_pdf(pcb_path, os.path.join(output_path, "pcb_placement.pdf"), True))
    print("\nPCB to ODB+")
    print(cli.generate_odb(pcb_path, os.path.join(output_path, "odb.zip")))
    print("\nPCB to step")
    print(cli.generate_step(pcb_path, os.path.join(output_path, "pcb.step")))
