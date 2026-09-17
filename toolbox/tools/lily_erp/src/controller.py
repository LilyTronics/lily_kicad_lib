"""
Controller for tool template.
"""

import wx

from toolbox.tools.common.controller_base import ControllerBase
from toolbox.tools.lily_erp.src.create_erp_import import create_erp_import_file
from toolbox.tools.lily_erp.src.symbol_data import get_erp_parts
from toolbox.common.erp_connect import get_components_from_erp
from toolbox.common.product_categories import ProductCategories
from toolbox.common.update_symbols import update_symbol_property


class Controller(ControllerBase):

    def __init__(self, *args, **kwargs):
        self._active_item = None
        super().__init__(*args, **kwargs)

        self.tool_view.Bind(wx.EVT_BUTTON, self._on_reload, id=self.tool_view.ID_BTN_RELOAD_LIST)
        self.tool_view.Bind(wx.EVT_CHOICE, self._on_category_select,
                            self.tool_view.ID_CMB_CATEGORIES)
        self.tool_view.Bind(wx.EVT_BUTTON, self._on_generate_click, self.tool_view.ID_BTN_GENERATE)
        self.tool_view.Bind(wx.EVT_BUTTON, self._on_apply_code_click,
                            self.tool_view.ID_BTN_APPLY_CODE)

        wx.CallAfter(self._load_parts)
        wx.CallAfter(self._load_categories)

    ###########
    # Private #
    ###########

    def _load_parts(self):
        self.logger.add_to_console('Load parts')
        parts = get_erp_parts()
        self.tool_view.show_parts(parts)
        self.logger.add_to_console(f'Loaded {len(parts)} parts')

    def _load_categories(self):
        self.tool_view.set_categories(ProductCategories.get_categories())

    ##################
    # Event handlers #
    ##################

    def _on_reload(self, event):
        self.logger.clear_console()
        self._load_parts()
        event.Skip()

    def _on_category_select(self, event):
        category = ProductCategories.get_category(event.GetString())
        if category is not None:
            self.tool_view.enable_controls(category)
        event.Skip()

    def _on_generate_click(self, event):
        error = ''
        category = None

        data = self.tool_view.get_input()
        category = ProductCategories.get_category(data['category'])

        if category is None:
            error = f"Category '{data['category']}' not found."
        else:
            series = ''
            if ',' in data['series']:
                series = data['series'].split(',')[0]
            id_filter = f'{category.product_id[:category.product_id.index('-') + 1]}{series}%'
            result = get_components_from_erp(self.logger.add_to_console, id_filter)
            if not result[0]:
                error = 'Failed to retrieve components from the ERP database.'
            else:
                product_ids = sorted(list(map(lambda r: r['default_code'], result[1])))
                output = {
                    'low': 'na' if len(product_ids) == 0 else product_ids[0],
                    'high': 'na' if len(product_ids) == 0 else product_ids[-1],
                    'next': ProductCategories.generate_next_code(
                        category, product_ids, data['series'], data['value']
                    )
                }
                self.tool_view.set_product_ids(output)

        if error != '':
            dlg = wx.MessageDialog(
                self.tool_view, error, 'Generate product ID', style=wx.OK | wx.ICON_EXCLAMATION
            )
            dlg.ShowModal()
            dlg.Destroy()

        event.Skip()

    def _on_apply_code_click(self, event):
        new_code = self.tool_view.get_new_code()
        selected_part = self.tool_view.get_selected_part()
        if new_code == '' or selected_part == '':
            message = ''
            if new_code == '':
                message = 'Generate a code.'
            elif selected_part == '':
                message = 'Select a part.'
            with wx.MessageDialog(
                    self.tool_view, message, 'Generate product ID',
                    style=wx.OK | wx.ICON_EXCLAMATION
                ) as dlg:
                dlg.ShowModal()
        else:
            self.logger.add_to_console(f"Apply '{new_code}' to '{selected_part}'")
            try:
                update_symbol_property(selected_part, 'Lily_ID', new_code)
                create_erp_import_file(selected_part, new_code, self.tool_view)
            except Exception as e:
                message = f'Error applying new code to selected part:\n{e}'
                with wx.MessageDialog(
                        self.tool_view, message, 'Generate product ID',
                        style=wx.OK | wx.ICON_EXCLAMATION
                    ) as dlg:
                    dlg.ShowModal()
            self._load_parts()
        event.Skip()


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.lily_erp.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
