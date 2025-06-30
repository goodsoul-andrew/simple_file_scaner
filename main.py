from argparse import ArgumentParser
import os
from my_classes import FileElement
from app import ScanerApp


parser = ArgumentParser()
parser.add_argument("start_dir",
                    help="директория для сканирования",
                    default=".")
args = parser.parse_args()
start_dir = args.start_dir
all_dirs = {start_dir: FileElement("", start_dir)}
for root, folders, files in os.walk(start_dir):
    for curr_file in files:
        path = os.path.join(root, curr_file)
        if os.path.isfile(path):
            s = os.path.getsize(path)
            all_dirs[path] = FileElement(root, curr_file, all_dirs[root], s, is_folder=False)
    for folder in folders:
        path = os.path.join(root, folder)
        if os.path.isdir(path):
            all_dirs[path] = FileElement(root, folder, all_dirs[root], is_folder=True)


app = ScanerApp(start_dir, all_dirs)
app.run()