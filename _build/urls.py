"""URLs limpias: quita «.html» de los enlaces internos (GitHub Pages sirve /laboratorio → laboratorio.html).

    python3 _build/urls.py            # reescribe todas las páginas publicadas
    from urls import limpia           # lo usa generar_paginas.py antes de escribir
"""
import os
import re
import subprocess

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINAS = sorted({os.path.basename(f)[:-5] for f in subprocess.run(
    ["git", "ls-files", "*.html"], cwd=RAIZ, capture_output=True, text=True).stdout.split() if not f.startswith(("api/", "_build/"))}
    | {"index"}, key=len, reverse=True)

# prefijo opcional (dominio, ../, blog/, {pre}) + nombre de página + .html, seguido de fin de URL
RE = re.compile(r'(?<![\w./-])((?:https://www\.endurace-lab\.com/)?(?:\{pre\}|(?:\.\./)+)?(?:blog/)?)(' +
                "|".join(map(re.escape, PAGINAS)) + r')\.html(?=[#?"\'<)\s`,;]|$)')


def _sub(m):
    pre, nombre = m.group(1), m.group(2)
    if nombre == "index":
        return pre if pre.startswith("https://") else "/"
    return pre + nombre


def limpia(texto):
    return RE.sub(_sub, texto)


if __name__ == "__main__":
    archivos = subprocess.run(["git", "ls-files", "*.html", "*.js", "*.xml", "*.json", "*.webmanifest"],
                              cwd=RAIZ, capture_output=True, text=True).stdout.split()
    for f in archivos:
        if f.startswith(("api/", "_build/")) or f == "sw.js":
            continue
        p = os.path.join(RAIZ, f)
        antes = open(p, encoding="utf-8").read()
        despues = limpia(antes)
        if despues != antes:
            open(p, "w", encoding="utf-8").write(despues)
            print(f"{f}: {len(RE.findall(antes))} enlaces")
