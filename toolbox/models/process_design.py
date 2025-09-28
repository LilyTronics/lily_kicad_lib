"""
Model for processing a design using the KiCad cli
"""

import csv
import os
import re

from toolbox.models.kicad_cli import KiCadCli


class ProcessDesign:

    def __init__(self, timestamp, design_name, output_folder):
        self._timestamp = timestamp
        self._design_name = design_name
        self._output_folder = output_folder
        self._cli = KiCadCli()

    ###########
    # Private #
    ###########

    @staticmethod
    def _read_csv(filename):
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    @staticmethod
    def _write_csv(filename, field_names, data):
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, field_names, quotechar="\"", quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(data)

    ##########
    # Public #
    ##########

    def get_kicad_version(self):
        return self._cli.get_version()

    def schematics_to_pdf(self, sch_filename):
        output_filename = f"{self._timestamp}_{self._design_name}_schematics.pdf"
        output_filename = os.path.join(self._output_folder, output_filename)
        return self._cli.generate_schematics_pdf(sch_filename, output_filename)

    def create_bom(self, sch_filename, options, pca_id):
        report = ""
        for option in options:
            report += f"Generate BOM: {option}\n"
            if option == "General":
                output_filename = f"{self._timestamp}_{self._design_name}_bom_general.tsv"
                output_filename = os.path.join(self._output_folder, output_filename)
                message = self._cli.generate_bill_of_materials(sch_filename, output_filename)
                report += f"{message}\n"

            elif option == "LilyTronics ERP":
                output_filename = f"{self._timestamp}_{self._design_name}_bom_lily_erp.csv"
                output_filename = os.path.join(self._output_folder, output_filename)
                message = self._cli.generate_bill_of_materials(sch_filename, output_filename, "lily_erp")
                if pca_id == "":
                    message += "\nWARNING: PCA ID is empty"
                convert_message = ""
                if os.path.isfile(output_filename):
                    data_in = self._read_csv(output_filename)
                    data_in = sorted(data_in, key=lambda x: x["Lily_ID"])
                    data_out = []
                    quantity = 1
                    bom_type = "Kit"
                    for record in data_in:
                        data_out.append({
                            "External ID": pca_id,
                            "Product": pca_id,
                            "Quantity": quantity,
                            "BoM Type": bom_type,
                            "BoM Lines/Component": record["Lily_ID"],
                            "BoM Lines/Quantity": int(record["QUANTITY"])
                        })
                        if pca_id is not None:
                            pca_id = None
                            quantity = None
                            bom_type = None
                        if record["Lily_ID"] == "NO_ID":
                            convert_message = "WARNING: Component with 'NO_ID' in BOM"
                    field_names = ["External ID", "Product", "Quantity", "BoM Type",
                                   "BoM Lines/Component", "BoM Lines/Quantity"]
                    self._write_csv(output_filename, field_names, data_out)

                report += f"{message}\n"
                if convert_message != "":
                    report += f"{convert_message}\n"

            elif option == "JLCPCB":
                output_filename = f"{self._timestamp}_{self._design_name}_bom_jlcpcb.csv"
                output_filename = os.path.join(self._output_folder, output_filename)
                message = self._cli.generate_bill_of_materials(sch_filename, output_filename, "jlcpcb")
                # JLCPCB cannot handle ranges of designators like R1-R3 must be R1, R2, R3
                # We need to convert that
                if os.path.isfile(output_filename):
                    data_in = self._read_csv(output_filename)
                    for record in data_in:
                        if "-" in record["Reference"]:
                            new_range = []
                            parts = record["Reference"].split(",")
                            for i in range(len(parts)):
                                if "-" in parts[i]:
                                    start, end = parts[i].split("-")
                                    match = re.match(r"([A-Za-z]+)(\d+)", start)
                                    i = int(match.group(2))
                                    ref = f"{match.group(1)}{i}"
                                    while ref != end:
                                        new_range.append(ref)
                                        i += 1
                                        ref = f"{match.group(1)}{i}"
                                    new_range.append(end)
                                else:
                                    new_range.append(parts[i])
                            record["Reference"] = ",".join(new_range)
                    self._write_csv(output_filename, data_in[0].keys(), data_in)
                report += f"{message}\n"

            else:
                raise Exception(f"BOM option '{option}' is not defined")
        return report

    def create_gerbers_and_drill(self, pcb_filename, n_layers):
        gerber_output_folder = os.path.join(self._output_folder, f"{self._timestamp}_gerbers")
        zip_filename = os.path.join(self._output_folder, f"{self._timestamp}_{self._design_name}_gerbers.zip")
        message = f"Number of copper layers: {n_layers}\n"
        message += self._cli.generate_gerbers(pcb_filename, gerber_output_folder, zip_filename, n_layers)
        return message

    def create_position_file(self, pcb_filename):
        output_filename = f"{self._timestamp}_{self._design_name}_position.csv"
        output_filename = os.path.join(self._output_folder, output_filename)
        message = self._cli.generate_position_file(pcb_filename, output_filename)
        if os.path.isfile(output_filename):
            warnings = ""
            data_in = self._read_csv(output_filename)
            data_out = []
            for record in data_in:
                data_out.append({
                    "Designator": record["Ref"],
                    "Mid X": record["PosX"],
                    "Mid Y": record["PosY"],
                    "Layer": record["Side"],
                    "Rotation": record["Rot"]
                })
                not_on_raster = False
                i = record["PosX"].find(".")
                if i > -1:
                    not_on_raster = int(record["PosX"][i + 2:]) > 0
                i = record["PosY"].find(".")
                if i > -1:
                    not_on_raster = not_on_raster or int(record["PosY"][i + 2:]) > 0
                if not_on_raster:
                    warnings += (f"\nWARNING: Component {record["Ref"]} is not on a 0.1mm raster "
                                 f"({record["PosX"]}, {record["PosY"]})")

            if warnings != "":
                message += warnings

            self._write_csv(output_filename, ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"], data_out)
        return message

    def pcb_to_pdf(self, pcb_filename, has_comp_bot):
        output_filename = f"{self._timestamp}_{self._design_name}_pcb_placement.pdf"
        output_filename = os.path.join(self._output_folder, output_filename)
        return self._cli.generate_pcb_pdf(pcb_filename, output_filename, has_comp_bot)

    def create_odb(self, pcb_filename):
        output_filename = f"{self._timestamp}_{self._design_name}_odb.zip"
        output_filename = os.path.join(self._output_folder, output_filename)
        return self._cli.generate_odb(pcb_filename, output_filename)

    def create_3d_model(self, pcb_filename):
        output_filename = f"{self._timestamp}_{self._design_name}_pcb.step"
        output_filename = os.path.join(self._output_folder, output_filename)
        return self._cli.generate_step(pcb_filename, output_filename)


if __name__ == "__main__":

    import shutil

    from datetime import datetime

    _bom_options = ("General", "LilyTronics ERP", "JLCPCB")
    _timestamp = datetime.now().strftime("%Y%m%d")
    _design_filename = os.path.abspath("../../projects/arduino_base/arduino_base.kicad_pro")
    _sch_filename = _design_filename.replace(".kicad_pro", ".kicad_sch")
    _pcb_filename = _design_filename.replace(".kicad_pro", ".kicad_pcb")

    _design_name = os.path.basename(_design_filename).replace(".kicad_pro", "")
    _output_folder = os.path.join(os.path.dirname(_design_filename), "output")
    if os.path.exists(_output_folder):
        shutil.rmtree(_output_folder)
    os.makedirs(_output_folder)

    p = ProcessDesign(_timestamp, _design_name, _output_folder)

    print("Version:", p.get_kicad_version())
    print(p.schematics_to_pdf(_sch_filename))
    print(p.create_bom(_sch_filename, _bom_options, "1234-12345"))
    print(p.create_gerbers_and_drill(_pcb_filename, 2))
    print(p.create_position_file(_pcb_filename))
    print(p.pcb_to_pdf(_pcb_filename, False))
    print(p.create_odb(_pcb_filename))
    print(p.create_3d_model(_pcb_filename))
