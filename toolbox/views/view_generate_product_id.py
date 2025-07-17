"""
View for the generate product ID tab
"""

import wx


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
        self._cmb_categories = wx.Choice(self)
        btn_reload = wx.Button(self, wx.ID_ANY, "Reload")

        lbl_placeholder = wx.StaticText(self, wx.ID_ANY, size=wx.Size(0, 0))

        lbl_series = wx.StaticText(self, wx.ID_ANY, "Series")
        lbl_series.Hide()
        cmb_series = wx.Choice(self)
        cmb_series.Hide()
        lbl_version = wx.StaticText(self, wx.ID_ANY, "Version")
        lbl_version.Hide()
        txt_version = wx.TextCtrl(self)
        txt_version.Hide()

        btn_generate = wx.Button(self, wx.ID_ANY, "Generate product ID")

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
        grid.Add(lbl_placeholder, (1, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)

        grid.Add(btn_generate, (3, 0), (1, 2), wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_low, (5, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(txt_low, (5, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_high, (6, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(txt_high, (6, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_next, (7, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(txt_next, (7, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)

        grid.Add(lbl_series, (8, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(cmb_series, (8, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_version, (9, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(txt_version, (9, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)

        return grid

    def set_categories(self, categories):
        self._cmb_categories.Set(categories)


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(1)
