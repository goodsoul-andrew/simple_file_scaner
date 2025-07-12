import os
import pwd
from datetime import datetime

measures = {"b": 1024, "Kb": 1048576, "Mb": 1073741824, "Gb": 1073741824 * 1024, "Tb": 1073741824 * 1024 * 1024}


def convert_size(size: int) -> str:
    # return f"{size} b"
    for m in measures:
        if size < measures[m]:
            s = round(size / (measures[m] / 1024), 2)
            if int(s) == s:
                s = int(s)
            return f"{s} {m}"
    s = round(size / measures['Tb'], 2)
    if int(s) == s:
        s = int(s)
    return f"{s} Tb"


def size_sort(size: int | str) -> float:
    if size is None:
        return float('inf')
    if type(size) == str:
        s, m = size.split()
        s = float(s)
        m = measures[m] / 1024
        return s * m
    return size


def name_sort(name: str):
    if name == " ..":
        return -float('inf'), name
    if name[1] == '📁':
        return 0, name[2:]
    return 1, name[2:]


def get_parent_dir(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def get_owner(path):
    uid = os.stat(path).st_uid
    user = pwd.getpwuid(uid)[0]
    return user


def get_last_mod_time(path):
    if os.path.islink(path):
        stat_info = os.lstat(path)
        return stat_info.st_mtime
    else:
        stat_info = os.stat(path)
        return stat_info.st_mtime


def get_size(path):
    if os.path.islink(path):
        stat_info = os.lstat(path)
        return stat_info.st_size
    else:
        stat_info = os.stat(path)
        return stat_info.st_size


def safe_walk(directory, followlinks=False):
    visited = set()
    pending = set([directory])
    stack = [directory]
    root = get_parent_dir(directory)

    def get_content(dirname):
        abs_path = os.path.abspath(dirname)
        content = os.listdir(abs_path)
        files = []
        folders = []
        for el in content:
            path = os.path.join(dirname, el)
            if os.path.isfile(path):
                files.append(el)
            elif os.path.isdir(path):
                folders.append(el)
        return abs_path, folders, files

    while len(stack) > 0:
        current = stack.pop(0)
        pending.remove(current)
        dirname, folders, files = get_content(current)
        visited.add(current)
        yield dirname, folders, files
        for folder in folders:
            path = os.path.join(dirname, folder)
            if os.path.islink(path):
                path = os.readlink(path)
            if (not os.path.islink(path) or (os.path.islink(path) and followlinks)) and path not in visited and path not in pending:
                stack.append(path)
                pending.add(path)


def convert_utime(utime: float) -> str:
    dt_object = datetime.fromtimestamp(utime)
    formatted_string = dt_object.strftime("%H:%M:%S %d.%m.%Y")
    return formatted_string


def mtime_sort(date_string):
    return datetime.strptime(date_string, "%H:%M:%S %d.%m.%Y")