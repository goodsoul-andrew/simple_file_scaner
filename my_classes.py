import os


class FileElement:
    def __init__(self, root: str, name: str, parent=None, size=0, is_folder=False):
        self.root = root
        self.name = name
        self.is_folder = is_folder
        self.path = os.path.join(root, name)

        self.parent: FileElement = parent
        self.children: set[FileElement] = set()
        if self.parent is not None:
            self.parent.children.add(self)

        self._size = 0
        self.size = size

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        if self.parent is not None:
            self.parent.size += value

    def __str__(self):
        return f"FileElement({self.name}, size = {self.size})"

    def __hash__(self):
        return hash(self.path)