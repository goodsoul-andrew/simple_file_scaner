from textual.reactive import reactive
from textual.widgets import Checkbox

from utils import convert_size


class FilterCheckbox(Checkbox):
    files_size = reactive(0)
    def __init__(self, label: str, size: int, show_bytes=False, value=False):
        super().__init__(label=label, value=value)
        self.text = label
        self.show_bytes = show_bytes
        self.convert_size = (lambda x: x) if self.show_bytes else convert_size
        self.files_size = size
        self.refresh_label()

    def refresh_label(self):
        self.label = f"{self.text} {self.convert_size(self.files_size)}"

    def watch_files_size(self, size: int):
        self.refresh_label()