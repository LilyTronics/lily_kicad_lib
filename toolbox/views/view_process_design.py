"""
View for the process design tab
"""

import wx
import wx.lib.filebrowsebutton as filebrowse

from toolbox.models.id_manager import IdManager


class ViewProcessDesign(wx.Panel):

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
        lbl_file = wx.StaticText(self, wx.ID_ANY, "Design file:")
        self._btn_file = filebrowse.FileBrowseButton(self, labelText="", fileMask="*.kicad_pro")
        lbl_outputs = wx.StaticText(self, wx.ID_ANY, "Outputs:")
        self._chk_outputs = wx.CheckListBox(self, size=wx.Size(175, 150))
        lbl_bom_options = wx.StaticText(self, wx.ID_ANY, "BOM options:")
        self._chk_bom_options = wx.CheckListBox(self, size=wx.Size(125, 75))
        lbl_pca_id = wx.StaticText(self, wx.ID_ANY, "PCA ID:")
        self._txt_pca_id = wx.TextCtrl(self)
        lbl_layers = wx.StaticText(self, wx.ID_ANY, "Copper layers:")
        self._cmb_layers = wx.ComboBox(self, style=wx.CB_READONLY)
        self._cmb_layers.SetItems([str(i) for i in range(2, 33, 2)])
        self._cmb_layers.SetValue("2")
        lbl_options = wx.StaticText(self, wx.ID_ANY, "Misc. options:")
        self._chk_comp_bot = wx.CheckBox(self, wx.ID_ANY, label="Components on bottom side")
        btn_process = wx.Button(self, IdManager.ID_BTN_PROCESS, "Process design")

        grid = wx.GridBagSizer(self._GAP, self._GAP)
        grid.Add(lbl_file, (0, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._btn_file, (0, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        grid.Add(lbl_outputs, (1, 0), wx.DefaultSpan, wx.ALIGN_TOP)
        grid.Add(self._chk_outputs, (1, 1), wx.DefaultSpan, wx.ALIGN_TOP)
        grid.Add(lbl_bom_options, (2, 0), wx.DefaultSpan, wx.ALIGN_TOP)
        grid.Add(self._chk_bom_options, (2, 1), wx.DefaultSpan, wx.ALIGN_TOP)
        grid.Add(lbl_pca_id, (3, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._txt_pca_id, (3, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(lbl_layers, (4, 0), wx.DefaultSpan, wx.ALIGN_TOP)
        grid.Add(self._cmb_layers, (4, 1), wx.DefaultSpan, wx.ALIGN_TOP)
        grid.Add(lbl_options, (5, 0), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._chk_comp_bot, (5, 1), wx.DefaultSpan, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(btn_process, (7, 0), (1, 2))
        grid.AddGrowableCol(1)
        return grid

    ##########
    # Public #
    ##########

    def init_outputs(self, outputs):
        self._chk_outputs.SetItems(outputs)
        self._chk_outputs.SetCheckedStrings(outputs)

    def init_bom_options(self, options):
        self._chk_bom_options.SetItems(options)
        self._chk_bom_options.SetCheckedStrings(options)

    def get_design_file(self):
        return self._btn_file.GetValue().strip()

    def get_outputs(self):
        return self._chk_outputs.GetCheckedStrings()

    def get_bom_options(self):
        return self._chk_bom_options.GetCheckedStrings()

    def get_pca_id(self):
        return self._txt_pca_id.GetValue().strip()

    def get_layers(self):
        return int(self._cmb_layers.GetValue())

    def get_option_comp_bot(self):
        return self._chk_comp_bot.IsChecked()


if __name__ == "__main__":

    from toolbox.run_toolbox import run_toolbox

    run_toolbox(2)
