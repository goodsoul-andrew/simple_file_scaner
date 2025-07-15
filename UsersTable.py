from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import DataTable, Checkbox
from textual.widget import Widget

from FileElement import FileElement
from FilterCheckbox import FilterCheckbox
from utils import convert_size


class UsersTable(DataTable):
    directory = reactive("")

    def __init__(self, directory: str = "", show_bytes=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory = directory
        self.show_bytes = show_bytes
        self.convert_size = (lambda x: x) if self.show_bytes else convert_size

    def watch_directory(self, directory: str) -> None:
        self.refresh_data()
        pass

    def refresh_data(self):
        self.clear(columns=True)
        if not self.directory:
            return
        dir_element: FileElement = self.app.dirs.get(self.directory)

        if not dir_element:
            return

        users: dict[str, int] = dict()
        for child in dir_element.children:
            if child.owner in users:
                users[child.owner] += child.size
            else:
                users[child.owner] = child.size
        for user in users:
            self.add_column(user, key=user)
        self.add_row(*(self.convert_size(users[user]) for user in users))

class UsersLine(Widget):
    directory = reactive("")

    def __init__(self, directory: str = "", show_bytes=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory = directory
        self.show_bytes = show_bytes
        self.convert_size = (lambda x: x) if self.show_bytes else convert_size

    def watch_directory(self, directory: str) -> None:
        self.refresh()
        pass

    def render(self):
        if not self.directory:
            return
        dir_element: FileElement = self.app.dirs.get(self.directory)

        if not dir_element:
            return

        users: dict[str, int] = dict()
        for child in dir_element.children:
            if child.owner in users:
                users[child.owner] += child.size
            else:
                users[child.owner] = child.size
        sizes = list(sorted(users.items(), key=lambda el: el[1], reverse=True))
        res = [f"{el[0]}: {self.convert_size(el[1])}" for el in sizes]
        return " | ".join(res)
