"""
Panel with controls for the power supply
"""

import wx
import wx.dataview

import toolbox.tools.common.gui_sizes as GuiSizes


class Panel(wx.Panel):

    ID_BTN_RELOAD_LIST = wx.NewIdRef()
    ID_LIST = wx.NewIdRef()
    ID_CMB_CATEGORIES = wx.NewIdRef()
    ID_BTN_GENERATE = wx.NewIdRef()
    ID_BTN_APPLY_CODE = wx.NewIdRef()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._lst_parts = wx.dataview.TreeListCtrl(self, self.ID_LIST)
        self._lst_parts.AppendColumn('Lily ID', width=GuiSizes.WIDTH_MEDIUM[0])
        self._lst_parts.AppendColumn('Name')

        btn_reload = wx.Button(self, self.ID_BTN_RELOAD_LIST, 'Reload')

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self._lst_parts, 1, wx.EXPAND | wx.ALL, GuiSizes.BOX_SPACING)
        box.Add(btn_reload, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, GuiSizes.BOX_SPACING)
        box.Add(self._create_form(), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, GuiSizes.BOX_SPACING)

        self.SetSizer(box)

    ###########
    # Private #
    ###########

    def _create_form(self):
        lbl_category = wx.StaticText(self, wx.ID_ANY, 'Category:')
        self._cmb_categories = wx.Choice(self, self.ID_CMB_CATEGORIES)
        self._lbl_series = wx.StaticText(self, wx.ID_ANY, 'Series:')
        self._lbl_series.Disable()
        self._cmb_series = wx.Choice(self)
        self._cmb_series.Disable()
        self._lbl_value = wx.StaticText(self, wx.ID_ANY, 'Value:')
        self._lbl_value.Disable()
        self._txt_value = wx.TextCtrl(self)
        self._txt_value.Disable()
        btn_generate = wx.Button(self, self.ID_BTN_GENERATE, 'Generate product ID')

        lbl_low = wx.StaticText(self, wx.ID_ANY, 'Lowest existing ID:')
        lbl_high = wx.StaticText(self, wx.ID_ANY, 'Highest existing ID:')
        lbl_next = wx.StaticText(self, wx.ID_ANY, 'Next available ID:')
        self._txt_low = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        self._txt_high = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        self._txt_next = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        btn_apply_code = wx.Button(self, self.ID_BTN_APPLY_CODE, 'Apply to selected part')

        grid = wx.GridBagSizer(*GuiSizes.GRID_SPACING)
        grid.Add(lbl_category, (0, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._cmb_categories, (0, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._lbl_series, (1, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._cmb_series, (1, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._lbl_value, (2, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._txt_value, (2, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(btn_generate, (3, 0), (1, 2), wx.ALIGN_CENTER_VERTICAL)

        grid.Add(lbl_low, (0, 4), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._txt_low, (0, 5), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_high, (1, 4), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._txt_high, (1, 5), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_next, (2, 4), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._txt_next, (2, 5), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(btn_apply_code, (3, 4), (1, 2), wx.ALIGN_CENTER_VERTICAL)

        return grid

    def _restore_controls(self):
        self._lbl_series.Disable()
        self._cmb_series.Disable()
        self._lbl_value.Disable()
        self._txt_value.Disable()
        self._txt_low.Clear()
        self._txt_high.Clear()
        self._txt_next.Clear()

    ##########
    # Public #
    ##########

    def show_parts(self, parts):
        self._lst_parts.DeleteAllItems()
        root = self._lst_parts.GetRootItem()
        for part in parts:
            item = self._lst_parts.AppendItem(root, part['Lily_ID'])
            self._lst_parts.SetItemText(item, 1, part['Name'])

    def set_categories(self, categories):
        self._cmb_categories.Set(categories)
        self._restore_controls()
        self.Layout()

    def enable_controls(self, category):
        self._restore_controls()
        if 'value' in category.product_id:
            self._lbl_value.Enable()
            self._txt_value.Enable()
        if len(category.series) > 0:
            self._lbl_series.Enable()
            self._cmb_series.Enable()
            self._cmb_series.Set(category.series)
        self.Layout()

    def get_input(self):
        cat_index = self._cmb_categories.GetSelection()
        ser_index = self._cmb_series.GetSelection()
        return {
            'category': '' if cat_index < 0 else self._cmb_categories.GetString(cat_index),
            'series': '' if ser_index < 0 else self._cmb_series.GetString(ser_index),
            'value': self._txt_value.GetValue().strip()
        }

    def set_product_ids(self, product_ids):
        self._txt_low.SetValue(product_ids['low'])
        self._txt_high.SetValue(product_ids['high'])
        self._txt_next.SetValue(product_ids['next'])
        self.Layout()

    def get_new_code(self):
        return self._txt_next.GetValue().strip()

    def get_selected_part(self):
        name = ''
        item = self._lst_parts.GetSelection()
        if item.IsOk():
            name = self._lst_parts.GetItemText(item, 1)
        return name


if __name__ == '__main__':

    from toolbox.tools.common.test_tool import run_tool
    from toolbox.tools.lily_erp.tool_info import ToolInfo

    run_tool(ToolInfo.name, ToolInfo.panel, ToolInfo.controller)
