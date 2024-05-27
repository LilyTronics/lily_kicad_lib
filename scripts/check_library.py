"""
Checks the library and report the errors
"""


def _show_report(messages):
    column_widths = [0, 0]
    if len(messages) > 0:
        for message in messages:
            if len(message["item"]) > column_widths[0]:
                column_widths[0] = len(message["item"])
            if len(message["message"]) > column_widths[1]:
                column_widths[1] = len(message["message"])
        format_string = f"| {{item:{column_widths[0]}}} | {{message:{column_widths[1]}}} |"
        row_line = f"+-{"-" * column_widths[0]}-+-{"-" * column_widths[1]}-+"
        print(row_line)
        print(format_string.format(item="item", message="message"))
        print(row_line)
        for message in messages:
            print(format_string.format(item=message["item"], message=message["message"]))
        print(row_line)
    print(f"{len(messages)} messages\n")


if __name__ == "__main__":

    from models.footprints_checker import FootprintsChecker
    from models.symbols_checker import SymbolsChecker
    from models.test_design_checker import TestDesignChecker

    report_messages = []
    SymbolsChecker.run(report_messages)
    _show_report(report_messages)
    del report_messages[:]
    FootprintsChecker.run(report_messages)
    _show_report(report_messages)
    del report_messages[:]
    TestDesignChecker.run(report_messages)
    _show_report(report_messages)
