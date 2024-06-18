__version__ = "0.3.1"

import argparse
import pathlib
import re
from typing import Generator

import colex
from actus import info, warn, LogSection


NEWLINE = "\n"
DOT = "."

match_log = LogSection("Match")


class ParserArguments(argparse.Namespace):
    path: str
    pattern: str
    depth: int | None
    include_dotfile: bool
    verbose: bool
    silent: bool
    flag: int


parser = argparse.ArgumentParser(
    prog="grep",
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
args = ParserArguments()
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
            warn(f"Skipping $['{file_path}']")
            info(f"Caused by {error.__class__.__name__}$[:] {error}")
        return
    printed_file = False
    for lino, line in enumerate(content.split(NEWLINE)):
        if (matches := pattern.findall(line)):
            if not printed_file:
                printed_file = True
                if not args.silent:
                    print()
                    print(colex.colorize("Pattern:", colex.WHITE),
                          colex.colorize(args.pattern, colex.RED))
                match_log(f'$["{file_path}"]')
            if args.silent:
                continue
            with match_log:
                for match in matches:
                    highlight_styling = colex.BOLD + colex.BLUE
                    number = colex.colorize(str(lino), colex.RED)
                    replaced = line.replace(match, colex.colorize(match, highlight_styling))
                    match_log(f"{number}$[)] {replaced}")
                    margin = ' ' * len(str(lino))
                    matched = colex.colorize(match, colex.CORAL)
                    match_log(f"{margin}$[:]", matched)


def walk_paths(
    start: pathlib.Path,
    depth: int | None = None
) -> Generator[pathlib.Path, None, None]:
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
