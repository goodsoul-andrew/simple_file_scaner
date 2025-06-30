from textual.widget import Widget
from textual.widgets import DataTable
from my_classes import FileElement
from textual.reactive import reactive

class DirectoryTable(DataTable):
    directory = reactive("")

    def __init__(self, directory: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory = directory

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Name", "Size")
        self.refresh_data()

    def watch_directory(self, directory: str) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self.clear()
        if not self.directory:
            return
        dir_element = self.app.dirs.get(self.directory)

        if not dir_element:
            self.add_row("Directory not found", "")
            return

        rows = []
        for child in dir_element.children:
            name = f"{'📁' if child.is_folder else '🗋'} {child.name}"
            rows.append((name, str(child.size)))
        rows = sorted(rows, key=lambda el: -int(el[1]))
        self.add_rows(rows)