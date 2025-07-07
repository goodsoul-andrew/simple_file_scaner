import os

from textual.reactive import reactive
from textual.widget import Widget

from utils import convert_size


class AddressLine(Widget):
    address = reactive("")
    dirsize = reactive(4096)

    def __init__(self, address: str = "", show_bytes=False, *children: Widget):
        super().__init__(*children)
        self.start_address = address
        self.address = address
        self.show_bytes = show_bytes
        self.convert_size = (lambda x: str(x)) if self.show_bytes else convert_size
        self.dirsize = self.app.dirs[self.address]

    def render(self):
        res = os.path.abspath(self.address)
        self.dirsize = self.app.dirs[self.address].size
        size = self.convert_size(self.dirsize)
        width = os.get_terminal_size().columns - 1
        if len(res) + len(size) + 1 > width:
            full_len = len(res)
            splitted = res.split("/")
            mid = len(splitted) // 2
            i = 0
            while full_len + len(size) + 1 > width:
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
        return f"{res} {size}"

    def watch_address(self, address: str) -> None:
        self.refresh()

    def refresh_size(self):
        self.dirsize = self.app.dirs[self.address].size