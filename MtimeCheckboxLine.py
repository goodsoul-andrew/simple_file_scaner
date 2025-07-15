import datetime as dt

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive

from DirectoryTable import DirectoryTable
from FileElement import FileElement
from FilterCheckbox import FilterCheckbox
from utils import convert_size, convert_utime


class MtimeCheckboxLine(Horizontal):
    directory = reactive("")
    checkboxes = reactive([])

    def __init__(self, directory: str = "", show_bytes=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_bytes = show_bytes
        self.convert_size = (lambda x: x) if self.show_bytes else convert_size
        self.mtime_checks = {"сегодня": self.modified_today,
                             "на этой неделе": self.modified_this_week,
                             "в этом месяце": self.modified_this_month,
                             "в этом году": self.modified_this_year,
                             "давно": self.modified_long_ago}
        self.checked_mtimes = {mtime: True for mtime in self.mtime_checks}
        self.directory = directory

    def compose(self) -> ComposeResult:
        for checkbox in self.checkboxes:
            yield checkbox

    def watch_directory(self, directory: str) -> None:
        self.refresh_checkboxes()

    def modified_today(self, file_element: FileElement) -> bool:
        norm_time = dt.datetime.fromtimestamp(file_element.mtime).date()
        today = dt.date.today()
        return norm_time == today

    def modified_this_week(self, file_element: FileElement) -> bool:
        norm_time = dt.datetime.fromtimestamp(file_element.mtime)
        today = dt.date.today()
        return today.isocalendar()[:2] == norm_time.date().isocalendar()[:2]

    def modified_this_month(self, file_element: FileElement) -> bool:
        norm_time = dt.datetime.fromtimestamp(file_element.mtime)
        today = dt.date.today()
        return today.year == norm_time.year and today.month == norm_time.month

    def modified_this_year(self, file_element: FileElement) -> bool:
        norm_time = dt.datetime.fromtimestamp(file_element.mtime)
        today = dt.date.today()
        return today.year == norm_time.year

    def modified_long_ago(self, file_element: FileElement):
        return not self.modified_this_year(file_element)

    def get_mtime_data(self) -> list[tuple[str, int]]:
        if not self.directory:
            return []
        dir_element: FileElement = self.app.dirs.get(self.directory)
        if not dir_element:
            return []
        sizes_by_mtime = {mtime: 0 for mtime in self.mtime_checks}
        for child in dir_element.children:
            for mtime in self.mtime_checks:
                if self.mtime_checks[mtime](child):
                    sizes_by_mtime[mtime] += child.size
        return sizes_by_mtime.items()

    def refresh_checkboxes(self):
        if not self.is_mounted:
            return
        mtime_data = self.get_mtime_data()
        self.remove_children()
        self.checkboxes.clear()
        new_checkboxes = []
        for el in mtime_data:
            checkbox = FilterCheckbox(el[0], el[1], show_bytes=self.show_bytes, value=True)
            new_checkboxes.append(checkbox)
        self.checkboxes.extend(new_checkboxes)
        for checkbox in new_checkboxes:
            self.mount(checkbox)

    def on_checkbox_changed(self, event: FilterCheckbox.Changed):
        checkbox = event.checkbox
        self.checked_mtimes[checkbox.text] = not self.checked_mtimes[checkbox.text]
        # self.app.notify(str(self.checked_users))
        directory_table = self.app.query_one(DirectoryTable)
        directory_table.filter(self.app.filter)

    def filter(self, file_element: FileElement) -> bool:
        for mtime in self.mtime_checks:
            if self.checked_mtimes[mtime] and self.mtime_checks[mtime](file_element):
                return True
        return False