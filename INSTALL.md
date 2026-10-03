# Installing wordcount

`wordcount.py` is a single standard-library file: there is no build, no
database, no migration, no seed step and no environment file. The steps below
are ordered; a stranger can follow them top to bottom on a clean checkout.

## Prerequisites (installed by *you*, not by the setup script)

| Requirement | Why | Notes |
| ----------- | --- | ----- |
| Python 3.8+ | runs the tool | `python3 --version`. Uses only `argparse`, `os`, `sys`. |
| `pip` | installs the declared test runner | `python3 -m pip --version` (bundled with CPython). |
| A POSIX shell (`bash` or `sh`) | runs `install.sh` and `demo.sh` | any Linux/macOS shell |

No system packages are needed or installed: the setup script never calls `sudo`,
`apt`, `dnf`, `apk` or `brew`. Package manager: **pip** (the only one this
project uses).

## 1. Install the project dependencies

```console
bash install.sh
```

What it does, in order, then exits without starting any long-running process:

1. verifies a Python 3.8+ interpreter is on `PATH`;
2. refreshes `pip`/`setuptools`/`wheel` and installs `requirements.txt`
   (pytest, the test runner — the CLI itself has no third-party dependencies);
3. self-checks: imports `wordcount`, counts `examples/sample.txt` and runs the
   test suite, so a broken environment fails loudly here rather than silently
   later.

The script is idempotent — re-running it is safe — and exits non-zero if a
genuinely required dependency cannot be installed.

## 2. Verify the install

```console
python3 wordcount.py examples/sample.txt
```

Expected output (exit code 0):

```
examples/sample.txt: 60 words
```

A full non-interactive pass over every success, edge-case, bad-path and
usage-error path:

```console
bash demo.sh
```

## 3. No database, migration or seed step

This tool keeps no state: it opens one file read-only, prints the count and
exits. There is no schema to create, no demo data to seed and no `.env` to copy
(`.env.example` is intentionally absent because the code reads no environment
variables). If you skipped step 1 entirely, `python3 wordcount.py <file>` still
works: the runtime needs nothing but the interpreter.

## 4. Run it

```console
python3 wordcount.py <file>          # relative or absolute path, any cwd
python3 wordcount.py --help          # usage, positional argument, exit codes
python3 wordcount.py --version       # version string, exits 0
```

Exit codes: `0` counted, `1` bad path (missing, unreadable, undecodable or a
directory), `2` usage error. See [README.md](README.md) for the full contract
and [USAGE.md](USAGE.md) for walkthroughs.

## 5. Run the tests

```console
python3 -m unittest test_wordcount.py
```

or, if you prefer pytest (installed in step 1):

```console
python3 -m pytest
```

The suite runs offline, needs no fixtures outside `test_wordcount.py` and
`examples/`, and skips only the unreadable-file case when executed as `root`
(where permission bits are not enforced).

## Uninstalling

Delete the checkout. Nothing was installed outside it except the pip packages
listed in `requirements.txt`.
