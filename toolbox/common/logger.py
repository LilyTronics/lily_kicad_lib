"""
Logs messsages to a file and redirects stdout and stderror to the logger.
"""

import sys
import wx

from datetime import datetime


class Logger:

    _TIME_STAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, console_window):
        self._console = console_window
        self._org_stdout = sys.stdout
        sys.stdout = self
        sys.stderr = self

    ##########
    # Public #
    ##########

    def add_to_console(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for line in message.split('\n'):
            if line.strip() != '':
                line = f'{timestamp} - {line}'
                self._console.AppendText(f'{line}\n')
                self._org_stdout.write(f'{line}\n')
        wx.YieldIfNeeded()

    def clear_console(self):
        self._console.Clear()
        wx.YieldIfNeeded()


    ########################
    # Overrides for stdout #
    ########################

    def write(self, message):
        self.add_to_console(message)

    def flush(self):
        pass


if __name__ == '__main__':

    import threading


    def _generate_error():
        _ = 1 / 0


    app = wx.App()
    f = wx.Frame(None, title='Logger test')
    console = wx.TextCtrl(f, style=wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_READONLY)
    console.SetFont(
        wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    )
    f.SetPosition((100, 50))
    f.SetInitialSize((800, 400))
    f.Show()

    logger = Logger(console)
    logger.add_to_console('Console message')

    print('Stdout message')

    threading.Thread(target=_generate_error).start()

    app.MainLoop()
