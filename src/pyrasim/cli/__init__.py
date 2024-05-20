from argparse import (
    ArgumentParser,
    Namespace,
)
import sys
from traceback import format_exc
from typing import (
    Callable,
    Dict,
)

from .config import (
    get_argument_parser,
    parse_cli_args,
)

def main():
    parser: ArgumentParser = get_argument_parser()
    args: Namespace = parse_cli_args(parser, sys.argv[1:])
    if args.version:
        from pyrasim.version import PACKAGE_VERSION
        print(PACKAGE_VERSION)
        return
    # if args.command in commands:
    #     if hasattr(args, "suppress_progress") and args.suppress_progress is False:
    #         from .utility import register_progress
    #         register_progress()
    #     try:
    #         commands[args.command](parser, args)
    #     except KeyboardInterrupt:
    #         return
    #     except Exception:
    #         print(format_exc())
    else:
        parser.print_help()
