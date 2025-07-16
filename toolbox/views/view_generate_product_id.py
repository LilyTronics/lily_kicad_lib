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

        self.SetSizer(sizer)


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(1)
