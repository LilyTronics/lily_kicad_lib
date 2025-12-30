"""
Shows messages from the checkers in a table.
"""

def show_messages(messages):
    print(f"{len(messages)} messages")

    if len(messages) > 0:
        max_item = max(len(m['item']) for m in messages)
        max_msg = max(len(m['message']) for m in messages)

        separator = f"+{'-' * (max_item + 2)}+{'-' * (max_msg + 2)}+"

        # Print table
        print(separator)
        print(f"| {'iten'.ljust(max_item)} | {'message'.ljust(max_msg)} |")
        print(separator)
        for m in messages:
            print(f"| {m['item'].ljust(max_item)} | {m['message'].ljust(max_msg)} |")
        print(separator)
