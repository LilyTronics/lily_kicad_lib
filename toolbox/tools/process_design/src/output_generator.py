"""
Generate the requested outputs using the KiCad CLI.
"""

import csv
import os
import re

from toolbox.common.parsers.design_parser import DesignParser
from toolbox.tools.process_design.src.kicad_cli import KiCadCli
from toolbox.tools.process_design.src.process_context import ProcessContext


class OutputGenerator:

    _KICAD_CLI = None
    _logger = print


    ###########
    # Private #
    ###########

    @classmethod
    def _log(cls, message):
        cls._logger(message)
        return message

    @classmethod
    def _set_kicad_cli(cls):
        cls._KICAD_CLI = KiCadCli()

    @staticmethod
    def _read_csv(filename):
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            return list(csv.DictReader(file))

    @staticmethod
    def _write_csv(filename, field_names, data):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, field_names, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(data)

    @classmethod
    def _schematics_to_pdf(cls, context: ProcessContext):
        output_filename = f'{context.timestamp}_{context.design_name}_schematics.pdf'
        output_filename = os.path.join(context.output_folder, output_filename)
        return cls._KICAD_CLI.generate_schematics_pdf(context.sch_filename, output_filename)

    @classmethod
    def _create_bom(cls, context: ProcessContext):
        report = ''
        for option in context.bom_options:
            if option == 'General':
                report += f'Generate BOM: {option}\n'
                output_filename = f'{context.timestamp}_{context.design_name}_bom_general.tsv'
                output_filename = os.path.join(context.output_folder, output_filename)
                message = cls._KICAD_CLI.generate_bill_of_materials(
                    context.sch_filename, output_filename
                )
                report += f'{message}\n'

            elif option == 'LilyTronics ERP':
                props = DesignParser.get_schematics_properties(context.project_folder)
                pca_id = props.get('pca_id', '')
                report += f'Generate BOM: {option}\n'
                output_filename = f'{context.timestamp}_{context.design_name}_bom_lily_erp.csv'
                output_filename = os.path.join(context.output_folder, output_filename)
                message = cls._KICAD_CLI.generate_bill_of_materials(
                    context.sch_filename, output_filename, 'lily_erp')
                if pca_id == '':
                    message += '\nWARNING: PCA ID is empty'
                convert_message = ''
                if os.path.isfile(output_filename):
                    data_in = cls._read_csv(output_filename)
                    data_in = sorted(data_in, key=lambda x: x['Lily_ID'])
                    data_out = []
                    quantity = 1
                    bom_type = 'Kit'
                    for record in data_in:
                        data_out.append({
                            'External ID': pca_id,
                            'Product': pca_id,
                            'Quantity': quantity,
                            'BoM Type': bom_type,
                            'BoM Lines/Component': record['Lily_ID'],
                            'BoM Lines/Quantity': int(record['QUANTITY'])
                        })
                        if pca_id is not None:
                            pca_id = None
                            quantity = None
                            bom_type = None
                        if record['Lily_ID'] == 'NO_ID':
                            convert_message = "WARNING: Component with 'NO_ID' in BOM"
                    field_names = ['External ID', 'Product', 'Quantity', 'BoM Type',
                                    'BoM Lines/Component', 'BoM Lines/Quantity']
                    cls._write_csv(output_filename, field_names, data_out)

                report += f'{message}\n'
                if convert_message != '':
                    report += f'{convert_message}\n'

            elif option == 'JLCPCB':
                report += f'Generate BOM: {option}\n'
                output_filename = f'{context.timestamp}_{context.design_name}_bom_jlcpcb.csv'
                output_filename = os.path.join(context.output_folder, output_filename)
                message = cls._KICAD_CLI.generate_bill_of_materials(
                    context.sch_filename, output_filename, 'jlcpcb'
                )
                # JLCPCB cannot handle ranges of designators like R1-R3 must be R1, R2, R3
                # We need to convert that
                if os.path.isfile(output_filename):
                    data_in = cls._read_csv(output_filename)
                    for record in data_in:
                        if '-' in record['Reference']:
                            new_range = []
                            parts = record['Reference'].split(',')
                            for p in parts:
                                if '-' in p:
                                    start, end = p.split('-')
                                    match = re.match(r'([A-Za-z]+)(\d+)', start)
                                    i = int(match.group(2))
                                    ref = f'{match.group(1)}{i}'
                                    while ref != end:
                                        new_range.append(ref)
                                        i += 1
                                        ref = f'{match.group(1)}{i}'
                                    new_range.append(end)
                                else:
                                    new_range.append(p)
                            record['Reference'] = ','.join(new_range)
                    cls._write_csv(output_filename, data_in[0].keys(), data_in)
                report += f'{message}\n'

            else:
                raise Exception(f"BOM option '{option}' is not defined")
        return report.strip()

    @classmethod
    def _create_gerbers_and_drill(cls, context: ProcessContext):
        props = DesignParser.get_pcb_properties(context.pcb_filename)
        n_layers = props.get('n_layers', 0)
        gerber_output_folder = os.path.join(context.output_folder, f'{context.timestamp}_gerbers')
        zip_filename = os.path.join(
            context.output_folder, f'{context.timestamp}_{context.design_name}_gerbers.zip'
        )
        message = f'Number of copper layers: {n_layers}\n'
        message += cls._KICAD_CLI.generate_gerbers(
            context.pcb_filename, gerber_output_folder, zip_filename, n_layers
        )
        return message

    @classmethod
    def _create_position_file(cls, context: ProcessContext):
        output_filename = f'{context.timestamp}_{context.design_name}_position.csv'
        output_filename = os.path.join(context.output_folder, output_filename)
        message = cls._KICAD_CLI.generate_position_file(context.pcb_filename, output_filename)
        if os.path.isfile(output_filename):
            warnings = ''
            data_in = cls._read_csv(output_filename)
            data_out = []
            for record in data_in:
                data_out.append({
                    'Designator': record['Ref'],
                    'Mid X': record['PosX'],
                    'Mid Y': record['PosY'],
                    'Layer': record['Side'],
                    'Rotation': record['Rot']
                })
                not_on_raster = False
                i = record['PosX'].find('.')
                if i > -1:
                    not_on_raster = int(record['PosX'][i + 2:]) > 0
                i = record['PosY'].find('.')
                if i > -1:
                    not_on_raster = not_on_raster or int(record['PosY'][i + 2:]) > 0
                if not_on_raster:
                    warnings += (f'\nWARNING: Component {record['Ref']} is not on a 0.1mm raster '
                                 f'({record['PosX']}, {record['PosY']})')

            if warnings != '':
                message += warnings

            cls._write_csv(
                output_filename, ['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'], data_out
            )
        return message

    @classmethod
    def _pcb_to_pdf(cls, context: ProcessContext):
        props = DesignParser.get_pcb_properties(context.pcb_filename)
        has_comp_bot = props.get('has_comp_bot', False)
        output_filename = f'{context.timestamp}_{context.design_name}_pcb_placement.pdf'
        output_filename = os.path.join(context.output_folder, output_filename)
        return cls._KICAD_CLI.generate_pcb_pdf(context.pcb_filename, output_filename, has_comp_bot)

    @classmethod
    def _create_odb(cls, context: ProcessContext):
        output_filename = f'{context.timestamp}_{context.design_name}_odb.zip'
        output_filename = os.path.join(context.output_folder, output_filename)
        return cls._KICAD_CLI.generate_odb(context.pcb_filename, output_filename)

    @classmethod
    def _create_3d_model(cls, context: ProcessContext):
        output_filename = f'{context.timestamp}_{context.design_name}_pcb.step'
        output_filename = os.path.join(context.output_folder, output_filename)
        return cls._KICAD_CLI.generate_step(context.pcb_filename, output_filename)

    ##########
    # Public #
    ##########

    @classmethod
    def run(cls, context: ProcessContext, report, logger):
        cls._logger = logger

        report.append(cls._log('Generate output'))
        cls._set_kicad_cli()
        report.append(cls._log(f'KiCad CLI version: {cls._KICAD_CLI.get_version()}'))

        for output in context.outputs:
            report.append(cls._log(f'\nGenerate {output}'))

            if output == 'Schematics to PDF':
                report.append(
                    cls._schematics_to_pdf(context)
                )

            elif output == 'Bill of materials (BOM)':
                report.append(cls._create_bom(context))

            elif output == 'Gerbers and drill data':
                report.append(cls._create_gerbers_and_drill(context))

            elif output == 'Position data':
                report.append(cls._create_position_file(context))

            elif output == 'PCB placement to PDF':
                report.append(cls._pcb_to_pdf(context))

            elif output == 'ODB+':
                report.append(cls._create_odb(context))

            elif output == 'PCB 3D model (step)':
                report.append(cls._create_3d_model(context))

            else:
                raise Exception(f"Output '{output}' is not defined")


if __name__ == '__main__':

    from toolbox.tools.process_design.src.process_context import test_context

    _messages = []
    OutputGenerator.run(test_context(), _messages, print)
    for m in _messages:
        print(m)
