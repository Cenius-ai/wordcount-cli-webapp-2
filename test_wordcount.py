"""Tests for wordcount.py.

Standard-library ``unittest`` only, so the suite runs with either of:

    python3 -m unittest test_wordcount.py
    pytest

No third-party dependency is imported and no network or fixture file outside
``examples/`` is touched.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import wordcount  # noqa: E402  (import after sys.path is fixed for direct runs)

SCRIPT = os.path.join(PROJECT_DIR, "wordcount.py")


def run_cli(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run the CLI as a real subprocess and capture stdout/stderr separately."""
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
        cwd=cwd or PROJECT_DIR,
    )


class CountWordsTests(unittest.TestCase):
    """The counting rule: a word is any run of whitespace."""

    def test_single_spaced_words(self) -> None:
        self.assertEqual(wordcount.count_words("hello world"), 2)

    def test_repeated_whitespace_does_not_inflate_the_count(self) -> None:
        self.assertEqual(wordcount.count_words("a\t b\n\nc   "), 3)

    def test_empty_text_counts_zero(self) -> None:
        self.assertEqual(wordcount.count_words(""), 0)

    def test_whitespace_only_text_counts_zero(self) -> None:
        self.assertEqual(wordcount.count_words("   \n\t\n"), 0)

    def test_non_ascii_words(self) -> None:
        self.assertEqual(wordcount.count_words("café déjà vu"), 3)

    def test_hyphenated_and_punctuated_tokens_count_once(self) -> None:
        self.assertEqual(wordcount.count_words("state-of-the-art tool, tested."), 3)

    def test_newlines_are_separators(self) -> None:
        self.assertEqual(wordcount.count_words("one\ntwo\nthree\n"), 3)


class CliSuccessTests(unittest.TestCase):
    """Happy path: one stdout line, exit 0, trailing newline."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmpdir = self._tmp.name

    def write(self, name: str, text: str) -> str:
        path = os.path.join(self.tmpdir, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_counts_a_file_and_exits_zero(self) -> None:
        path = self.write("sample.txt", "hello world")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, f"{path}: 2 words\n")
        self.assertEqual(result.stderr, "")

    def test_prints_the_path_exactly_as_given(self) -> None:
        self.write("sample.txt", "hello world")
        result = run_cli("sample.txt", cwd=self.tmpdir)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "sample.txt: 2 words\n")

    def test_output_line_ends_with_a_trailing_newline(self) -> None:
        path = self.write("sample.txt", "hello world")
        result = run_cli(path)
        self.assertTrue(result.stdout.endswith("\n"))
        self.assertEqual(len(result.stdout.splitlines()), 1)

    def test_whitespace_only_file_reports_zero(self) -> None:
        path = self.write("blank.txt", "   \n\t\n")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, f"{path}: 0 words\n")

    def test_empty_file_reports_zero(self) -> None:
        path = self.write("empty.txt", "")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, f"{path}: 0 words\n")

    def test_non_ascii_file_counts_correctly(self) -> None:
        path = self.write("accents.txt", "café déjà vu\n")
        result = run_cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, f"{path}: 3 words\n")

    def test_repeated_runs_are_deterministic(self) -> None:
        path = self.write("sample.txt", "alpha  beta\n\tgamma\n")
        first = run_cli(path)
        second = run_cli(path)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.returncode, second.returncode)

    def test_bundled_example_matches_its_documented_count(self) -> None:
        result = run_cli(os.path.join("examples", "sample.txt"), cwd=PROJECT_DIR)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "examples/sample.txt: 60 words\n")

    def test_help_exits_zero_and_names_the_positional_file_argument(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)
        self.assertIn("file", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_version_exits_zero(self) -> None:
        result = run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn(wordcount.__version__, result.stdout)


class CliBadPathTests(unittest.TestCase):
    """Failure paths: one stderr line, documented exit code, clean stdout."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmpdir = self._tmp.name

    def test_missing_argument_prints_usage_to_stderr_and_exits_two(self) -> None:
        result = run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("usage:", result.stderr)
        self.assertIn("file", result.stderr)

    def test_nonexistent_path_exits_one_with_file_not_found(self) -> None:
        result = run_cli("nope.txt", cwd=self.tmpdir)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "file not found: nope.txt\n")

    def test_directory_reports_a_directory_specific_message(self) -> None:
        result = run_cli(self.tmpdir)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"is a directory: {self.tmpdir}\n")
        self.assertNotIn("file not found", result.stderr)

    def test_directory_message_differs_from_the_not_found_message(self) -> None:
        directory = run_cli(self.tmpdir).stderr
        missing = run_cli(os.path.join(self.tmpdir, "gone.txt")).stderr
        self.assertNotEqual(directory, missing)
        self.assertTrue(directory.startswith("is a directory: "))
        self.assertTrue(missing.startswith("file not found: "))

    def test_unreadable_file_exits_one_without_a_traceback(self) -> None:
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("running as root: file permission bits are not enforced")
        path = os.path.join(self.tmpdir, "noperm.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("hello world\n")
        os.chmod(path, 0o000)
        self.addCleanup(os.chmod, path, 0o600)

        result = run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"file not found: {path}\n")
        self.assertNotIn("Traceback", result.stderr)

    def test_undecodable_file_exits_one_without_a_traceback(self) -> None:
        path = os.path.join(self.tmpdir, "binary.dat")
        with open(path, "wb") as handle:
            handle.write(b"\xff\xfe\x00\x01 not utf-8 \xff")
        result = run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"file not found: {path}\n")

    def test_error_text_never_reaches_stdout(self) -> None:
        for args in (("nope.txt",), (self.tmpdir,)):
            with self.subTest(args=args):
                result = run_cli(*args, cwd=self.tmpdir)
                self.assertEqual(result.stdout, "")
                self.assertNotEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
