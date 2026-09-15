"""
Main view for the tool runner.
"""

import wx


class ViewFrameMain(wx.Frame):

    ID_RELOAD = wx.NewIdRef()

    _MIN_SIZE = (900, 700)
    _SPACING = 5

    def __init__(self, title):
        super().__init__(None, title=title)

        panel = wx.Panel(self)
        self._image_list = wx.ImageList(32, 32)
        self._lbk_tools = wx.Listbook(panel, style=wx.BK_DEFAULT)
        self._lbk_tools.AssignImageList(self._image_list)
        btn_reload = wx.Button(panel, self.ID_RELOAD, 'Reload')

        self._txt_console = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_READONLY
        )
        self._txt_console.SetFont(
            wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        )

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self._lbk_tools, 2, wx.EXPAND | wx.ALL, self._SPACING)
        box.Add(btn_reload, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, self._SPACING)
        box.Add(self._txt_console, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, self._SPACING)

        panel.SetSizer(box)
        self.SetInitialSize(self._MIN_SIZE)

    ##########
    # Public #
    ##########

    def get_console(self):
        return self._txt_console

    def get_list_book(self):
        return self._lbk_tools

    def remove_tools(self):
        self._lbk_tools.DeleteAllPages()
        self._lbk_tools.DeleteAllPages()

    def add_tool(self, name, window, image):
        i = self._image_list.Add(image)
        self._lbk_tools.AddPage(window, name, imageId=i)


if __name__ == '__main__':

    from toolbox.tool_runner.main import run_main

    run_main()
