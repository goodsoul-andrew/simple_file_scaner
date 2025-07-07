import os

from textual.reactive import reactive
from textual.widget import Widget


class AddressLine(Widget):
    address = reactive("")

    def __init__(self, address: str = "", *children: Widget):
        super().__init__(*children)
        self.start_address = address
        self.address = address

    def render(self):
        res = os.path.abspath(self.address)
        width = os.get_terminal_size().columns - 1
        if len(res) > width:
            full_len = len(res)
            splitted = res.split("/")
            mid = len(splitted) // 2
            i = 0
            while full_len > width:
                to_cut = int(mid + (-1 ** i) * i)
                if i == 0:
                    i = 1
                    full_len -= len(splitted[to_cut]) + 1 - 3
                    splitted[to_cut] = "..."
                elif i > 0:
                    i = -i
                    full_len -= len(splitted[to_cut])
                    splitted[to_cut] = ""
                else:
                    i = -i + 1
                    full_len -= len(splitted[to_cut])
                    splitted[to_cut] = ""
            res = "/".join([el for el in splitted if el])
        return res

    def watch_address(self, address: str) -> None:
        self.refresh()