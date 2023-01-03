import argparse
from sys import argv
from unwind import unwind_file
from . import *

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outfile")
parser.add_argument("file", nargs='+')
args = parser.parse_args()

cu = CompilationUnit()

for file in args.file:
    cu.read_file(file)

if args.outfile == None:
    cu.print()
else:
    lines = cu.render()

    out_path = Path(args.outfile)
    if not out_path.parent.exists():
        raise FileNotFoundError(f"parent folder doesn't exist: {out_path.parent}")

    with open(args.outfile, 'w') as f:
        f.write(lines)

