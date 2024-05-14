"""collection of languages with their translation rules"""

import pathlib
import languages.default as default_lang
import languages.python as python_lang
import languages.html as html_lang

# TODO: use absolute paths so that this import can be done elsewhere

MODULES = [python_lang, html_lang]


def format_config(path: str) -> dict:
    """match the extension of a file and return the appropriate rules"""
    extension = pathlib.Path(path).suffix
    for language in MODULES:
        if language.rules["extension"] == extension:
            return language.rules
    return default_lang.rules


a = format_config(".../hell.py")
b = format_config("../hey/there/index.html")
c = format_config("this/it is/t.c")

...
