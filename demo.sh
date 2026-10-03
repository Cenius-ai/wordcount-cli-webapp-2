#!/usr/bin/env bash
# demo.sh — non-interactive, end-to-end demonstration of wordcount.py.
#
#   bash demo.sh
#
# It builds its sample inputs in a temporary directory, exercises every
# documented path of the CLI (counting, edge cases, bad paths, usage errors,
# help), checks each result against the contract, prints an aligned summary and
# exits 0 only when every case matched.  Nothing is downloaded and nothing
# outside the temporary directory is written.
set -u

cd "$(dirname "$0")" || exit 1

PYTHON="${PYTHON:-python3}"

if [ ! -f wordcount.py ]; then
    printf 'demo: wordcount.py is missing next to demo.sh\n' >&2
    exit 1
fi
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    printf 'demo: %s not found (set PYTHON=/path/to/python3)\n' "$PYTHON" >&2
    exit 1
fi

work="$(mktemp -d)" || exit 1
trap 'rm -rf "$work"' EXIT HUP INT TERM

: > "$work/empty.txt"
printf '   \t\n\n  \n' > "$work/blank.txt"
printf 'café déjà vu\n' > "$work/accents.txt"
printf 'The wordcounter splits on\nany   run of\twhitespace.\n' > "$work/runs.txt"

checks=0
failures=0

# record OUTCOME LABEL STATUS DETAIL -> one aligned row, printed immediately
record() {
    checks=$((checks + 1))
    printf '│ %-4s │ %-30s │ %-7s │ %s\n' "$1" "$2" "$3" "$4"
    if [ "$1" != "ok" ]; then
        failures=$((failures + 1))
    fi
}

# check_case LABEL EXPECTED_STATUS EXPECTED_TEXT -- COMMAND...
# Runs the command, then compares the exit status with EXPECTED_STATUS and
# looks for EXPECTED_TEXT in stdout or in the first stderr line.
check_case() {
    label="$1"; expected_status="$2"; expected_text="$3"; shift 3
    if [ "${1:-}" = "--" ]; then shift; fi

    stdout="$("$@" 2>"$work/stderr")"
    status=$?
    first_err="$(head -n 1 "$work/stderr")"

    shown="$stdout"
    if [ -z "$shown" ]; then shown="$first_err"; fi
    shown="$(printf '%s\n' "$shown" | head -n 1)"

    matched=no
    if [ "$status" = "$expected_status" ]; then
        if printf '%s\n%s\n' "$stdout" "$first_err" | grep -qF -- "$expected_text"; then
            matched=yes
        fi
    fi

    if [ "$matched" = "yes" ]; then
        record ok "$label" "exit $status" "$shown"
    else
        record FAIL "$label" "exit $status" \
            "expected exit $expected_status + \"$expected_text\"; got: $shown"
    fi
}

printf '\n'
printf '┌─ wordcount.py ─ demo ───────────────────────────────────────────────────────┐\n'
printf '│ a single-file, dependency-free word counter — python3 wordcount.py <file>   │\n'
printf '└─────────────────────────────────────────────────────────────────────────────┘\n\n'

rule='├──────┼────────────────────────────────┼─────────┼─────────────────────────────────────────────'
printf '│ %-4s │ %-30s │ %-7s │ %s\n' 'ok?' 'case' 'status' 'output'
printf '%s\n' "$rule"

printf '│                                                                              │\n'
printf '│ %-76s │\n' 'counting'
check_case 'bundled example'            0 'examples/sample.txt: 60 words' -- "$PYTHON" wordcount.py examples/sample.txt
check_case 'empty file -> 0 words'      0 '0 words'                      -- "$PYTHON" wordcount.py "$work/empty.txt"
check_case 'whitespace-only -> 0 words' 0 '0 words'                      -- "$PYTHON" wordcount.py "$work/blank.txt"
check_case 'runs of spaces and tabs'    0 'runs.txt: 8 words'            -- "$PYTHON" wordcount.py "$work/runs.txt"
check_case 'non-ASCII (UTF-8) file'     0 '3 words'                      -- "$PYTHON" wordcount.py "$work/accents.txt"
check_case 'path printed as given'      0 'examples/blank.txt: 0 words'  -- "$PYTHON" wordcount.py examples/blank.txt

printf '│                                                                              │\n'
printf '│ %-76s │\n' 'bad paths and usage errors'
check_case 'missing path'               1 'file not found:' -- "$PYTHON" wordcount.py "$work/gone.txt"
check_case 'directory argument'         1 'is a directory:' -- "$PYTHON" wordcount.py "$work"
check_case 'no argument -> usage'       2 'usage:'          -- "$PYTHON" wordcount.py
check_case 'unknown flag -> usage'      2 'usage:'          -- "$PYTHON" wordcount.py --lines

printf '│                                                                              │\n'
printf '│ %-76s │\n' 'self-documentation'
check_case '--help'                     0 'usage:'            -- "$PYTHON" wordcount.py --help
check_case '--version'                  0 'wordcount.py 1.0.0' -- "$PYTHON" wordcount.py --version

# Determinism: the same input must always produce the same line and exit code.
first="$("$PYTHON" wordcount.py examples/sample.txt)"
second="$("$PYTHON" wordcount.py examples/sample.txt)"
if [ "$first" = "$second" ]; then
    record ok 'same input twice' 'same' "$first"
else
    record FAIL 'same input twice' 'differs' "$first vs $second"
fi

# Scriptability: stdout carries only the result line, so it pipes cleanly.
piped="$("$PYTHON" wordcount.py examples/sample.txt | sed 's/^[^:]*: //')"
if [ "$piped" = '60 words' ]; then
    record ok 'stdout pipes cleanly' 'captured' "$piped"
else
    record FAIL 'stdout pipes cleanly' 'unexpected' "$piped"
fi

printf '\n'
if [ "$failures" -eq 0 ]; then
    printf 'demo complete — %d checks, 0 failures; every case matched the documented contract.\n' "$checks"
    exit 0
fi
printf 'demo failed — %d of %d checks did not match the documented contract.\n' "$failures" "$checks" >&2
exit 1
