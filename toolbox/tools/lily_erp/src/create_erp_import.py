"""
Create and save a import file for the ERP system.
"""

import os
import wx

import toolbox.common.toolbox_data as ToolboxData


def create_erp_import_file(part_name, lily_id, parent_view=None):
    import_template = os.path.join(ToolboxData.TEMPLATES_PATH, 'erp_import_product.csv')
    with open(import_template, 'r', encoding='utf-8') as fp:
        content = fp.read()

    name = part_name.replace('_', ' ')
    content = content.replace('KICAD_NAME', name).replace('LILY_ID', lily_id)
    filename = None
    with wx.FileDialog(
            parent_view, 'Save file', style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
            wildcard="CSV files (*.csv)|*.csv", defaultFile=f'{part_name}.csv'
        ) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

    if filename is not None:
        if not filename.endswith('.csv'):
            filename += '.csv'
        with open(filename, 'w', encoding='utf-8') as fp:
            fp.write(content)


if __name__ == '__main__':

    app = wx.App()

    create_erp_import_file('bjt_npn_BC850B_sot23', '1234-12345')
