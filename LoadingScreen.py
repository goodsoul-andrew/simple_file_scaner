from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, ProgressBar, LoadingIndicator
from textual.containers import Vertical, Horizontal
from textual.widgets import Label
from textual.reactive import reactive
from AddressLine import AddressLine

class LoadingScreen(Screen):

    def __init__(self, directory: str):
        super().__init__()
        self.directory = directory

    def compose(self) -> ComposeResult:
        with Vertical(id="loading-screen"):
            yield AddressLine(address=self.directory)
            with Horizontal(id="loading-animation-container"):
                yield LoadingIndicator()

