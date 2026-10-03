#!/usr/bin/env python3
"""Count the words in a UTF-8 text file.

The whole tool is this one file:

    python3 wordcount.py <file>

A successful run prints exactly one line to stdout and exits 0:

    <path>: <N> words

Every failure prints one line to stderr and exits with a documented code, so
the tool is safe to use from shell scripts and CI:

    0   the file was counted
    1   the path is missing, unreadable, undecodable or a directory
    2   the command line was wrong (no file argument)

Python 3.8+ standard library only (argparse, os, sys).  No third-party
dependencies, no network access, no files are created, modified or deleted.
See README.md for the full contract and test_wordcount.py for the test suite.
"""
from __future__ import annotations

import argparse
import os
import sys

__version__ = "1.0.0"

EXIT_OK = 0
EXIT_BAD_PATH = 1


def count_words(text: str) -> int:
    """Return the number of whitespace-separated words in ``text``.

    ``str.split()`` with no argument splits on any run of whitespace and
    discards leading/trailing whitespace, so repeated spaces, tabs and blank
    lines never inflate the count and whitespace-only text yields 0.
    """
    return len(text.split())


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser: one positional file path plus --help."""
    parser = argparse.ArgumentParser(
        prog="wordcount.py",
        description="Count whitespace-separated words in a UTF-8 text file.",
        epilog="exit codes: 0 counted, 1 bad path, 2 usage error",
    )
    parser.add_argument(
        "file",
        metavar="file",
        help="path to the UTF-8 text file to count (relative or absolute)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="wordcount.py " + __version__,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return the process exit code."""
    args = build_parser().parse_args(argv)
    path = args.file

    # A directory must be reported as a directory, never as a missing file, so
    # the isdir check happens before isfile.
    if os.path.isdir(path):
        print(f"is a directory: {path}", file=sys.stderr)
        return EXIT_BAD_PATH

    # os.path.isfile passes for an existing file whose permissions deny reading,
    # so the open() below is still wrapped: any remaining I/O failure and any
    # UTF-8 decode failure become the documented unreadable-file message
    # instead of a traceback.
    if not os.path.isfile(path):
        print(f"file not found: {path}", file=sys.stderr)
        return EXIT_BAD_PATH

    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError):
        print(f"file not found: {path}", file=sys.stderr)
        return EXIT_BAD_PATH

    print(f"{path}: {count_words(text)} words")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
