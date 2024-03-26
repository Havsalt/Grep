__version__ = "0.2.3"

import argparse
import pathlib
import re
from typing import Generator
import color
from color import paint


NEWLINE = "\n"
DOT = "."


class ParserArgs(argparse.Namespace):
    path: str
    pattern: str
    depth: int | None
    include_dotfile: bool
    verbose: bool
    silent: bool
    flag: int


parser = argparse.ArgumentParser(
    prog="Grep",
    description="Know which file and where, that contains specified regular expression"
    )
parser.add_argument("pattern")
parser.add_argument("-v", "--version",
                    action="version",
                    version=f"%(prog)s: v{__version__}")
parser.add_argument("-p", "--path",
                    default=".",
                    help="Path to initial search location")
parser.add_argument("-r", "--depth",
                    dest="depth",
                    metavar="[depth]",
                    type=int,
                    default=1,
                    nargs="?",
                    help="Recurision depth. Defaults to 1")
parser.add_argument("-i", "--include-dotfile",
                    dest="include_dotfile",
                    action="store_true",
                    help="Recurision depth. Defaults to 1")
parser.add_argument("-f",
                    dest="flag",
                    metavar="[flag]",
                    action="store",
                    type=int,
                    default=0,
                    help="Compiler flag for regular expression")
group = parser.add_mutually_exclusive_group()
group.add_argument("--verbose",
                    action="store_true",
                    help="Display more information during execution")
group.add_argument("--silent",
                    action="store_true",
                    help="Display less information during execution")
args = ParserArgs()
parser.parse_args(namespace=args)

absolute_path = (pathlib.Path
                 .cwd()
                 .joinpath(args.path)
                 .resolve())

pattern = re.compile(args.pattern, flags=args.flag)


def process_file(file_path: pathlib.Path) -> None:
    try:
        content = pathlib.Path(file_path).read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        if args.verbose:
            print(paint("[Warning]", color.YELLOW),
                  paint("Skipping", color.AQUA),
                  paint(file_path, color.WHITE),
                  paint(f"\n[Reason]", color.YELLOW),
                  paint(error.__class__.__name__, color.BOLD + color.AQUA) + paint(":", color.WHITE),
                  paint(error, color.RED))
        return
    printed_file = False
    for lino, line in enumerate(content.split(NEWLINE)):
        if (matches := pattern.findall(line)):
            if not printed_file:
                printed_file = True
                if not args.silent:
                    print()
                    print(paint("Pattern:", color.WHITE),
                        paint(args.pattern, color.RED))
                print(paint("[Match]", color.LIME), paint(file_path, color.WHITE))
            if args.silent:
                continue
            for match in matches:
                highlight_styling = color.BOLD + color.BLUE
                print(f"  {paint(lino, color.RED)}{paint(')', color.WHITE)} " + line.replace(match, paint(match, highlight_styling)))
                print(f"  {' ' * len(str(lino))}{paint(':', color.WHITE)}", paint(match, color.CORAL))


def walk_paths(start: pathlib.Path, depth: int | None = None) -> Generator[pathlib.Path, None, None]:
    if depth is not None:
        if depth <= 0:
            return
        depth -= 1
    for sub_path in start.iterdir():
        if sub_path.name.startswith(DOT):
            if not args.include_dotfile:
                continue
        if sub_path.is_file():
            # try: # check if can be opened using utf-8 decoding
            #     fd = open(sub_path, "r", encoding="utf-8")
            # except UnicodeDecodeError:
            #     print("FAILED")
            #     continue
            # finally:
            #     fd.close()
            yield sub_path
        else:
            yield from walk_paths(sub_path, depth=depth)


assert absolute_path.exists()

if absolute_path.is_file():
    process_file(absolute_path)
else:
    for sub_path in walk_paths(absolute_path, depth=args.depth):
        if sub_path.is_file():
            process_file(sub_path)
