from typing import Callable

from textual.widget import Widget
from textual.widgets import DataTable
from FileElement import FileElement
from textual.reactive import reactive

from utils import convert_size, convert_utime


class DirectoryTable(DataTable):
    directory = reactive("")

    def __init__(self, directory: str = "", show_bytes: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_type = "row"
        self.add_column("Имя", key="name")
        self.add_column("Размер", key="size")
        self.add_column("Владелец", key="owner")
        self.add_column("Последнее изменение", key="mtime")
        self.add_column("", key="visual_size")
        self.start_directory = directory
        self.directory = directory
        self.show_bytes = show_bytes
        self.convert_size = (lambda x: x) if self.show_bytes else convert_size

    def on_mount(self) -> None:
        self.refresh_data()

    def watch_directory(self, directory: str) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self.clear()
        if not self.directory:
            return
        dir_element: FileElement = self.app.dirs.get(self.directory)

        if not dir_element:
            return

        rows = []
        for child in dir_element.children:
            name = f"{child.type_icon} {child.name}"
            rows.append([name, child.size, child.owner, convert_utime(child.mtime), child.visual_size()])
        rows = list(sorted(rows, key=lambda el: -el[1]))
        for el in rows:
            el[1] = self.convert_size(el[1])
        if self.directory != self.start_directory:
            self.add_row(" ..", self.convert_size(dir_element.size), dir_element.owner, convert_utime(dir_element.mtime), key=" ..")
        self.add_rows(rows)

    def filter(self, key: Callable[[FileElement], bool]):
        self.clear()
        if not self.directory:
            return
        dir_element: FileElement = self.app.dirs.get(self.directory)
        if not dir_element:
            return
        children = [ch for ch in dir_element.children if key(ch)]
        rows = []
        for child in children:
            name = f"{child.type_icon} {child.name}"
            rows.append([name, child.size, child.owner, convert_utime(child.mtime), child.visual_size()])
        rows = list(sorted(rows, key=lambda el: -el[1]))
        for el in rows:
            el[1] = self.convert_size(el[1])
        if self.directory != self.start_directory:
            self.add_row(" ..", self.convert_size(dir_element.size), dir_element.owner,
                         convert_utime(dir_element.mtime), key=" ..")
        self.add_rows(rows)
