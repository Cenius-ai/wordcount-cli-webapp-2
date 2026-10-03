# Using wordcount

Every walkthrough below is a real invocation of the shipped CLI — copy and
paste them from the project root.

## 1. Count the words in a file

```console
$ python3 wordcount.py examples/sample.txt
examples/sample.txt: 60 words
$ echo $?
0
```

The path is echoed exactly as you typed it, so relative and absolute arguments
both read naturally:

```console
$ python3 wordcount.py examples/accents.txt
examples/accents.txt: 3 words
```

## 2. Whitespace, empty files and non-ASCII text

A word is any run of whitespace: spaces, tabs, blank lines and trailing
newlines collapse, and they never inflate the total.

```console
$ printf 'a\t b\n\nc   \n' > /tmp/runs.txt
$ python3 wordcount.py /tmp/runs.txt
/tmp/runs.txt: 3 words

$ printf '   \n\t\n' > /tmp/blank.txt      # whitespace only
$ python3 wordcount.py /tmp/blank.txt
/tmp/blank.txt: 0 words                    # zero is a result, not an error

$ : > /tmp/empty.txt                       # completely empty
$ python3 wordcount.py /tmp/empty.txt
/tmp/empty.txt: 0 words

$ python3 wordcount.py examples/accents.txt
examples/accents.txt: 3 words              # café déjà vu — read as UTF-8
```

## 3. Use the count in a script

stdout carries the result line and nothing else, so it pipes cleanly; errors go
to stderr, so a pipeline never swallows a failure message into the data.

```console
$ python3 wordcount.py examples/sample.txt | sed 's/^[^:]*: //'
60 words

$ count=$(python3 wordcount.py examples/sample.txt | sed 's/^[^:]*: //; s/ words$//')
$ echo "the file has $count words"
the file has 60 words
```

Branch on the exit code instead of parsing text:

```sh
#!/bin/sh
# reject a document that grew past a word budget
words=$(python3 wordcount.py README.md 2>/dev/null | sed 's/^[^:]*: //; s/ words$//')
if [ -z "$words" ]; then
    echo "could not count README.md (run: python3 wordcount.py README.md)" >&2
    exit 1
fi
if [ "$words" -gt 500 ]; then
    echo "README.md is $words words, over the 500-word budget" >&2
    exit 1
fi
echo "README.md is $words words"
```

## 4. Handle the failure paths

Each bad invocation prints exactly one line on stderr and exits `1`; nothing is
written to stdout, so `$(...)` captures stay empty.

```console
$ python3 wordcount.py nope.txt
file not found: nope.txt                   # exit 1

$ python3 wordcount.py examples
is a directory: examples                   # exit 1, distinct from "not found"

$ touch /tmp/noperm.txt && chmod 000 /tmp/noperm.txt     # as a non-root user
$ python3 wordcount.py /tmp/noperm.txt
file not found: /tmp/noperm.txt            # exit 1, no traceback

$ printf '\377\376\000\001 not \377' > /tmp/binary.dat   # invalid UTF-8
$ python3 wordcount.py /tmp/binary.dat
file not found: /tmp/binary.dat            # exit 1, no traceback
```

## 5. Usage errors and self-documentation

```console
$ python3 wordcount.py
usage: wordcount.py [-h] [--version] file
wordcount.py: error: the following arguments are required: file
# exit 2 — argparse usage on stderr, naming the positional file argument

$ python3 wordcount.py examples/sample.txt extra.txt
usage: wordcount.py [-h] [--version] file
wordcount.py: error: unrecognized arguments: extra.txt
# exit 2 — this tool counts exactly one file

$ python3 wordcount.py --help       # full usage, argument list, exit codes; exit 0
$ python3 wordcount.py --version    # wordcount.py 1.0.0; exit 0
```

## 6. See everything at once

```console
$ bash demo.sh
```

`demo.sh` runs fourteen checks — the counting cases, the bad-path cases, the
usage errors, `--help`, `--version`, determinism and clean piping — prints them
as one aligned table in box-drawing rules and exits `0` only when every case
matched the documented contract.

## Exit-code reference

| Code | Meaning |
| ---- | ------- |
| `0` | the file was counted; one result line on stdout |
| `1` | bad path: missing, unreadable, not valid UTF-8, or a directory |
| `2` | usage error: no `file` argument, unknown flag, extra argument |
