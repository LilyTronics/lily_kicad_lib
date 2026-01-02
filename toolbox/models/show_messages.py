"""
Shows messages from the checkers in a table.
"""

def show_messages(messages):
    max_line_length = 200

    print(f"{len(messages)} messages")

    if len(messages) > 0:
        max_item = max(len(m["item"]) for m in messages)
        max_msg = max(len(m["message"]) for m in messages)

        if max_item + max_msg + 7 > max_line_length:
            max_msg = max_line_length - max_item - 7

        separator = f"+{"-" * (max_item + 2)}+{"-" * (max_msg + 2)}+"

        # Print table
        print(separator)
        print(f"| {"item".ljust(max_item)} | {"message".ljust(max_msg)} |")
        print(separator)
        for m in messages:
            message = m["message"].ljust(max_msg)
            parts = []
            while len(message) > max_msg:
                pos = message.rfind(" ", 0, max_msg)
                if pos == -1:
                    break
                parts.append(message[:pos])
                message = message[pos + 1:]
            # Start with item
            print(f"| {m["item"].ljust(max_item)} |", end="")
            # Add parts
            for part in parts:
                print(f" {part.ljust(max_msg)} |")
                print(f"| {"".ljust(max_item)} |", end="")
            # Add remaining message or complete message if there were no parts
            print(f" {message.ljust(max_msg)} |")
        print(separator)


if __name__ == "__main__":

    messages = [
        { "item": "some item", "message": "There is some message"},
        { "item": "another item", "message": "There is another message"},
        { "item": "this item has a long message",
          "message": "This message is very long and should be properly wrapped so that we can see it correctly in the "
                     "terminal without the need for constantly resizing the terminal"},
    ]
    show_messages(messages)
