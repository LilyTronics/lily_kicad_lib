"""
View for the generate product ID tab
"""

import wx

from toolbox.models.id_manager import IdManager


class ViewGenerateProductId(wx.Panel):

    _GAP = 5

    def __init__(self, parent):
        super().__init__(parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._create_controls(), 0, wx.EXPAND | wx.ALL, self._GAP * 2)
        self.SetSizer(sizer)

    ###########
    # Private #
    ###########

    def _create_controls(self):
        lbl_category = wx.StaticText(self, wx.ID_ANY, "Category:")
        self._cmb_categories = wx.Choice(self, IdManager.ID_CMB_CATEGORIES)

        btn_reload = wx.Button(self, IdManager.ID_BTN_RELOAD, "Reload")

        self._lbl_series = wx.StaticText(self, wx.ID_ANY, "Series:")
        self._lbl_series.Disable()
        self._cmb_series = wx.Choice(self)
        self._cmb_series.Disable()
        self._lbl_value = wx.StaticText(self, wx.ID_ANY, "Value:")
        self._lbl_value.Disable()
        self._txt_value = wx.TextCtrl(self)
        self._txt_value.Disable()

        btn_generate = wx.Button(self, IdManager.ID_BTN_GENERATE, "Generate product ID")

        lbl_low = wx.StaticText(self, wx.ID_ANY, "Lowest existing ID:")
        lbl_high = wx.StaticText(self, wx.ID_ANY, "Highest existing ID:")
        lbl_next = wx.StaticText(self, wx.ID_ANY, "Next available ID:")
        txt_low = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        txt_high = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        txt_next = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)

        grid = wx.GridBagSizer(self._GAP, self._GAP)
        grid.Add(lbl_category, (0, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._cmb_categories, (0, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(btn_reload, (0, 2), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._lbl_series, (1, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._cmb_series, (1, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._lbl_value, (2, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._txt_value, (2, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)

        grid.Add(btn_generate, (4, 0), (1, 2), wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_low, (5, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(txt_low, (5, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_high, (6, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(txt_high, (6, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_next, (7, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(txt_next, (7, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)

        return grid

    ###########
    # Private #
    ###########

    def _restore_controls(self):
        self._lbl_series.Disable()
        self._cmb_series.Disable()
        self._lbl_value.Disable()
        self._txt_value.Disable()

    ##########
    # Public #
    ##########

    def set_categories(self, categories):
        self._cmb_categories.Set(categories)
        self._restore_controls()

    def enable_controls(self, properties):
        self._restore_controls()
        product_id = properties.get("product_id", "")
        series = properties.get("series", [])
        if "value" in product_id:
            self._lbl_value.Enable()
            self._txt_value.Enable()
        if len(series) > 0:
            self._lbl_series.Enable()
            self._cmb_series.Enable()
            self._cmb_series.Set(series)
        self.Layout()


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(1)
