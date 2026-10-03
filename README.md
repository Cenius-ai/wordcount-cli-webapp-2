# wordcount-cli — complete Full-stack app command-line tool example app

A Full-stack app command-line tool, open-source and ready to self-host: that's **wordcount-cli**. A single-file plain-Python command-line tool that counts the words in a text file and prints the total. wordcount-cli ships complete — source, design assets, seed data — under the Apache-2.0 license; no cloud account needed. [Remix wordcount-cli on cenius.ai](https://cenius.ai/marketplace/p/wordcount-cli-2?ref=gh&utm_campaign=wordcount-cli-webapp-2) for a custom build.


[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) ![Stack](https://img.shields.io/badge/Stack-Full--stack%20app-3b82f6) [![Built with cenius.ai](https://img.shields.io/badge/Built%20with-cenius.ai-8b5cf6)](https://cenius.ai)

[![Open in cenius.ai](https://img.shields.io/badge/▶%20Open%20%26%20edit%20in-cenius.ai-8b5cf6?style=for-the-badge)](https://cenius.ai/marketplace/p/wordcount-cli-2?ref=gh&utm_campaign=wordcount-cli-webapp-2)

> **▶ [Open & edit in cenius.ai](https://cenius.ai/marketplace/p/wordcount-cli-2?ref=gh&utm_campaign=wordcount-cli-webapp-2)** — one click to an editable workspace: describe changes in plain English, get an instant preview, one-click deploy and host. Modifications made on the platform come with full rebrand & relicense rights.

_Local clone? See [Quick start](#quick-start) below. cenius.ai is the zero-setup path._

## Demo

![wordcount-cli demo — command-line tool built with Full-stack app](.github/media/hero.gif)

▶ **[Full demo walkthrough](https://cenius.ai/marketplace/p/wordcount-cli-2?ref=gh&utm_campaign=wordcount-cli-webapp-2)** — watch it on the project page · [download MP4](.github/media/demo.mp4)

## Quick start

```bash
./install.sh   # installs dependencies + seeds demo data
```

See [`INSTALL.md`](INSTALL.md) for full setup and usage instructions.

## Features

- Count words in a file
- Command-line entry point
- Input validation and errors

## Architecture

Folder layout: `examples/`. `./install.sh` gets you from a fresh clone to a running instance with sample data in a single step. Built in Full-stack app (22 files). Step-by-step setup guide: [`INSTALL.md`](INSTALL.md).

## Usage guide

Every walkthrough below is a real invocation of the shipped CLI — copy and
paste them from the project root.

### 1. Count the words in a file

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

### 2. Whitespace, empty files and non-ASCII text

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

### 3. Use the count in a script

stdout carries the result line and nothing else, so it pipes cleanly; errors go
to stderr, so a pipeline never swallows a failure message into the data.

```console
$ python3 wordcount.py examples/sample.txt | sed 's/^[^:]*: //'
60 words

$ count=$(python3 wordcount.py examples/sample.txt | sed 's/^[^:]*: //; s/ words$//')
$ echo "the file has $count words"
the file has 60 words
```

_Full guide: [`USAGE.md`](USAGE.md)_

## FAQ

### What does it take to self-host wordcount-cli?

Pull the repo, run `./install.sh`, and you are up — the script installs packages and pre-seeds the database. [`INSTALL.md`](INSTALL.md) covers any platform-specific tweaks.

### Can I change wordcount-cli without writing code?

The easiest route: [visit the project on cenius.ai](https://cenius.ai/marketplace/p/wordcount-cli-2?ref=gh&utm_campaign=wordcount-cli-webapp-2), tell the platform what to change, and collect the updated build. No source-editing needed.

### Is wordcount-cli free for commercial use?

Yes — it ships under the Apache-2.0 license, which permits commercial use, modification and redistribution. The full text is in [LICENSE](LICENSE).

### Can I remove the wordcount-cli name and use my own?

Absolutely. [Open it on cenius.ai](https://cenius.ai/marketplace/p/wordcount-cli-2?ref=gh&utm_campaign=wordcount-cli-webapp-2) and remix it there — platform modifications come with full rebrand and relicense rights over your derivative, so the result is entirely yours.

### How is wordcount-cli built technically?

Full-stack app. The full source in this repository is exactly what the app runs. Highlights include command-line entry point.

## License & rebranding

Released under the [Apache License 2.0](LICENSE) (© 2026 Cenius AI) — free for personal and commercial use. The Cenius name/logo are trademarks (see NOTICE).

**Need a customized version?** [Remix this app on cenius.ai](https://cenius.ai/marketplace/p/wordcount-cli-2?ref=gh&utm_campaign=wordcount-cli-webapp-2) — modifications made on the platform come with **full rebrand & relicense rights** over your derivative.

## Built with cenius.ai

This entire application — code, design, seeded demo data — was generated on **[cenius.ai](https://cenius.ai)** from a plain-English description.

- 🚀 [Build your own app on cenius.ai](https://cenius.ai)
- 🎛️ [Remix wordcount-cli on the marketplace](https://cenius.ai/marketplace/p/wordcount-cli-2?ref=gh&utm_campaign=wordcount-cli-webapp-2) — open it in a workspace, prompt for changes, and ship your own version.

More open-source apps: [the Cenius-ai catalog](https://github.com/Cenius-ai) · [showcase index](https://github.com/Cenius-ai/showcase)
