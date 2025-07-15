from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive

from DirectoryTable import DirectoryTable
from FileElement import FileElement
from FilterCheckbox import FilterCheckbox
from utils import convert_size


class TypesCheckboxLine(Horizontal):
    directory = reactive("")
    checkboxes = reactive([])

    def __init__(self, directory: str = "", show_bytes=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory = directory
        self.show_bytes = show_bytes
        self.checked_types = {}
        self.convert_size = (lambda x: x) if self.show_bytes else convert_size

    def compose(self) -> ComposeResult:
        for checkbox in self.checkboxes:
            yield checkbox

    def watch_directory(self, directory: str) -> None:
        self.refresh_checkboxes()

    def get_types_data(self) -> list[tuple[str, int]]:
        if not self.directory:
            return []
        dir_element: FileElement = self.app.dirs.get(self.directory)
        if not dir_element:
            return []
        mime_types: dict[str, int] = {}
        for child in dir_element.children:
            if child.mime_type in mime_types:
                mime_types[child.mime_type] += child.size
            else:
                self.checked_types[child.mime_type] = True
                mime_types[child.mime_type] = child.size
        sizes = list(sorted(mime_types.items(), key=lambda el: el[1], reverse=True))
        return sizes

    def refresh_checkboxes(self):
        types_data = self.get_types_data()
        self.remove_children()
        self.checkboxes.clear()
        new_checkboxes = []
        for el in types_data:
            checkbox = FilterCheckbox(el[0], el[1], show_bytes=self.show_bytes, value=True)
            new_checkboxes.append(checkbox)
        self.checkboxes.extend(new_checkboxes)
        for checkbox in new_checkboxes:
            self.mount(checkbox)

    def on_checkbox_changed(self, event: FilterCheckbox.Changed):
        checkbox = event.checkbox
        self.checked_types[checkbox.text] = not self.checked_types[checkbox.text]
        # self.app.notify(str(self.checked_users))
        directory_table = self.app.query_one(DirectoryTable)
        directory_table.filter(self.app.filter)

    def filter(self, file_element: FileElement) -> bool:
        possible_types = [mime_type for mime_type in self.checked_types if self.checked_types[mime_type]]
        return file_element.mime_type in possible_types