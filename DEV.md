# Documentation Development

Dorado-docs documentation is generated using [MkDocs](https://www.mkdocs.org/) which is configured
via the `mkdocs.yml` file. The core content is written in markdown (.md) source files linked in the `mkdocs.yml`.

## Building / Serving the Documentation

Create a python environment to build / serve the documentation using [MkDocs](https://www.mkdocs.org/).
All required dependencies such as mkdocs themes are contained within this project's `pyproject.toml` file. As such,
simply install the dorado-docs python project. The `[dev]` optional dependencies will download [pre-commit](https://pre-commit.com/).

```bash
python3.10 -m venv venv --prompt="dorado-docs"
source venv/bin/activate
pip install -U pip '.[dev]'
```

To serve the documentation for local development serve the documentation on localhost port 8000 (default).
If you see: `OSError: [Errno 48] Address already in use` try another port `e.g. 8080`.

```bash
mkdocs serve -a localhost:8000 --strict
```

In a web browser navigate to `http://localhost:8000/` to view the documentation which is updated live.

## Auto find internal links

When using Mkdocs, links to other target files in the docs must be relative to the source file.
This is fine until a file moves, at which point the links break and the docs won't build (in strict mode).

To avoid this we can use the [Mkdocs-Macros plugin](https://github.com/fralau/mkdocs-macros-plugin)
([docs](https://mkdocs-macros-plugin.readthedocs.io/en/latest/)) to write python functions which are
called during the build.

The `find(name)` function from [main.py](main.py) can be called in a markdown file and it's result
is substituted into the file content during the build and importantly **before** linking.

The `find` function `name` argument is a filename that must resolve uniquely in the `docs/`.
If the argument doesn't end in `.md` then a wildcard extension `*.md` is added automatically.

The relative path to the target from the source is returned making everything magically work.

This function is called within the jinja2 templating escape context `{{}}` for example: `{{find("name")}}`.
For some reason, it doesn't always work in the yaml header when assigning to a variable.

To debug this function set `plugins.macros.verbose` to `true` and the Mkdocs server output will show debugging
info such as:

```text
INFO    -  [macros - Page Finder] - find(downloader): glob='downloader*.md' relative_path='../models/downloader.md
```

## Dorado Syntax Highlighting

The `dorado_docs` repo implements an extension class for the default `bash` lexer from `Pygments`
which is used by `Mkdocs` for syntax highlighting. `dorado` and it's subcommands e.g. `basecaller` are all registered as types of keywords
in the bash lexer extension. These keywords have a custom colour configuration defined in the
`stylesheets/extra.css` file.

Importantly, the custom dorado lexer is registered with `Pygments` in the `pyproject.toml` as
an **plugin entry point**:

```toml
[project.entry-points."pygments.lexers"]
dorado = "dorado_docs:DoradoBashLexer"
```

We can check that it's installed by listing the `Pygments` lexers and checking for the `dorado` lexer.

```bash
pygmentize -L lexers | grep -A1 dorado
```
