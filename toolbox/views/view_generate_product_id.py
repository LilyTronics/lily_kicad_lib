"""
View for the generate product ID tab
"""

import wx

from toolbox.models.id_manager import IdManager


class ViewGenerateProductId(wx.Panel):

    _GAP = 5

    def __init__(self, parent, categories):
        super().__init__(parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._create_controls(categories), 0, wx.EXPAND | wx.ALL, self._GAP * 2)
        self.SetSizer(sizer)

    ###########
    # Private #
    ###########

    def _create_controls(self, categories):
        lbl_category = wx.StaticText(self, wx.ID_ANY, "Category:")
        cmb_categories = wx.Choice(self, choices=categories)

        grid = wx.GridBagSizer(self._GAP, self._GAP)
        grid.Add(lbl_category, (0, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(cmb_categories, (0, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)

        return grid


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(1)
