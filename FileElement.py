import os


class FileElement:
    def __init__(self, root: str, name: str, parent=None, size=0, is_folder=False, is_link=False, owner=None):
        self.root = root
        self.name = name
        self.owner = owner
        self.is_folder = is_folder
        self.is_link = is_link
        self.path = os.path.join(root, name)

        self.parent: FileElement = parent
        self.children: set[FileElement] = set()
        if self.parent is not None:
            self.parent.children.add(self)

        self._size = 0
        self.increase_size(size)

    @property
    def size(self):
        return self._size

    def increase_size(self, value):
        self._size += value
        if self.parent and not self.is_link:
            self.parent.increase_size(value)

    def __str__(self):
        return f"({self.type_icon} {self.name}, size = {self.size}, owner={self.owner})"

    def __repr__(self):
        return str(self)

    @property
    def type_icon(self) -> str:
        res = '🔗' if self.is_link else ' '
        if self.is_folder:
            return res + '📁'
        else:
            return res + '🗋'

    def __hash__(self):
        return hash(self.path)