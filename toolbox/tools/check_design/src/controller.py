"""
Controller for tool template.
"""

import os
import wx

from toolbox.common.checkers.projects_checker import ProjectsChecker
from toolbox.common.parsers.design_parser import DesignParser
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
        ProjectsChecker.stdout = self.logger.add_to_console
        messages = ProjectsChecker.check_project(project_folder)
        if len(messages) > 0:
            for message in messages:
                self.tool_view.add_message(message['item'])
                self.tool_view.add_message(f' - {message['message']}')
        else:
            self.tool_view.add_message('No messages from the project checker')

        self.logger.add_to_console("Check design properties")
        DesignParser.stdout = self.logger.add_to_console
        sch_props = DesignParser.get_schematics_properties(project_folder)
        self.tool_view.add_message("\nSchematics properties:")
        for key, value in sch_props.items():
            self.tool_view.add_message(f" - {key}: {value}")
        pcb_props = DesignParser.get_pcb_properties(project_folder)
        self.tool_view.add_message("PCB properties:")
        for key, value in pcb_props.items():
            self.tool_view.add_message(f" - {key}: {value}")

        # Test properties
        self.tool_view.add_message('\n')
        for prop in ["design_name", "date", "revision", "pca_id", "pcb_id"]:
            if sch_props[prop] != pcb_props[prop]:
                self.tool_view.add_message(
                    f'The {prop.replace('_', ' ')} is not equal between the schematics and the PCB'
                )

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
