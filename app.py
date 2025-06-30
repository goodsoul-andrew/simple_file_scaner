from textual import events
from textual.widget import Widget
from textual.app import App, ComposeResult, RenderResult
from textual.widgets import DataTable
from my_classes import FileElement



class ScanerApp(App):
    CSS_PATH = "disc_usage.tcss"

    def __init__(self, start_dir: str, dirs: dict[str, FileElement]):
        super().__init__()
        self.dirs = dirs
        self.start_dir = start_dir

    def on_mount(self) -> None:
        self.styles.background = "transparent"
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("name", "size")
        rows = []
        for child in self.dirs[self.start_dir].children:
            name = f"{'📁' if child.is_folder else '🗋'} {child.name}"
            rows.append((name, child.size))
        rows = sorted(rows, key=lambda el: -el[1])
        table.add_rows(rows)

    def compose(self) -> ComposeResult:
        yield DataTable()