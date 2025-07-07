import os
import pwd

from textual import events, work
from textual.app import App, ComposeResult, RenderResult
from textual.containers import Vertical
from textual.widgets import DataTable, LoadingIndicator, Footer
from textual.worker import Worker, WorkerState

from AddressLine import AddressLine
from FileElement import FileElement
from DirectoryTable import DirectoryTable
from utils import size_sort, name_sort, safe_walk, get_size, get_owner, mtime_sort


class ScanerApp(App):
    CSS_PATH = "disc_usage.tcss"
    BINDINGS = [
        ("n", "sort_by_name", "Сортировка по имени"),
        ("s", "sort_by_size", "Сортировка по размеру"),
        ("n", "sort_by_owner", "Сортировка по владельцу"),
        ("t", "sort_by_mtime", "Сортировка по времени изменения"),
        ("ctrl+c", "quit", "Выход"),
    ]

    def __init__(self, start_dir: str, show_bytes: bool = False):
        super().__init__()
        self.start_dir = os.path.abspath(start_dir)
        self.dirs = {self.start_dir: FileElement("", self.start_dir)}
        self.show_bytes = show_bytes

    def on_mount(self) -> None:
        self.styles.background = "transparent"
        self.scan_directory()

    @work(thread=True)
    def scan_directory(self):
        # self.dirs = {self.start_dir: FileElement("", self.start_dir)}
        for root, folders, files in safe_walk(self.start_dir, followlinks=False):
            for curr_file in files:
                path = os.path.join(root, curr_file)
                self.dirs[path] = FileElement(root, curr_file, self.dirs[root])
            for folder in folders:
                path = os.path.join(root, folder)
                self.dirs[path] = FileElement(root, folder, self.dirs[root])

    def compose(self) -> ComposeResult:
        yield AddressLine(address=self.start_dir, show_bytes=self.show_bytes)
        with Vertical():
            yield LoadingIndicator()
        yield DirectoryTable(directory=self.start_dir, show_bytes=self.show_bytes)
        yield Footer()

    async def on_worker_state_changed(self, event: Worker.StateChanged):
        # self.notify(event.state.name)
        if event.state == WorkerState.SUCCESS:
            loader = self.query_one(LoadingIndicator)
            await loader.remove()
            table = self.query_one(DirectoryTable)
            table.refresh_data()
            address_line = self.query_one(AddressLine)
            address_line.refresh_size()
            # await self.mount(DirectoryTable(directory=self.start_dir))

    def action_sort_by_name(self):
        table = self.query_one(DirectoryTable)
        table.sort("name", key=name_sort)

    def action_sort_by_owner(self):
        table = self.query_one(DirectoryTable)
        table.sort("owner")

    def action_sort_by_mtime(self):
        table = self.query_one(DirectoryTable)
        table.sort("mtime", key=mtime_sort, reverse=True)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key
        table = self.query_one(DirectoryTable)
        selected_row_data = table.get_row(row_key)
        name = selected_row_data[0]
        if name == " ..":
            prev_path = table.directory[:table.directory.rfind("/")]
            table.directory = prev_path
        else:
            new_path = os.path.join(table.directory, name[3:])
            if os.path.isdir(new_path) and not os.path.islink(new_path):
                table.directory = new_path
        address_line = self.query_one(AddressLine)
        address_line.address = table.directory


    def action_sort_by_size(self):
        table = self.query_one(DirectoryTable)
        table.sort("size", key=size_sort, reverse=True)
