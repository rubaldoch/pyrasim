from argparse import (
    ArgumentParser,
    Namespace,
    _HelpAction,
)
from typing import (
    Any,
    Callable,
    Dict,
    IO,
    List,
    Optional,
)

def add_input_args(parser: ArgumentParser):
    parser.add_argument(
        "--start-frequency",
        "-sf",
        metavar="FLOAT",
        type=float,
        dest="start_frequency",
        default=100,
        help="The starting frequency (MHz).",
    )
    parser.add_argument(
        "--end-frequency",
        "-ef",
        metavar="FLOAT",
        type=float,
        dest="end_frequency",
        default=250,
        help="The ending frequency (MHz).",
    )
    parser.add_argument(
        "--frequency-step",
        "-fs",
        metavar="FLOAT",
        type=float,
        dest="frequency_step",
        default=10,
        help="Frequency Step (MHz).",
    )

def add_output_args(
    parser: ArgumentParser,
    multiple_names: bool = False,
    ):
    parser.add_argument(
        "--output-to",
        "-ot",
        dest="output",
        action="store_true",
        help="Output to file(s) in the output directory in the output format. Otherwise the output is simply printed.",
    )
    parser.add_argument(
        "--output-format",
        "-of",
        metavar="STRING",
        dest="output_format",
        type=str,
        default="markdown",
        help="The output format to use: 'markdown'/'md', 'csv', 'json', or 'latex'/'tex'. Defaults to 'markdown'.",
    )
    parser.add_argument(
        "--output-name",
        "-on",
        nargs="+" if multiple_names else 1,
        metavar="STRING",
        dest="output_name",
        type=str,
        default=[""],
        help="The name of the output file. Defaults to the name of the input file.",
    )
    parser.add_argument(
        "--output-significant-digits",
        "-osd",
        metavar="INTEGER",
        dest="output_significant_digits",
        type=int,
        default=6,
        help="The number of significant digits in the output",
    )
    parser.add_argument(
        "--output-dir",
        "-od",
        metavar="STRING",
        dest="output_dir",
        type=str,
        default=".",
        help="The path to the output directory. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--suppress-progress",
        dest="suppress_progress",
        action="store_true",
        help="Suppress printing progress messages.",
    )

def parse_args(parser: ArgumentParser):
    add_input_args(parser)
    add_output_args(parser)

def parse_cli_args(parser: ArgumentParser, argv: List[str]) -> Namespace:
    args: Namespace = parser.parse_args(argv)
    return args

def get_argument_parser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser(
        prog="pyrasim",
        allow_abbrev=False,
        description="""
        pyRaSim Copyright (C) 2024 pyRaSim developers
        """.strip(),
    )
    subparsers = parser.add_subparsers(dest="command")
    parse_args(
        subparsers.add_parser(
            "sfcw",
            description="""
            Stepped Frequency Continuos Wave Radar.
            """.strip(),
        )
    )
    parser.add_argument(
        "--version",
        action="store_true",
        dest="version",
        help="Print the current version.",
    )
    return parser
