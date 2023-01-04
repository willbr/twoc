import argparse

from subprocess import Popen, PIPE
from sys import argv
from unwind import unwind_file
from . import *

def run(code):
    process = Popen(
            ['tcc', '-run', '-', '-Wall'],
            stdin=PIPE,
            stdout=PIPE)

    input_bytes = code.encode()
    outs, errs = process.communicate(input=input_bytes, timeout=15)
    output = outs.decode()

    print(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile")
    parser.add_argument("-run", help="run compiled source", action="store_true")
    parser.add_argument("file", nargs='+')
    args = parser.parse_args()

    cu = CompilationUnit()

    for file in args.file:
        cu.read_file(file)

    code = cu.render()

    if args.run:
        run(code)
        return

    if args.outfile == None:
        print(code)
    else:

        out_path = Path(args.outfile)
        if not out_path.parent.exists():
            raise FileNotFoundError(f"parent folder doesn't exist: {out_path.parent}")

        with open(args.outfile, 'w') as f:
            f.write(code)

if __name__ == '__main__':
    main()

