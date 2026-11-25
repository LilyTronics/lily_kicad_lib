"""
Checks the design blocks.
"""

import os

import toolbox.common.toolbox_data as ToolboxData

from toolbox.common.checkers.design_checker import DesignChecker


class DesignBlocksChecker:

    stdout = print


    @classmethod
    def run(cls):
        DesignChecker.stdout = cls.stdout

        report_messages = []
        for item in os.listdir(ToolboxData.DESIGN_BLOCKS_PATH):
            full_path = os.path.join(ToolboxData.DESIGN_BLOCKS_PATH, item)
            if os.path.isdir(full_path) and full_path.endswith('.kicad_block'):
                report_messages.extend(DesignChecker.run(full_path))

        return report_messages


if __name__ == '__main__':

    from toolbox.common.show_messages import show_messages

    show_messages(DesignBlocksChecker.run())
