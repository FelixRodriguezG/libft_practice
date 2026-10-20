#!/usr/bin/env python3
"""Pinta en la terminal el markdown que le llega por la entrada estándar.

Lo usa libft_43.sh para las notas (tip, casos, nota…) si está instalado
rich (pip install --user rich); si no, el script les da formato él mismo.
Lo propio de Obsidian (callouts, [[enlaces]]) ya llega convertido.

Ancho: MANWIDTH (lo pone el menú) o el de la terminal. Solo usa los 8
colores básicos, que son los que entiende el panel de salida del menú.
"""

import os
import re
import sys

from rich.console import Console
from rich.markdown import BlockQuote, CodeBlock, Heading, Markdown
from rich.padding import Padding
from rich.segment import Segment
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text
from rich.theme import Theme

THEME = Theme({
    "markdown.h1": "bold cyan",
    "markdown.h2": "bold cyan",
    "markdown.h3": "bold",
    "markdown.h4": "bold",
    "markdown.code": "yellow",
    "markdown.block_quote": "none",
    "markdown.link": "blue",
    "markdown.item.bullet": "cyan",
    "markdown.item.number": "cyan",
    "markdown.hr": "dim",
})


# Espacios (y colores que solo pintan espacios) al final de la línea.
TRAILING = re.compile(r"(?:\s|\033\[[\d;]*m)+$")


class LeftHeading(Heading):
    """Títulos a la izquierda; los de sección, como «── Prototipo»."""

    def __rich_console__(self, console, options):
        text = self.text.copy()
        if self.tag == "h2":
            text = Text("── ", "bold cyan") + text
        text.justify = "left"
        yield text


class BarQuote(BlockQuote):
    """Cita con la barra azul y el texto en el color normal."""

    def __rich_console__(self, console, options):
        bar = Segment("│ ", Style(color="blue"))
        inner = options.update(width=options.max_width - 2)
        for i, element in enumerate(self.elements):
            if i:       # una línea en blanco entre párrafos, como en la nota
                yield from (bar, Segment("\n"))
            for line in console.render_lines(element, inner):
                yield bar
                yield from line
                yield Segment("\n")


class IndentedCode(CodeBlock):
    """Bloques de código sangrados, sin fondo; sin lenguaje, en cian."""

    def __rich_console__(self, console, options):
        code = str(self.text).rstrip()
        if self.lexer_name == "text":
            body = Text(code, "cyan")
        else:
            body = Syntax(code, self.lexer_name, theme="ansi_dark",
                          background_color="default", word_wrap=True)
        yield Padding(body, (0, 0, 0, 4))


class NoteMarkdown(Markdown):
    elements = {**Markdown.elements, "heading_open": LeftHeading,
                "blockquote_open": BarQuote, "fence": IndentedCode,
                "code_block": IndentedCode}


def main():
    width = os.environ.get("MANWIDTH", "")
    console = Console(theme=THEME, force_terminal=True,
                      color_system="standard",
                      width=int(width) if width.isdigit() else None)
    with console.capture() as out:
        console.print(NoteMarkdown(sys.stdin.read()))
    # rich rellena cada línea con espacios hasta el ancho: fuera. Y nunca
    # dos líneas en blanco seguidas.
    blank = True
    for line in out.get().splitlines():
        line = TRAILING.sub("\033[0m", line) if "\033" in line \
            else line.rstrip()
        if line in ("", "\033[0m"):
            if blank:
                continue
            line, blank = "", True
        else:
            blank = False
        print(line)


if __name__ == "__main__":
    main()
