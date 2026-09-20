"""
Class that checks for unused items
"""

import os

import toolbox.common.toolbox_data as ToolboxData

from toolbox.common.parsers.lib_parser import LibParser


class UnusedItemsChecker:

    stdout = print

    _SKIP_SYMBOLS_UNUSED = ['0_new_symbol', 'Earth', 'GND', 'Vxx', 'con_TC2030-IDC_lock',
                            'doc_logo_', 'doc_pot_meter_scale_']
    _SKIP_FOOTPRINTS_UNUSED = ['0_new_footprint', 'mec_mouse_bytes']

    @classmethod
    def run(cls):
        LibParser.stdout = cls.stdout
        symbols = LibParser.get_symbols()
        footprints = LibParser.get_footprints()
        report_messages = []

        cls._check_unused_symbols(symbols, report_messages)
        cls._check_unused_datasheets(symbols, report_messages)
        cls._check_unused_footprints(symbols, footprints, report_messages)
        cls._check_unused_3d_models(footprints, report_messages)
        cls._check_unused_pictures(footprints, report_messages)

        return report_messages

    ############
    # Checkers #
    ############

    @classmethod
    def _check_unused_symbols(cls, symbols, report_messages):
        caller = f'({cls.__name__}._check_unused_symbols)'
        for symbol in filter(lambda s: s.get('Extends', None) is None, symbols):
            if symbol['Name'].startswith(tuple(cls._SKIP_SYMBOLS_UNUSED)):
                continue
            matches = list(filter(lambda x: x.get('Extends', None) == symbol['Name'], symbols))
            if len(matches) == 0:
                report_messages.append({
                    'item': symbol['Name'],
                    'message': f'Symbol is not used in any part {caller}'
                })

    @classmethod
    def _check_unused_datasheets(cls, symbols, report_messages):
        caller = f'({cls.__name__}._check_unused_datasheets)'
        file_path = f'{ToolboxData.ROOT_PATH}/docs/datasheets'
        for current_folder, sub_folders, filenames in os.walk(file_path):
            sub_folders.sort()
            filenames.sort()
            for filename in filenames:
                rel_path = os.path.join(
                    current_folder, filename
                ).replace('\\', '/')[len(file_path):]
                matches = list(filter(lambda x: rel_path in x['Datasheet'], symbols))
                if len(matches) == 0:
                    report_messages.append({
                        'item': rel_path,
                        'message': f'Datasheet file is not used in any symbol {caller}'
                    })

    @classmethod
    def _check_unused_footprints(cls, symbols, footprints, report_messages):
        caller = f'({cls.__name__}._check_unused_footprints)'
        for footprint in filter(lambda f: f['Name'] not in cls._SKIP_FOOTPRINTS_UNUSED, footprints):
            matches = list(filter(
                lambda x: x['Footprint'] == f'lily_footprints:{footprint['Name']}', symbols
            ))
            if len(matches) == 0:
                report_messages.append({
                    'item': footprint['Name'],
                    'message': f'Footprint is not used in any symbol {caller}'
                })

    @classmethod
    def _check_unused_3d_models(cls, footprints, report_messages):
        caller = f'({cls.__name__}._check_unused_3d_models)'
        model_files = [
            f for f in os.listdir(ToolboxData.MODELS_3D_PATH)
            if os.path.isfile(os.path.join(ToolboxData.MODELS_3D_PATH, f))
        ]
        for filename in model_files:
            rel_path = f'../3d_models/{filename}'
            matches = list(filter(lambda x: rel_path == x.get('Model', None), footprints))
            if len(matches) == 0:
                report_messages.append({
                    'item': filename,
                    'message': f'3D model file is not used in any footprint {caller}'
                })

    @classmethod
    def _check_unused_pictures(cls, footprints, report_messages):
        caller = f'({cls.__name__}._check_unused_pictures)'
        image_files = [
            f for f in os.listdir(ToolboxData.FOOTPRINTS_LIB_PATH)
            if (os.path.isfile(os.path.join(ToolboxData.FOOTPRINTS_LIB_PATH, f)) and
                f.endswith('.png'))
        ]
        for filename in image_files:
            matches = list(filter(lambda x: filename == f'{x['Name']}.png', footprints))
            if len(matches) == 0:
                report_messages.append({
                    'item': filename,
                    'message': f'picture is not matching any footprint {caller}'
                })


if __name__ == '__main__':

    from toolbox.common.show_messages import show_messages

    show_messages(UnusedItemsChecker.run())
