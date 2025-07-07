from argparse import ArgumentParser
import os
from FileElement import FileElement
from app import ScanerApp


parser = ArgumentParser()
parser.add_argument("start_dir",
                    help="директория для сканирования",
                    default=".")
parser.add_argument("-b", "--bytes",
                    help="показывать размер в байтах",
                    action="store_true")
args = parser.parse_args()
app = ScanerApp(args.start_dir, show_bytes=args.bytes)
app.run()