import os
import pwd


class FileElement:
    max_size = 0
    def __init__(self, root: str, name: str, parent=None):
        self.root = root
        self.name = name
        self.path = os.path.join(root, name)
        self.is_dir = os.path.isdir(self.path)
        self.is_link = os.path.islink(self.path)
        if self.is_link:
            stat = os.lstat(self.path)
        else:
            stat = os.stat(self.path)
        try:
            self.owner = pwd.getpwuid(stat.st_uid)[0]
        except KeyError:
            self.owner = "???"
        self.mtime = stat.st_mtime

        self.parent: FileElement = parent
        self.children: set[FileElement] = set()
        if self.parent is not None:
            self.parent.children.add(self)

        self._size = 0
        self.increase_size(stat.st_size)
        if self.size > FileElement.max_size:
            FileElement.max_size = self.size

    @property
    def size(self):
        return self._size

    def increase_size(self, value):
        self._size += value
        if self.parent and not self.is_link:
            self.parent.increase_size(value)
        if self.size > FileElement.max_size:
            FileElement.max_size = self.size

    def __str__(self):
        return f"({self.type_icon} {self.name}, size = {self.size}, owner={self.owner}, mtime={self.mtime})"

    def __repr__(self):
        return str(self)

    @property
    def type_icon(self) -> str:
        res = '🔗' if self.is_link else ' '
        if self.is_dir:
            return res + '📁'
        else:
            return res + '🗋'

    def visual_size(self):
        p = round(self.size / FileElement.max_size * 10)
        '''if p > 10:
            raise ValueError(f"{p} > 10, {self.size}, {FileElement.max_size}")'''
        return "=" * p + " " * (10 - p)

    def __hash__(self):
        return hash(self.path)