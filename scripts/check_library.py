"""
Checks the library and report the errors
"""


def _show_report(messages):
    column_widths = [4, 7]
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
    return len(messages) == 0


if __name__ == "__main__":

    from models.erp_checker import ErpChecker
    from models.footprints_checker import FootprintsChecker
    from models.projects_checker import ProjectsChecker
    from toolbox.models.symbols_checker import SymbolsChecker

    do_continue = _show_report(SymbolsChecker.run())
    if do_continue:
        do_continue = _show_report(FootprintsChecker.run())
    if do_continue:
        do_continue = _show_report(ErpChecker.run())
    if do_continue:
        _show_report(ProjectsChecker.run())
