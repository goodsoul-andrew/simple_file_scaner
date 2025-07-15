import os.path
import pytest
from app import ScanerApp


test_app = ScanerApp("test")
test_app.scan_directory()
print(test_app.dirs)

@pytest.mark.parametrize("path, expected_size", [
    ("test/empty", 4096),
    ("test/abcd.txt", 5),
    ("test/inner/link_music", 83),
    ("test/inner/", 5386),
    ("test", 4090600)
])
def test_size(path: str, expected_size: int):
    path = os.path.abspath(path)
    assert test_app.dirs[path].size == expected_size