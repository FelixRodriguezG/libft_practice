#!/usr/bin/env python3
"""Copia las notas de la libft de una bóveda de Obsidian a notas/.

Copia la carpeta libft/ de la bóveda y las notas de conceptos a las que
enlaza (Punteros en C, La Norma…), con la misma estructura de carpetas.
Los enlaces a notas que no se copian se convierten en texto normal, para
que no queden enlaces rotos, y las rutas personales del tipo
/home/<usuario>/… se quitan.

Uso: python3 scripts/exportar_notas.py ~/Documents/Barcelona42 [destino]
     (destino por defecto: notas/, junto al script libft_43.sh)
"""

import os
import re
import shutil
import sys

# Notas enlazadas que no tienen que ver con la libft.
EXCLUDE = {"Inicio", "get_next_line - Índice"}

LINK = re.compile(r"(!?)\[\[([^\]|#]*)(#[^\]|]*)?(?:\|([^\]]*))?\]\]")
HOME_PATH = re.compile(r"/home/[^/\s`]+/(?:[^\s`]*/)?")


def find_notes(vault):
    """{nombre: ruta relativa} de todas las notas de la bóveda."""
    notes = {}
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(root, f), vault)
                notes.setdefault(f[:-3], rel)
    return notes


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    vault = os.path.expanduser(sys.argv[1])
    here = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "notas")

    notes = find_notes(vault)
    chosen = {n: p for n, p in notes.items()
              if p.startswith("libft" + os.sep)}
    linked = set()
    for rel in chosen.values():
        with open(os.path.join(vault, rel), encoding="utf-8") as f:
            linked |= {m.group(2) for m in LINK.finditer(f.read())}
    for name in sorted(linked - EXCLUDE - set(chosen)):
        if name in notes:
            chosen[name] = notes[name]

    def relink(m):
        bang, target, heading, alias = m.groups()
        if not target or target in chosen:
            return m.group(0)
        return alias or target

    if os.path.isdir(dest):
        shutil.rmtree(dest)
    for rel in sorted(chosen.values()):
        with open(os.path.join(vault, rel), encoding="utf-8") as f:
            text = f.read()
        text = HOME_PATH.sub("", LINK.sub(relink, text))
        out = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(rel)
    print(f"{len(chosen)} notas copiadas en {dest}")


if __name__ == "__main__":
    main()
