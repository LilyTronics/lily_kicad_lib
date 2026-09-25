"""
Checks the lib test projects.
"""

import os

import toolbox.common.toolbox_data as ToolboxData

from toolbox.common.checkers.design_checker import DesignChecker
from toolbox.common.parsers.design_parser import DesignParser
from toolbox.common.parsers.lib_parser import LibParser


class LibTestProjectsChecker:

    stdout = print


    @classmethod
    def run(cls):
        DesignParser.stdout = cls.stdout
        LibParser.stdout = cls.stdout
        DesignChecker.stdout = cls.stdout
        project_folders = []
        report_messages = []
        for current_folder, sub_folders, filenames in os.walk(ToolboxData.LIB_TEST_PROJECTS_PATH):
            sub_folders.sort()
            matches = list(filter(lambda x: x.endswith('.kicad_pro'), filenames))
            if len(matches) == 1:
                project_folders.append(current_folder)

        designs = {}
        for folder in project_folders:
            cls.stdout(f'Check project: {folder}')
            designs[folder[len(ToolboxData.TEST_PROJECTS_PATH) + 1:]] = {
                'symbols': DesignParser.get_symbols(folder),
                'footprints': DesignParser.get_footprints(folder)
            }

        lib_symbols = LibParser.get_symbols()
        lib_footprints = LibParser.get_footprints()

        cls._check_if_symbols_in_designs(lib_symbols, designs, report_messages)
        cls._check_if_footprints_in_designs(lib_footprints, designs, report_messages)

        for folder in project_folders:
            report_messages.extend(DesignChecker.run(folder))

        return report_messages

    @classmethod
    def _check_if_symbols_in_designs(cls, lib_symbols, designs, report_messages):
        caller = f'({cls.__name__}._check_if_symbols_in_designs)'
        for lib_symbol in lib_symbols:
            should_be_used = (
                # Parts should be used in designs
                lib_symbol.get('Extends', None) is not None or
                # Power symbols should be used in designs
                lib_symbol['Reference'] == '#PWR' or
                # Doc symbols should be used in designs
                lib_symbol['Name'].startswith('doc_') or
                # Specific symbol
                lib_symbol['Name'] == 'con_TC2030-IDC_lock'
            )

            is_used = False
            for design in designs:
                matches = list(filter(lambda x: x['lib_id'] == f'lily_symbols:{lib_symbol['Name']}',
                                        designs[design]['symbols']))

                # Only count if it is used if it is in one of the test designs
                if design.startswith('lib_test\\') and len(matches) > 0:
                    is_used = True

                if len(matches) > 0 and not should_be_used:
                    report_messages.append({
                        'item': lib_symbol['Name'],
                        'message': f'symbol should not be in the project {design} {caller}'
                    })

            if should_be_used and not is_used:
                report_messages.append({
                    'item': lib_symbol['Name'],
                    'message': f'symbol is not in one of the projects {caller}'
                })

    @classmethod
    def _check_if_footprints_in_designs(cls, lib_footprints, designs, report_messages):
        caller = f'({cls.__name__}._check_if_footprints_in_designs)'
        for lib_footprint in lib_footprints:
            for design in designs:
                matches = list(filter(
                    lambda x: x['Footprint'] == f'lily_footprints:{lib_footprint['Name']}',
                    designs[design]['footprints']
                ))
                if len(matches) > 0:
                    break
            else:
                report_messages.append({
                    'item': lib_footprint['Name'],
                    'message': f'footprint is not in one of the projects {caller}'
                })


if __name__ == '__main__':

    from toolbox.common.show_messages import show_messages

    show_messages(LibTestProjectsChecker.run())
