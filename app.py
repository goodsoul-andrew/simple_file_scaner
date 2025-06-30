import os.path
from markdown_it.rules_block import table
from textual import events
from textual.widget import Widget
from textual.app import App, ComposeResult, RenderResult
from textual.widgets import DataTable
from my_classes import FileElement
from DirectoryTable import DirectoryTable, size_sort


class ScanerApp(App):
    CSS_PATH = "disc_usage.tcss"
    BINDINGS = [
        ("n", "sort_by_name", "Сортировка по имени"),
        ("s", "sort_by_size", "Сортировка по размеру"),
        ("ctrl+c", "quit", "Выход"),
    ]

    def __init__(self, start_dir: str, dirs: dict[str, FileElement]):
        super().__init__()
        self.dirs = dirs
        self.start_dir = start_dir

    def on_mount(self) -> None:
        self.styles.background = "transparent"

    def compose(self) -> ComposeResult:
        yield DirectoryTable(directory=self.start_dir)

    def action_sort_by_name(self):
        table = self.query_one(DirectoryTable)
        table.sort("name")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key
        table = self.query_one(DirectoryTable)
        selected_row_data = table.get_row(row_key)
        name = selected_row_data[0]
        if name == "..":
            prev_path = table.directory[:table.directory.rfind("/")]
            table.directory = prev_path
        else:
            new_path = os.path.join(table.directory, name[2:])
            if os.path.isdir(new_path):
                table.directory = new_path


    def action_sort_by_size(self):
        table = self.query_one(DirectoryTable)
        table.sort("size", key=size_sort, reverse=True)
