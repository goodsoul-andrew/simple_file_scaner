from textual.widget import Widget
from textual.widgets import DataTable
from my_classes import FileElement
from textual.reactive import reactive


def size_sort(size: int):
    if size is None:
        return float('inf')
    return size


class DirectoryTable(DataTable):
    directory = reactive("")

    def __init__(self, directory: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_type = "row"
        self.add_column("Имя", key="name")
        self.add_column("Размер", key="size")
        self.start_directory = directory
        self.directory = directory

    def on_mount(self) -> None:
        self.refresh_data()

    def watch_directory(self, directory: str) -> None:
        self.refresh_data()
        pass

    def refresh_data(self) -> None:
        self.clear()
        if not self.directory:
            return
        dir_element: FileElement = self.app.dirs.get(self.directory)

        if not dir_element:
            return

        rows = []
        for child in dir_element.children:
            name = f"{'📁' if child.is_folder else '🗋'} {child.name}"
            rows.append((name, child.size))
        rows = list(sorted(rows, key=lambda el: -el[1]))
        if self.directory != self.start_directory:
            prev_path = self.directory[:self.directory.rfind("/")]
            prev_size = self.app.dirs[prev_path].size
            self.add_row("..", key="..")
        self.add_rows(rows)
