import os
import pwd

from textual import events, work
from textual.app import App, ComposeResult, RenderResult
from textual.containers import Vertical
from textual.widgets import DataTable, LoadingIndicator, Footer, Checkbox
from textual.worker import Worker, WorkerState

from AddressLine import AddressLine
from FileElement import FileElement
from DirectoryTable import DirectoryTable
from TypesCheckboxLine import TypesCheckboxLine
from UsersCheckboxLine import UsersCheckboxLine
from MtimeCheckboxLine import MtimeCheckboxLine
from utils import size_sort, name_sort, safe_walk, get_size, get_owner, mtime_sort


class ScanerApp(App):
    CSS_PATH = "disc_usage.tcss"
    BINDINGS = [
        ("n", "sort_by_name", "Сортировка по имени"),
        ("s", "sort_by_size", "Сортировка по размеру"),
        ("o", "sort_by_owner", "Сортировка по владельцу"),
        ("t", "sort_by_mtime", "Сортировка по времени изменения"),
        ("ctrl+c", "quit", "Выход"),
    ]

    def __init__(self, start_dir: str, show_bytes: bool = False):
        super().__init__()
        self.start_dir = os.path.abspath(start_dir)
        self.dirs: dict[str, FileElement] = {self.start_dir: FileElement("", self.start_dir)}
        self.users = set()
        self.filters = []
        self.show_bytes = show_bytes

    def on_mount(self) -> None:
        self.styles.background = "transparent"
        self.scan()
        users_checkboxes = self.query_one(UsersCheckboxLine)
        types_checkboxes = self.query_one(TypesCheckboxLine)
        mtime_checkboxes = self.query_one(MtimeCheckboxLine)
        self.filters.append(users_checkboxes)
        self.filters.append(types_checkboxes)
        self.filters.append(mtime_checkboxes)

    def filter(self, file_element: FileElement) -> bool:
        filters_res = [filter_table.filter(file_element) for filter_table in self.filters]
        return all(filters_res)

    @work(thread=True)
    def scan(self):
        self.scan_directory()

    def scan_directory(self):
        for root, folders, files in os.walk(self.start_dir, followlinks=False):
            for curr_file in files:
                path = os.path.join(root, curr_file)
                self.dirs[path] = FileElement(root, curr_file, self.dirs[root])
                self.users.add(self.dirs[path].owner)
            for folder in folders:
                path = os.path.join(root, folder)
                self.dirs[path] = FileElement(root, folder, self.dirs[root])
                self.users.add(self.dirs[path].owner)

    def compose(self) -> ComposeResult:
        yield AddressLine(address=self.start_dir, show_bytes=self.show_bytes)
        with Vertical():
            yield LoadingIndicator()
        yield DirectoryTable(directory=self.start_dir, show_bytes=self.show_bytes)
        # yield UsersLine(directory=self.start_dir, show_bytes=self.show_bytes)
        yield UsersCheckboxLine(directory=self.start_dir, show_bytes=self.show_bytes)
        yield TypesCheckboxLine(directory=self.start_dir, show_bytes=self.show_bytes)
        yield MtimeCheckboxLine(directory=self.start_dir, show_bytes=self.show_bytes)
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
            users_checkboxes = self.query_one(UsersCheckboxLine)
            users_checkboxes.refresh_checkboxes()
            types_checkboxes = self.query_one(TypesCheckboxLine)
            types_checkboxes.refresh_checkboxes()
            mtime_checkboxes = self.query_one(MtimeCheckboxLine)
            mtime_checkboxes.refresh_checkboxes()

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
        users_checkboxes = self.query_one(UsersCheckboxLine)
        types_checkboxes = self.query_one(TypesCheckboxLine)
        mtime_checkboxes = self.query_one(MtimeCheckboxLine)
        selected_row_data = table.get_row(row_key)
        name = selected_row_data[0]
        if name == " ..":
            prev_path = table.directory[:table.directory.rfind("/")]
            table.directory = prev_path
        else:
            new_path = os.path.join(table.directory, name[3:])
            if os.path.isdir(new_path) and not os.path.islink(new_path):
                table.directory = new_path
        users_checkboxes.directory = table.directory
        types_checkboxes.directory = table.directory
        mtime_checkboxes.directory = table.directory
        address_line = self.query_one(AddressLine)
        address_line.address = table.directory


    def action_sort_by_size(self):
        table = self.query_one(DirectoryTable)
        table.sort("size", key=size_sort, reverse=True)

    def on_checkbox_change(self, event: Checkbox.Changed):
        checkbox = event.checkbox
        self.notify(str(checkbox.label))
