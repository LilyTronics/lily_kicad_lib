"""
Controller for tool template.
"""

import os
import wx

from toolbox.common.checkers.design_checker import DesignChecker
from toolbox.tools.common.controller_base import ControllerBase


class Controller(ControllerBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_view.Bind(wx.EVT_BUTTON, self._on_check_click, self.tool_view.ID_BTN_CHECK)

    ###########
    # Private #
    ###########

    def _check_design(self, project_file):
        self.tool_view.clear_messages()
        project_folder = os.path.dirname(project_file)
        self.logger.add_to_console(f'Check design in folder: {project_folder}')
        DesignChecker.stdout = self.logger.add_to_console
        messages = DesignChecker.run(project_folder)
        if len(messages) > 0:
            for message in messages:
                self.tool_view.add_message(message['item'])
                self.tool_view.add_message(f' - {message['message']}')
        else:
            self.tool_view.add_message('No messages from the design checker')

    ##################
    # Event handlers #
    ##################

    def _on_check_click(self, event):
        self.logger.clear_console()
        self.logger.add_to_console('Check design')
        try:
            design_filename = self.tool_view.get_design_file()
            if not os.path.isfile(design_filename):
                raise Exception(f"The file '{design_filename}' does not exist")
            self._check_design(design_filename)
        except Exception as e:
            self.logger.add_to_console(f'{type(e).__name__}: {e}')
        event.Skip()


if __name__ == "__main__":

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.check_design.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
