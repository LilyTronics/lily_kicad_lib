"""
Checks a design.
"""

from toolbox.common.parsers.design_parser import DesignParser
from toolbox.common.parsers.lib_parser import LibParser


class DesignChecker:

    stdout = print

    DESIGN_PROPS = ["design_name", "date", "revision", "pca_id", "pcb_id"]
    PART_MANDATORY_FIELDS = ['Status', 'Manufacturer', 'Manufacturer_ID', 'Lily_ID', 'JLCPCB_ID']
    SKIP_SYMBOL_FIELDS = ['Name', 'Extends']


    @classmethod
    def run(cls, project_folder):
        report_messages = []

        LibParser.stdout = cls.stdout
        lib_symbols = LibParser.get_symbols()
        lib_footprints = LibParser.get_footprints()

        DesignParser.stdout = cls.stdout
        sch_props = DesignParser.get_schematics_properties(project_folder)
        pcb_props = DesignParser.get_pcb_properties(project_folder)

        design = {
            'name': '',
            'symbols': DesignParser.get_symbols(project_folder),
            'footprints': DesignParser.get_footprints(project_folder),
            'sch_props': sch_props,
            'pcb_props': pcb_props
        }

        design['name'] = sch_props['design_name']
        if design['name'] == '':
            design['name'] = pcb_props['design_name']
        if design['name'] == '':
            design['name'] = 'no design name'

        cls._check_design_properties(design, report_messages)
        cls._check_if_symbols_not_in_library(design, lib_symbols, report_messages)
        cls._check_symbols_properties(design, lib_symbols, report_messages)
        cls._check_if_footprints_not_in_library(design, lib_footprints, report_messages)
        cls._check_footprint_properties(design, lib_footprints, report_messages)
        cls._check_symbols_vs_footprints(design, report_messages)

        return report_messages

    @classmethod
    def _check_design_properties(cls, design, report_messages):
        caller = f'({cls.__name__}._check_design_properties)'
        for prop in cls.DESIGN_PROPS:
            if design['sch_props'][prop] != design['pcb_props'][prop]:
                report_messages.append({
                    'item': f'{design['name']}',
                    'message': f'The {prop} is not equal between the schematics and the PCB '
                               f'{caller}'
                })


    @classmethod
    def _check_if_symbols_not_in_library(cls, design, lib_symbols, report_messages):
        caller = f'({cls.__name__}._check_if_symbols_not_in_library)'
        for design_symbol in design['symbols']:
            lib_name = design_symbol['lib_id'].split(':')[1]
            matches = list(filter(lambda x: x['Name'] == lib_name, lib_symbols))
            if len(matches) == 0:
                report_messages.append({
                    'item': lib_name,
                    'message': f'symbol in project {design['name']} is not in the library '
                               f'{caller}'
                })

    @classmethod
    def _check_symbols_properties(cls, design, lib_symbols, report_messages):
        caller = f'({cls.__name__}._check_symbols_properties)'
        for design_symbol in design['symbols']:
            lib_name = design_symbol['lib_id'].split(':')[1]
            matches = list(filter(lambda x: x['Name'] == lib_name, lib_symbols))
            if len(matches) > 0:
                lib_symbol = matches[0]
                # Check if keys are same
                # Fields in the design but not in the lib
                diff = list(set(design_symbol.keys()) - set(lib_symbol.keys()))
                diff.remove('lib_id')
                if len(diff) > 0:
                    report_messages.append({
                        'item': f'{design_symbol['Reference']} ({design['name']}, {lib_name})',
                        'message': 'symbol has fields that are not in the library: '
                                    f'{', '.join(diff)} {caller}'
                    })
                # Fields missing in the design symbol
                diff = list(set(lib_symbol.keys()) - set(design_symbol.keys()))
                diff.remove('Name')
                if 'Extends' in diff:
                    diff.remove('Extends')
                if 'Notes' in diff:
                    diff.remove('Notes')
                # Special parts, no mandatory fields
                # Do not populate
                if ('_do_not_populate_' in lib_name or
                        # Logos
                        lib_name.startswith('doc_logo_') or
                        # Power symbols
                        design_symbol['Reference'].startswith('#PWR') or
                        # Test points
                        lib_name.startswith('test_point_') or
                        # Cable to PCB connectors, footprint only, no physical component
                        (lib_name.startswith('con_') and 'cable_to_pcb' in lib_name) or
                        # Programming cable TC2030, footprint only no physical component
                        lib_name.startswith('con_TC2030') or
                        # Mechanical holes
                        lib_name.startswith('mec_hole_') or
                        # Fiducials
                        lib_name.startswith('mec_fiducial')):
                    i = 0
                    while i < len(diff):
                        if diff[i] in cls.PART_MANDATORY_FIELDS:
                            diff.pop(i)
                            i = 0
                        else:
                            i += 1
                if len(diff) > 0:
                    report_messages.append({
                        'item': f'{design_symbol['Reference']} ({design['name']}, {lib_name})',
                        'message': f'symbol has missing fields: {', '.join(diff)} {caller}'
                    })
                # Check property values
                for field in filter(lambda x: x not in cls.SKIP_SYMBOL_FIELDS, lib_symbol):
                    lib_value = lib_symbol[field]
                    design_value = design_symbol.get(field, None)
                    if field in cls.PART_MANDATORY_FIELDS and design_value is None:
                        design_value = lib_value
                    elif field == 'Notes' and lib_value == '':
                        design_value = lib_value
                    elif field == 'Reference':
                        reference = design_value[:len(lib_value)]
                        number = design_value[len(lib_value):]
                        if lib_value != reference:
                            report_messages.append({
                                'item': f'{design_symbol['Reference']} ({design['name']}, '
                                        f'{lib_name})',
                                'message': f"reference field does not start with '{lib_value}' "
                                            f'{caller}'
                            })
                        try:
                            int(number)
                        except ValueError:
                            report_messages.append({
                                'item': f'{design_symbol['Reference']} ({design['name']}, '
                                        f'{lib_name})',
                                'message': 'numeric part of reference field is not numeric '
                                            f"'{number}' {caller}"
                            })
                        # Prevent other messages for reference field
                        design_value = lib_value
                    elif field == 'Value':
                        # Values can be different in some cases
                        if (lib_value == 'Vxx' or lib_name.startswith('con_') or
                            lib_name.startswith('dio_led')):
                            lib_value = design_value
                    if lib_value != design_value:
                        report_messages.append({
                            'item': f'{design_symbol['Reference']} ({design['name']}, {lib_name})',
                            'message': f'field value for field {field} not correct: '
                                        f"'{design_value}' {caller}"
                        })

    @classmethod
    def _check_if_footprints_not_in_library(cls, design, lib_footprints, report_messages):
        caller = f'({cls.__name__}._check_if_footprints_not_in_library)'
        for design_footprint in design['footprints']:
            lib_name = design_footprint['Footprint'].split(':')[1]
            matches = list(filter(lambda x: x['Name'] == lib_name, lib_footprints))
            if len(matches) == 0:
                report_messages.append({
                    'item': lib_name,
                    'message': f'footprint in project {design['name']} is not in the library '
                               f'{caller}'
                })

    @classmethod
    def _check_footprint_properties(cls, design, lib_footprints, report_messages):
        caller = f'({cls.__name__}._check_footprint_properties)'
        for design_footprint in design['footprints']:
            lib_name = design_footprint['Footprint'].split(':')[1]
            matches = list(filter(lambda x: x['Name'] == lib_name, lib_footprints))
            if len(matches) > 0:
                lib_footprint = matches[0]
                lib_keys = list(lib_footprint.keys())
                lib_keys.remove('Name')
                design_keys = list(design_footprint.keys())
                if 'Footprint' in design_keys:
                    design_keys.remove('Footprint')
                for field in cls.PART_MANDATORY_FIELDS:
                    if field in design_keys:
                        design_keys.remove(field)
                # Fields in the lib but not in the design
                diff = list(set(lib_keys) - set(design_keys))
                if len(diff) > 0:
                    report_messages.append({
                        'item': f'{design_footprint['Reference']['Value']} '
                                f'({design['name']}, {lib_name})',
                        'message': f'footprint has missing fields: {', '.join(diff)} {caller}'
                    })
                # Fields in the design but not in the lib
                diff = list(set(design_keys) - set(lib_keys))
                if len(diff) > 0:
                    report_messages.append({
                        'item': f'{design_footprint['Reference']['Value']} '
                                f'({design['name']}, {lib_name})',
                        'message': f'footprint has fields that are not in the library: '
                                    f'{', '.join(diff)} {caller}'
                    })

                # Check values
                for lib_key in lib_keys:
                    lib_value = lib_footprint[lib_key]
                    design_value = design_footprint.get(lib_key, None)
                    lib_instance = type(lib_value)
                    design_instance = type(design_value)
                    if lib_instance != design_instance:
                        report_messages.append({
                            'item': f'{design_footprint['Reference']['Value']} '
                                    f'({design['name']}, {lib_name})',
                            'message': f"values of property '{lib_key}' are not of the same type: "
                                        f'{design_instance}, expected {lib_instance} {caller}'
                        })
                    else:
                        if isinstance(lib_value, dict):
                            diff = {
                                k: (lib_value[k], design_value[k]) for k in lib_value
                                if lib_value[k] != design_value[k]
                            }
                            # Value field is always different from library
                            for key in filter(lambda k: k not in ['Value'], diff):
                                report_messages.append({
                                    'item': f'{design_footprint['Reference']['Value']} '
                                            f'({design['name']}, {lib_name})',
                                    'message': f"property '{lib_key}' has a different value for "
                                               f'{key}: {diff[key]} {caller}'
                                })
                        else:
                            if lib_value != design_value:
                                report_messages.append({
                                    'item': f'{design_footprint['Reference']['Value']} '
                                            f'({design['name']}, {lib_name})',
                                    'message': f"property '{lib_key}' has a different value: "
                                                f'{design_value}, expected: {lib_value} {caller}'
                                })

    @classmethod
    def _check_symbols_vs_footprints(cls, design, report_messages):
        caller = f'({cls.__name__}._check_symbols_vs_footprints)'
        for design_symbol in design['symbols']:
            if design_symbol['Reference'].startswith('#PWR'):
                continue
            matches = list(filter(
                lambda x: x['Reference']['Value'] == design_symbol['Reference'],
                design['footprints']
            ))
            if len(matches) == 0:
                report_messages.append({
                    'item': f'{design_symbol['Reference']} '
                            f'({design['name']}, {design_symbol['lib_id']})',
                    'message': f'symbol has no matching footprint in the PCB design {caller}'
                })
            else:
                design_footprint = matches[0]
                symbol_keys = list(design_symbol.keys())
                symbol_keys.remove('lib_id')
                footprint_keys = list(design_footprint.keys())
                footprint_keys.remove('Attributes')
                if 'Reference_F.Fab' in footprint_keys:
                    footprint_keys.remove('Reference_F.Fab')
                if 'Model' in footprint_keys:
                    footprint_keys.remove('Model')
                if 'Pin_1_mark' in footprint_keys:
                    footprint_keys.remove('Pin_1_mark')

                # Fields in the symbol but not in the footprint
                diff = list(set(symbol_keys) - set(footprint_keys))
                if len(diff) > 0:
                    report_messages.append({
                        'item': f'{design_symbol['Reference']} '
                                f'({design['name']}, {design_symbol['lib_id']})',
                        'message': 'symbol has fields that are not in the footprint: '
                                    f'{', '.join(diff)} {caller}'
                    })
                # Fields in the footprint but not in the symbol
                diff = list(set(footprint_keys) - set(symbol_keys))
                if len(diff) > 0:
                    report_messages.append({
                        'item': f'{design_symbol['Reference']} '
                                f'({design['name']}, {design_symbol['lib_id']})',
                        'message': 'footprint has fields that are not in the symbol: '
                                    f'{', '.join(diff)} {caller}'
                    })

                # Check values
                for key in symbol_keys:
                    symbol_value = design_symbol[key]
                    footprint_value = design_footprint.get(key, None)
                    if isinstance(footprint_value, dict):
                        footprint_value = footprint_value.get('Value', None)
                    if symbol_value != footprint_value:
                        report_messages.append({
                            'item': f'{design_symbol['Reference']} '
                                    f'({design['name']}, {design_symbol['lib_id']})',
                            'message': f'value for field {key} in symbol is not matching '
                                        f'with footprint: {footprint_value}, expected '
                                        f'{symbol_value} {caller}'
                        })

        for design_footprint in design['footprints']:
            if design_footprint['Reference']['Value'] == 'REF**':
                continue
            matches = list(filter(
                lambda x: x['Reference'] == design_footprint['Reference']['Value'],
                design['symbols']
            ))
            if len(matches) == 0:
                report_messages.append({
                    'item': f'{design_footprint['Reference']['Value']} '
                            f'({design['name']}, {design_footprint['Footprint']})',
                    'message': 'footprint has no matching symbol in the schematics design '
                                f'{caller}'
                })

if __name__ == '__main__':

    import os

    import toolbox.common.toolbox_data as ToolboxData

    from toolbox.common.show_messages import show_messages


    _test_project_folder = os.path.join(ToolboxData.TEST_PROJECTS_PATH, 'lib_test', 'capacitors')

    show_messages(DesignChecker.run(_test_project_folder))
