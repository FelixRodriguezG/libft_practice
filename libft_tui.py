#!/usr/bin/env python3
"""Menú interactivo (TUI) para libft_43.sh.

Se queda abierto mientras trabajas: muestra tus ft_*.c, la ficha de la
función seleccionada y la salida de los comandos, y desde aquí sugieres,
creas y testeas funciones sin volver a lanzar el script.

Todas las acciones están en App.actions(): de ahí salen la barra de teclas,
el menú de acciones (espacio), la ayuda (?) y las teclas rápidas.

Uso: ./libft_43.sh menu (con vim al lado) o ./libft_43.sh tui (solo el menú)
"""

import curses
import locale
import os
import re
import signal
import subprocess
import threading
import time
import unicodedata
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT = os.path.join(SCRIPT_DIR, "libft_43.sh")
HISTORY = os.path.join(SCRIPT_DIR, ".libft_historial")
ATTEMPTS = os.path.join(SCRIPT_DIR, ".libft_intentos")
LAST = os.path.join(SCRIPT_DIR, ".libft_ultima")
REQUESTS = os.path.join(SCRIPT_DIR, ".libft_peticiones")

# Panel de tmux con vim, si el menú se abrió con ./libft_43.sh menu.
VIM_PANE = os.environ.get("LIBFT_VIM_PANE")

MAX_LINES = 5000        # líneas de salida que se guardan
POLL_EVERY = 0.5        # segundos entre comprobaciones de archivos
SAVE_SETTLE = 0.6       # espera tras guardar antes del auto-test

ANSI_SGR = re.compile(r"\x1b\[([0-9;]*)m")
ANSI_OTHER = re.compile(r"\x1b\[[0-9;?]*[A-Za-ln-z]")
# Secuencias OSC (título, enlaces…) y demás caracteres de control: la salida
# de los comandos se muestra como texto, nunca se pasa a la terminal.
ANSI_OSC = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)?")
CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")

# Con NO_COLOR (https://no-color.org) no se usan colores; la negrita, el
# vídeo inverso y los símbolos siguen marcando estado y selección.
USE_COLOR = not os.environ.get("NO_COLOR")
HIST_LINE = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d)\s+([✔✘])\s+(\S+)\s+(.*)$")

# Peticiones que puede hacer vim (F5, F6, F7).
VIM_REQUESTS = ("test", "tip", "man")

# Por debajo de este ancho, todo va en una columna.
STACK_BELOW = 100

# Órdenes cuya salida se lee desde el principio, no desde el final.
PINNED = ("tip", "nota", "casos", "progreso", "intentos", "man",
          "preparado")

# Colores de cada fila del «43», como el degradado del logo de 42.
LOGO_COLORS = (6, 6, 4, 4, 5, 5, 5)

# Colores: 1 rojo, 2 verde, 3 amarillo, 4 azul, 5 magenta, 6 cian, 7 blanco.
RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN = 1, 2, 3, 4, 5, 6

STATE_TEXT = {"✔": "dominada", "⟳": "toca repasar",
              "✘": "falló el último test", "·": "sin hacer"}
READY_TEXT = {"lista": ("✔ lista", GREEN), "pendiente": ("· pendiente", 0),
              "falla": ("✘ falla", RED), "caducada": ("⌛ caducada", YELLOW)}

ENTER_KEYS = (10, 13, curses.KEY_ENTER)


def parse_ansi(line):
    """Convierte una línea con colores ANSI en [(texto, color, negrita)]."""
    line = line.rstrip("\r\n").split("\r")[-1].replace("\t", "    ")
    line = ANSI_OTHER.sub("", ANSI_OSC.sub("", line))
    segs, color, bold, pos = [], 0, False, 0
    for m in ANSI_SGR.finditer(line):
        if m.start() > pos:
            segs.append((CONTROL.sub("", line[pos:m.start()]), color, bold))
        for code in (m.group(1) or "0").split(";"):
            n = int(code) if code.isdigit() else 0
            if n == 0:
                color, bold = 0, False
            elif n == 1:
                bold = True
            elif 31 <= n <= 37 or 91 <= n <= 97:
                color = n % 10
            elif n == 39:
                color = 0
        pos = m.end()
    if pos < len(line):
        segs.append((CONTROL.sub("", line[pos:]), color, bold))
    return segs


def char_width(ch):
    if unicodedata.combining(ch) or ch in "\ufe0f\u200d":
        return 0
    return 2 if unicodedata.east_asian_width(ch) in "WF" else 1


def text_width(text):
    return sum(char_width(ch) for ch in text)


def clip(text, width):
    """Corta text para que ocupe como mucho width columnas."""
    out, used = "", 0
    for ch in text:
        w = char_width(ch)
        if used + w > width:
            break
        out += ch
        used += w
    return out


def wrap(segs, width):
    """Parte una línea de segmentos en filas de width columnas."""
    rows, row, used = [], [], 0
    for text, color, bold in segs:
        buf = ""
        for ch in text:
            w = char_width(ch)
            if used + w > width:
                if buf:
                    row.append((buf, color, bold))
                    buf = ""
                rows.append(row)
                row, used = [], 0
            buf += ch
            used += w
        if buf:
            row.append((buf, color, bold))
    rows.append(row)
    return rows


def wrap_text(text, width):
    """Parte un texto plano en líneas de width columnas, por palabras."""
    lines, line = [], ""
    for word in text.split():
        if line and text_width(line) + 1 + text_width(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    return lines + [line] if line else lines


def short_result(mark, text):
    """Resumen corto de un resultado del historial para la lista."""
    if mark == "✔":
        m = re.search(r"tiempo (\S+)", text)
        return "todo OK" + (f" · {m.group(1).rstrip(',')}" if m else "")
    bad = [p.strip() for p in text.split(",")
           if re.search(r"KO|no compila|SIGSEGV|valgrind|no existe|sin test", p)
           and not p.strip().startswith("0 KO")]
    return " · ".join(bad) or text


def load_logo():
    """El dibujo del «43» de la cabecera (HEADER_ART del script)."""
    try:
        with open(SCRIPT, encoding="utf-8") as f:
            text = f.read()
        block = re.search(r"^HEADER_ART=\((.*?)^\)", text, re.S | re.M)
        return [line.rstrip() for line in
                re.findall(r'"([^"]*)"', block.group(1))]
    except (OSError, AttributeError):
        return []


def load_attempts():
    """Intentos en marcha: {nombre: (inicio, pistas, examen)}."""
    attempts = {}
    try:
        with open(ATTEMPTS, encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                if len(parts) == 4:
                    attempts[parts[0]] = (int(parts[1]), parts[2] == "1",
                                          parts[3] == "1")
    except (OSError, ValueError):
        pass
    return attempts


def fmt_time(secs):
    return f"{secs // 60}m{secs % 60:02d}s"


def notify(text):
    """Aviso en el escritorio, si hay notify-send."""
    try:
        subprocess.Popen(["notify-send", "-a", "libft", "libft · 43", text],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


def load_history():
    """Último resultado de cada función: {nombre: (fecha, marca, texto)}."""
    hist = {}
    try:
        with open(HISTORY, encoding="utf-8") as f:
            for line in f:
                m = HIST_LINE.match(line.rstrip("\n"))
                if m:
                    hist[m.group(3)] = (m.group(1), m.group(2), m.group(4))
    except OSError:
        pass
    return hist


class App:
    def __init__(self, scr):
        self.scr = scr
        self.cwd = os.getcwd()
        self.files = []             # nombres sin .c
        self.mtimes = {}
        self.changed = {}           # nombre -> momento en que cambió
        self.tested_at = {}         # nombre -> mtime al lanzar su test
        self.hist = {}
        self.attempts = {}
        self.data = {}              # nombre -> datos del script (ver load_stats)
        self.funcs = []             # (parte, nombre, veces, estado), en orden
        self.states = {}            # estado → nº de funciones (progreso)
        self.ready = (0, 0)         # funciones clave listas / total
        self.out_width = 80
        self.stats_dirty = True
        self.logo = load_logo()
        self.last_tip = None        # para pasar del tip al pseudocódigo
        self.sel_name = None
        self.last_poll = 0
        self.first_scan = True

        self.output = []            # líneas ya parseadas
        self.scroll = 0             # filas desde el final (0 = seguir)
        self.pin_line = None        # línea que se mantiene arriba (notas)
        self.lock = threading.Lock()

        self.proc = None
        self.job_title = ""
        self.job_done = None
        self.queue = []
        self.auto = False
        self.status = ""

        # Ventanas emergentes: None, "acciones", "ayuda", "buscador" o
        # "confirmar".
        self.mode = None
        self.confirm = None         # (pregunta, acción)
        self.filter = ""
        self.pick = 0               # fila elegida en el buscador / acciones
        self.help_scroll = 0

    # ---------- archivos e historial ----------

    def poll_files(self):
        now = time.time()
        if now - self.last_poll < POLL_EVERY:
            return
        self.last_poll = now
        mtimes = {}
        for entry in os.scandir(self.cwd):
            if entry.name.startswith("ft_") and entry.name.endswith(".c"):
                try:
                    mtimes[entry.name[:-2]] = entry.stat().st_mtime
                except OSError:
                    pass
        for name, mtime in mtimes.items():
            old = self.mtimes.get(name)
            if old is None and not self.first_scan:
                self.sel_name = name    # archivo nuevo: seleccionarlo
            elif old is not None and mtime != old:
                self.changed[name] = now
        self.mtimes = mtimes
        self.files = sorted(mtimes)
        self.first_scan = False
        self.hist = load_history()
        self.attempts = load_attempts()
        self.read_requests()
        if self.stats_dirty:
            self.load_stats()
        if self.sel_name not in mtimes:
            self.sel_name = self.files[0] if self.files else None

        for name, when in list(self.changed.items()):
            if now - when < SAVE_SETTLE:
                continue
            del self.changed[name]
            if self.auto and name in mtimes:
                self.enqueue(["test", name], f"auto-test {name}", test=name)

    def read_requests(self):
        """Peticiones de vim (F5 test, F6 tip, F7 man)."""
        try:
            tmp = REQUESTS + ".leyendo"
            os.replace(REQUESTS, tmp)
            with open(tmp, encoding="utf-8") as f:
                lines = f.read().splitlines()
            os.remove(tmp)
        except OSError:
            return
        for line in lines:
            parts = line.split()
            if len(parts) != 2 or parts[0] not in VIM_REQUESTS:
                continue
            cmd, name = parts
            if cmd == "test":
                # F5 guarda y pide el test: no hace falta además el auto-test.
                self.changed.pop(name, None)
                self.test(name)
            elif cmd == "tip":
                self.show_tip(name)
            else:
                self.enqueue(["man", name], f"man {name}")

    def load_stats(self):
        """Datos de las 43 funciones (orden datos del script)."""
        out = subprocess.run(["bash", SCRIPT, "datos"], cwd=self.cwd,
                             capture_output=True, text=True).stdout
        self.data, self.funcs, self.states = {}, [], {}
        ready = total = 0
        for line in out.splitlines():
            parts = line.split("\t")
            if len(parts) != 8:
                continue
            part, name, count, state, prep, best, cat, proto = parts
            self.data[name] = {"part": part, "count": count, "state": state,
                               "ready": prep, "best": int(best), "cat": cat,
                               "proto": proto}
            self.funcs.append((part, name, count, state))
            self.states[state] = self.states.get(state, 0) + 1
            if prep != "-":
                total += 1
                ready += prep == "lista"
        self.ready = (ready, total)
        self.stats_dirty = False

    def exam(self):
        """(nombre, inicio) del examen en marcha, o None."""
        for name, (start, _, exam) in self.attempts.items():
            if exam:
                return name, start
        return None

    def is_stale(self, name):
        """True si el archivo ha cambiado desde su último test."""
        mtime = self.mtimes.get(name, 0)
        if name in self.tested_at:
            return mtime > self.tested_at[name]
        if name not in self.hist:
            return False
        tested = datetime.strptime(self.hist[name][0], "%Y-%m-%d %H:%M")
        return mtime >= tested.timestamp() + 60

    # ---------- trabajos (llamadas al script) ----------

    def add_line(self, segs):
        with self.lock:
            # Si estás leyendo más arriba, lo nuevo no te mueve el texto:
            # se suma a las líneas pendientes (↓ N más).
            if self.scroll and self.pin_line is None:
                self.scroll += len(wrap(segs, max(1, self.out_width - 1)))
            self.output.append(segs)
            if len(self.output) > MAX_LINES:
                del self.output[:len(self.output) - MAX_LINES]

    def enqueue(self, args, title, test=None):
        if any(q[1] == title for q in self.queue) or \
                (self.proc and self.job_title == title):
            return
        self.queue.append((args, title, test))
        self.start_next()

    def start_next(self):
        if self.proc or not self.queue:
            return
        args, title, test = self.queue.pop(0)
        tests = [test] if test else (self.files if args == ["test"] else [])
        for name in tests:
            self.tested_at[name] = self.mtimes.get(name, 0)
        stamp = datetime.now().strftime("%H:%M:%S")
        self.add_line([])
        self.add_line([(f"── {title} · {stamp} ", CYAN, True)])
        self.scroll = 0
        self.pin_line = len(self.output) - 1 if args[:1] and args[0] in PINNED \
            else None
        self.job_title = title
        self.job_done = None
        self.status = f"⏳ {title}…"
        # El man se formatea al ancho del panel de salida.
        env = dict(os.environ, MANWIDTH=str(max(40, self.out_width - 1)))
        self.proc = subprocess.Popen(
            ["bash", SCRIPT, *args], cwd=self.cwd, env=env,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, start_new_session=True)
        threading.Thread(target=self.read_job, args=(self.proc,),
                         daemon=True).start()

    def read_job(self, proc):
        for raw in proc.stdout:
            self.add_line(parse_ansi(raw.decode("utf-8", "replace")))
        self.job_done = proc.wait()

    def check_job(self):
        if self.proc is None or self.job_done is None:
            return
        code = self.job_done
        self.proc = None
        if code < 0:
            self.status = f"⛔ {self.job_title}: parado"
        elif self.job_title.startswith(("test", "auto-test")):
            self.status = (f"✔ {self.job_title}: todo OK" if code == 0
                           else f"✘ {self.job_title}: hay fallos (míralos abajo)")
            if self.job_title.startswith("auto"):
                notify(self.status)
                if code != 0:
                    curses.beep()
        else:
            self.status = f"{self.job_title}: hecho"
            # Archivo recién creado: abrirlo en vim para empezar.
            if code == 0 and self.job_title.startswith(
                    ("sugerir", "nueva", "examen")):
                try:
                    with open(LAST, encoding="utf-8") as f:
                        self.open_in_vim(f.read().strip(), reload=True)
                except OSError:
                    pass
        self.last_poll = 0
        self.stats_dirty = True
        self.start_next()

    def stop_job(self):
        self.queue.clear()
        if self.proc:
            try:
                os.killpg(self.proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    # ---------- acciones ----------

    def test(self, name):
        self.enqueue(["test", name], f"test {name}", test=name)

    def show_tip(self, name):
        """Tip de name; si es el mismo que el anterior, el pseudocódigo."""
        if name and self.last_tip == name:
            self.enqueue(["tip", name, "2"], f"pseudocódigo {name}")
            self.last_tip = None
            return
        self.last_tip = name
        self.enqueue(["tip", name] if name else ["tip"],
                     f"tip {name or 'última sugerida'}")

    def run_on(self, cmd, name, title=None):
        """Orden del script sobre una función (sin nombre: la última)."""
        self.last_tip = None
        self.enqueue([cmd, name] if name else [cmd],
                     title or f"{cmd} {name or 'última sugerida'}")

    def open_in_vim(self, name, reload=False):
        """Abre name.c en el panel de vim y le pasa el foco. Con reload,
        descarta lo que hubiera en vim (archivo recién creado)."""
        if not VIM_PANE or not name:
            return
        path = os.path.join(self.cwd, name + ".c").replace(" ", "\\ ")
        cmd = f":hide edit{'!' if reload else ''} {path}"
        try:
            for keys in (["Escape"], ["-l", cmd], ["Enter"]):
                subprocess.run(["tmux", "send-keys", "-t", VIM_PANE, *keys],
                               check=True, capture_output=True)
            subprocess.run(["tmux", "select-pane", "-t", VIM_PANE],
                           capture_output=True)
        except (OSError, subprocess.CalledProcessError):
            self.status = "✘ No encuentro el panel de vim (¿lo has cerrado?)"

    def toggle_auto(self):
        self.auto = not self.auto
        self.status = ("Auto-test activado: cada vez que guardes un ft_*.c se "
                       "testea solo." if self.auto else "Auto-test desactivado.")

    def stop(self):
        self.stop_job()
        self.status = "⛔ Parando…"

    def clear_output(self):
        with self.lock:
            self.output.clear()
        self.scroll = 0
        self.pin_line = None

    def surrender(self):
        exam = self.exam()
        self.ask(f"¿Rendirte en el examen de {exam[0]}?",
                 lambda: self.enqueue(["rendirse"], "rendirse") or True)

    def reset_counter(self):
        self.ask("¿Poner a cero el contador de sugerencias?",
                 lambda: self.enqueue(["reset"], "reset") or True)

    def quit(self):
        if self.proc:
            self.ask("Hay un trabajo en marcha. ¿Salir?",
                     lambda: self.stop_job() or False)
            return True
        return False

    def actions(self):
        """Todas las acciones disponibles ahora mismo, por grupos:
        (grupo, tecla, nombre, explicación, función). La función devuelve
        False para salir del menú."""
        sel = self.sel_name
        exam = self.exam()
        acts = []

        def add(group, key, label, desc, fn, ok=True):
            if ok:
                acts.append((group, key, label, desc, fn))

        g = "Practicar"
        add(g, "r", "Sugerir una función",
            "Te toca una función según tu historial: salen más las que "
            "fallas o no has hecho, y vuelven las que toca repasar. Se abre "
            "en vim y empieza el cronómetro.",
            lambda: self.enqueue([], "sugerir"))
        for part, what in (("1", "libc"), ("2", "adicionales"),
                           ("3", "listas")):
            add(g, part, f"Sugerir de la Parte {part} ({what})",
                f"Como sugerir, pero solo con funciones de la Parte {part}.",
                lambda p=part: self.enqueue([p], f"sugerir (parte {p})"))
        add(g, "n", "Elegir una función…",
            "Buscador con las 43: escribe para filtrar, ⏎ crea el archivo y "
            "Tab muestra su pista sin crearlo.", self.open_picker)
        if exam:
            add(g, "E", f"Rendirse en el examen ({exam[0]})",
                "Vuelven las pistas. El tiempo sigue contando y el intento "
                "contará como resuelto con pistas.", self.surrender)
        else:
            add(g, "E", "Empezar un examen",
                "Una función clave al azar, sin pistas hasta que pase el "
                "test. El man sí está permitido.",
                lambda: self.enqueue(["examen"], "examen"))

        g = f"Con {sel}" if sel else "Con la función"
        if VIM_PANE:
            add(g, "⏎", "Abrir en vim",
                "Abre el archivo en el panel de vim y te lleva allí.",
                lambda: self.open_in_vim(sel), ok=sel)
        add(g, "t", "Testear",
            "Norminette, libftTester con valgrind y las reglas del subject. "
            "En vim: F5.", lambda: self.test(sel), ok=sel)
        add(g, "m", "Man / subject",
            "La página de man de la función original, o su ficha del "
            "subject en las Partes 2 y 3. Permitido en examen. En vim: F7.",
            lambda: self.run_on("man", sel), ok=sel)
        add(g, "i", "Pseudocódigo" if sel and self.last_tip == sel
            else "Pista",
            "Puntos clave de tus notas de Obsidian; pulsa otra vez para ver "
            "el pseudocódigo. Cuenta como pista. En vim: F6.",
            lambda: self.show_tip(sel), ok=sel)
        add(g, "e", "Casos límite",
            "Happy path y edge cases que debes probar, de tu nota de casos "
            "límite. Cuenta como pista.",
            lambda: self.run_on("casos", sel), ok=sel)
        add(g, "o", "Nota completa", "Toda su nota de Obsidian. Cuenta como "
            "pista.", lambda: self.run_on("nota", sel), ok=sel)
        add(g, "O", "Abrir la nota en Obsidian", "Cuenta como pista.",
            lambda: self.run_on("obsidian", sel), ok=sel)
        add(g, "h", "Historial", "Todos sus resultados anteriores.",
            lambda: self.run_on("historial", sel), ok=sel)
        add(g, "v", "Versiones guardadas",
            "Tus intentos anteriores, guardados en intentos/.",
            lambda: self.run_on("intentos", sel, f"versiones {sel}"), ok=sel)

        g = "Probar"
        add(g, "T", "Testear todas", "Todos los ft_*.c de la carpeta.",
            lambda: self.enqueue(["test"], "test todos"), ok=self.files)
        add(g, "a", "Desactivar el auto-test" if self.auto
            else "Activar el auto-test",
            "Cada vez que guardas un ft_*.c se testea solo y te avisa en el "
            "escritorio.", self.toggle_auto)
        add(g, "s", "Parar el test", "Para lo que esté en marcha.",
            self.stop, ok=self.proc or self.queue)

        g = "Ver"
        add(g, "P", "¿Preparado para el examen?",
            "Las 21 funciones clave: cuáles tienes listas (resueltas sin "
            "pistas en los últimos 14 días) y cuáles te faltan.",
            lambda: self.enqueue(["preparado"], "preparado"))
        add(g, "p", "Progreso de las 43",
            "Estado, días resueltas, mejor tiempo y cuándo toca repasar.",
            lambda: self.enqueue(["progreso"], "progreso"))
        add(g, "H", "Historial completo", "Todos los tests que has hecho.",
            lambda: self.enqueue(["historial"], "historial"))

        g = "Menú"
        add(g, "c", "Limpiar la salida", "", self.clear_output)
        add(g, "x", "Reiniciar el contador de sugerencias",
            "No borra el historial.", self.reset_counter)
        add(g, "?", "Ayuda", "Teclas y símbolos.", self.open_help)
        add(g, "q", "Salir", "", self.quit)
        return acts

    def footer_keys(self):
        """Las pocas teclas que más se usan ahora mismo."""
        short = {"r": "sugerir", "n": "elegir", "E": "examen", "t": "test",
                 "i": "pista", "m": "man", "s": "parar",
                 "⏎": "abrir en vim"}
        if not self.sel_name:
            keys = ["r", "n", "E"]
        elif self.exam():
            keys = ["⏎", "t", "m", "E"]
            short["E"] = "rendirse"
        else:
            keys = ["⏎", "t", "i", "m", "r"]
        if self.proc:
            keys.insert(0, "s")
        available = {a[1] for a in self.actions()}
        items = [(k, short[k]) for k in keys if k in available]
        return items + [("espacio", "acciones"), ("?", "ayuda")]

    # ---------- dibujo ----------

    def put(self, y, x, text, attr=0, width=None):
        h, w = self.scr.getmaxyx()
        if y < 0 or y >= h or x >= w:
            return
        width = w - x if width is None else min(width, w - x)
        try:
            self.scr.addstr(y, x, clip(text, width), attr)
        except curses.error:
            pass    # escribir en la última celda da error, pero se pinta

    def attr(self, color, bold=False):
        a = curses.color_pair(color) if color and USE_COLOR else 0
        return a | (curses.A_BOLD if bold else 0)

    def rule(self, y, x, width, title="", extra=""):
        """Línea separadora con título: ── título ───── extra"""
        self.put(y, x, "─" * width, self.attr(BLUE))
        if title:
            self.put(y, x + 1, f" {title} ", self.attr(CYAN, True), width - 2)
        if extra:
            self.put(y, x + width - text_width(extra) - 2, f" {extra}",
                     self.attr(YELLOW, True))

    def draw(self):
        self.scr.erase()
        h, w = self.scr.getmaxyx()
        if h < 12 or w < 30:
            self.put(0, 0, "Ventana demasiado pequeña · q: salir")
            self.scr.noutrefresh()
            curses.doupdate()
            return

        self.draw_title(w)
        body_top, body_h = 1, h - 3
        if w < STACK_BELOW:
            # Estrecho (por ejemplo, al lado de vim): todo en una columna.
            files_h = min(max(len(self.files), 1) + 1, max(3, body_h // 4))
            self.draw_files(body_top, 0, w, files_h)
            y = body_top + files_h
            y += self.draw_card(y, 0, w)
            self.draw_output(y, 0, body_h - (y - body_top), w)
        else:
            left_w = min(46, max(30, w // 3))
            for y in range(body_top, body_top + body_h):
                self.put(y, left_w, "│", self.attr(BLUE))
            top = body_top
            if self.logo and body_h >= 20:
                top = self.draw_logo(top, left_w)
            self.draw_files(top, 0, left_w, body_h - (top - body_top))
            x, width = left_w + 2, w - left_w - 2
            y = body_top + self.draw_card(body_top, x, width)
            self.draw_output(y, x, body_h - (y - body_top), width)

        self.draw_status(h - 2, w)
        self.draw_footer(h - 1, w)

        # Primero la pantalla y encima la ventana emergente, si la hay.
        self.scr.noutrefresh()
        if self.mode == "buscador":
            self.draw_picker()
        elif self.mode == "acciones":
            self.draw_actions()
        elif self.mode == "ayuda":
            self.draw_help()
        elif self.mode == "confirmar":
            self.draw_confirm()
        curses.doupdate()

    def draw_title(self, w):
        """Barra de título con el estilo de la cabecera de 42: /* … */"""
        bar = curses.A_REVERSE
        self.put(0, 0, " " * w, bar)
        self.put(0, 0, " /* libft · 43 */", bar | curses.A_BOLD)
        parts = []
        exam = self.exam()
        if exam:
            parts.append((f" 📝 EXAMEN {exam[0]} "
                          f"{fmt_time(int(time.time()) - exam[1])} ",
                          self.attr(RED, True) | bar))
        ready, total = self.ready
        if total:
            done = ready == total
            parts.append((" 🎯 ¡preparado! " if done
                          else f" 🎯 examen {ready}/{total} ",
                          bar | self.attr(GREEN if done else 0, done)))
        if self.auto:
            parts.append((" auto-test ", self.attr(GREEN, True) | bar))
        if self.queue:
            parts.append((f" cola: {len(self.queue)} ", bar))
        x = w
        for text, attr in reversed(parts):
            x -= text_width(text)
            if x < 18:
                break
            self.put(0, x, text, attr)

    def draw_logo(self, top, width):
        """El «43» con el estilo del logo de 42 y tu progreso al lado.
        Devuelve la primera fila libre debajo."""
        logo_w = max(text_width(line) for line in self.logo)
        for i, line in enumerate(self.logo):
            color = LOGO_COLORS[i] if i < len(LOGO_COLORS) else CYAN
            self.put(top + i, 1, line,
                     self.attr(color, i == len(self.logo) - 1), width - 2)
        x = logo_w + 3
        if width - x >= 12:
            s = self.states
            side = [(1, "libft · 43", self.attr(CYAN, True)),
                    (3, f"✔ {s.get('✔', 0):<3}dominadas", self.attr(GREEN)),
                    (4, f"⟳ {s.get('⟳', 0):<3}repasar", self.attr(YELLOW)),
                    (5, f"✘ {s.get('✘', 0):<3}con fallos", self.attr(RED)),
                    (6, f"· {s.get('·', 0):<3}sin hacer", curses.A_DIM)]
            for row, text, attr in side:
                self.put(top + row, x, text, attr, width - x - 1)
        return top + len(self.logo) + 1

    def draw_files(self, top, left, width, height):
        self.rule(top, left, width, f"Tus archivos ({len(self.files)})")
        if not self.files:
            self.put(top + 1, left + 1, "Ninguno todavía: pulsa r.",
                     curses.A_DIM, width - 2)
            return
        rows = height - 1
        name_w = max(len(n) for n in self.files)
        idx = self.files.index(self.sel_name) if self.sel_name else 0
        start = max(0, min(idx - rows // 2, len(self.files) - rows))
        for i, name in enumerate(self.files[start:start + rows]):
            y = top + 1 + i
            sel = name == self.sel_name
            base = curses.A_REVERSE if sel else 0
            self.put(y, left, " " * width, base)
            self.put(y, left, "▸" if sel else " ", base | curses.A_BOLD)
            info = self.hist.get(name)
            if info:
                mark = info[1]
                mark_attr = self.attr(GREEN if mark == "✔" else RED, True)
            else:
                mark, mark_attr = "·", curses.A_DIM
            self.put(y, left + 2, mark, base | mark_attr)
            self.put(y, left + 4, name, base | curses.A_BOLD, width - 4)
            x = left + 4 + name_w + 1
            if self.is_stale(name):
                self.put(y, x, "●", base | self.attr(YELLOW, True))
            x += 2
            attempt = self.attempts.get(name)
            if attempt:
                # Intento en marcha: cronómetro en vez del último resultado.
                start_t, hints, exam = attempt
                clock = ("📝 " if exam else "⏱ ") + \
                    fmt_time(int(time.time()) - start_t)
                self.put(y, x, clock, base | self.attr(
                    RED if exam else YELLOW, True), left + width - x)
                continue
            detail = short_result(info[1], info[2]) if info else "sin testear"
            self.put(y, x, detail, base | curses.A_DIM, left + width - x)

    def draw_card(self, top, left, width):
        """Ficha de la función seleccionada. Devuelve las filas usadas."""
        name = self.sel_name
        if not name:
            return 0
        d = self.data.get(name, {})
        extra = f"Parte {d['part']}" if d else ""
        self.rule(top, left, width, name, extra)
        y = top + 1
        if d.get("proto"):
            for line in wrap_text(d["proto"], width - 2)[:2]:
                self.put(y, left + 1, line, self.attr(YELLOW), width - 2)
                y += 1

        # Qué está pasando ahora: intento en marcha o último resultado.
        attempt = self.attempts.get(name)
        info = self.hist.get(name)
        if attempt:
            start, hints, exam = attempt
            text = (f"{'📝 examen' if exam else '⏱ en marcha'}: "
                    f"{fmt_time(int(time.time()) - start)} · "
                    f"{'con pistas' if hints else 'sin pistas'}")
            if exam:
                text += " (man sí)"
            self.put(y, left + 1, text,
                     self.attr(RED if exam else YELLOW, True), width - 2)
        elif info:
            self.put(y, left + 1, f"{info[1]} {info[2]}",
                     self.attr(GREEN if info[1] == "✔" else RED), width - 2)
        else:
            self.put(y, left + 1, "Sin testear", curses.A_DIM, width - 2)
        y += 1

        # Estado para el examen y para el repaso.
        if d:
            x = left + 1
            if d["ready"] != "-":
                label, color = READY_TEXT.get(d["ready"], (d["ready"], 0))
                text = f"★ {d['cat']}: {label}"
                self.put(y, x, text, self.attr(color or MAGENTA, True),
                         width - 2)
                x += text_width(text) + 3
            rest = STATE_TEXT.get(d["state"], "")
            if d["best"] >= 0:
                rest += f" · mejor {fmt_time(d['best'])}"
            self.put(y, x, rest, curses.A_DIM, left + width - x - 1)
            y += 1
        return y - top

    def draw_output(self, top, left, height, width):
        self.out_width = width
        with self.lock:
            lines = list(self.output)
        title = "Salida"
        if self.proc:
            spin = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[int(time.time() * 8) % 10]
            title = f"Salida {spin} {self.job_title}"
        more = ""
        if self.scroll:
            more = f"↓ {self.scroll} más (Fin)"
        self.rule(top, left, width, title, more)
        if not lines:
            self.draw_welcome(top + 1, left, width)
            return

        # Solo se envuelven las líneas necesarias, empezando por el final.
        rows_h = height - 1
        if self.pin_line is not None:
            pinned = sum(len(wrap(segs, width - 1))
                         for segs in lines[self.pin_line:])
            self.scroll = max(0, pinned - rows_h)
        rows_needed = rows_h + self.scroll
        rows = []
        for segs in reversed(lines):
            rows[:0] = wrap(segs, width - 1)
            if len(rows) >= rows_needed:
                break
        max_scroll = max(0, len(rows) - rows_h)
        if self.scroll > max_scroll and len(rows) < rows_needed:
            self.scroll = max_scroll
        end = len(rows) - self.scroll
        visible = rows[max(0, end - rows_h):end]
        for i, row in enumerate(visible):
            x = left + 1
            for text, color, bold in row:
                self.put(top + 1 + i, x, text, self.attr(color, bold))
                x += text_width(text)

    def draw_welcome(self, top, left, width):
        """Primeros pasos, mientras la salida está vacía. Los textos se
        parten por palabras si el panel es estrecho."""
        if VIM_PANE:
            steps = [("r", "te toca una función y se crea su archivo"),
                     ("", "escríbela en vim (a la izquierda)"),
                     ("F5", "guarda y testea (o t aquí)")]
        else:
            steps = [("r", "te toca una función y se crea su archivo"),
                     ("", "escríbela en tu editor"),
                     ("t", "testea (a: auto-test al guardar)")]
        blocks = [("Cómo se practica", steps),
                  ("¿Atascado?", [("m", "man"), ("i", "pista"),
                                  ("e", "casos límite")]),
                  ("¿Listo para el examen?", [("E", "examen sin pistas"),
                                              ("P", "ver qué te falta")])]
        y = top + 1
        text_w = width - 10
        for title, items in blocks:
            self.put(y, left + 2, title, self.attr(CYAN, True), width - 3)
            y += 1
            for key, text in items:
                self.put(y, left + 4, key, self.attr(YELLOW, True))
                for line in wrap_text(text, text_w):
                    self.put(y, left + 9, line, 0, text_w)
                    y += 1
            y += 1
        for line in wrap_text("espacio: todas las acciones · ?: ayuda",
                              width - 3):
            self.put(y, left + 2, line, curses.A_DIM, width - 3)
            y += 1

    def draw_status(self, y, w):
        if not self.status:
            return
        attr = 0
        if self.status.startswith("✔"):
            attr = self.attr(GREEN, True)
        elif self.status.startswith(("✘", "⛔")):
            attr = self.attr(RED, True)
        elif self.status.startswith("⏳"):
            attr = self.attr(YELLOW, True)
        self.put(y, 0, " " + self.status, attr, w - 1)

    def draw_footer(self, y, w):
        """Teclas útiles ahora: la tecla resaltada y su nombre."""
        bar = curses.A_REVERSE
        self.put(y, 0, " " * w, bar)
        items = self.footer_keys()

        def fits():
            return sum(text_width(f" {k} {l} ") + 1 for k, l in items) <= w - 1

        # Si no caben: primero «espacio más», luego se quitan teclas por el
        # medio. Espacio y ? siempre quedan.
        if not fits():
            items[-2] = ("espacio", "más")
        while len(items) > 2 and not fits():
            items.pop(-3)
        x = 1
        for key, label in items:
            self.put(y, x, f" {key} ", self.attr(CYAN, True) | bar)
            x += text_width(key) + 2
            self.put(y, x, f"{label} ", bar)
            x += text_width(label) + 2

    def popup(self, height, width, title):
        h, w = self.scr.getmaxyx()
        height, width = min(height, h - 2), min(width, w - 2)
        y, x = (h - height) // 2, (w - width) // 2
        win = curses.newwin(height, width, y, x)
        win.erase()
        win.attron(self.attr(BLUE))
        win.box()
        win.attroff(self.attr(BLUE))
        self.win_put(win, 0, 2, f" {title} ", self.attr(CYAN, True), width - 4)
        return win, height, width

    def win_put(self, win, y, x, text, attr=0, width=None):
        h, w = win.getmaxyx()
        if y < 0 or y >= h or x >= w:
            return
        width = w - x - 1 if width is None else min(width, w - x - 1)
        try:
            win.addstr(y, x, clip(text, width), attr)
        except curses.error:
            pass

    def draw_actions(self):
        """Menú de acciones (espacio), por grupos y con explicación."""
        acts = self.actions()
        rows, group = [], None
        for i, (g, key, label, desc, fn) in enumerate(acts):
            if g != group:
                rows.append(("grupo", g))
                group = g
            rows.append(("acción", i))
        self.pick = max(0, min(self.pick, len(acts) - 1))
        win, height, width = self.popup(
            len(rows) + 5, 60, "Acciones · ⏎ hacer · Esc cerrar")
        list_h = height - 5
        sel_row = next(r for r, (kind, v) in enumerate(rows)
                       if kind == "acción" and v == self.pick)
        start = max(0, min(sel_row - list_h // 2, len(rows) - list_h))
        for i, (kind, value) in enumerate(rows[start:start + list_h]):
            y = 1 + i
            if kind == "grupo":
                self.win_put(win, y, 2, value, self.attr(CYAN, True))
                continue
            _, key, label, _, _ = acts[value]
            sel = value == self.pick
            base = curses.A_REVERSE if sel else 0
            self.win_put(win, y, 1, " " * (width - 2), base)
            self.win_put(win, y, 3, f"{key:>3}", base | self.attr(YELLOW, True))
            self.win_put(win, y, 8, label, base)
        # Explicación de la acción elegida.
        desc = acts[self.pick][3] if acts else ""
        self.win_put(win, height - 4, 1, "─" * (width - 2), self.attr(BLUE))
        for i, line in enumerate(wrap_text(desc, width - 4)[:2]):
            self.win_put(win, height - 3 + i, 2, line, curses.A_DIM)
        win.noutrefresh()

    def help_lines(self):
        """Contenido de la ayuda (?)."""
        lines = []
        group = None
        for g, key, label, _, _ in self.actions():
            if g != group:
                lines += [("", 0), (g, CYAN)]
                group = g
            lines.append((f"  {key:>3}  {label}", 0))
        lines += [("", 0), ("Moverse", CYAN),
                  ("  ↑↓ jk  elegir archivo", 0),
                  ("  RePág AvPág Inicio Fin  desplazar la salida", 0),
                  ("  espacio  menú de acciones", 0)]
        if VIM_PANE:
            lines += [("", 0), ("En vim", CYAN),
                      ("  F5 guardar y testear · F6 pista · F7 man", 0),
                      ("  Ctrl-b + flecha (o clic): cambiar de panel", 0),
                      ("  Mayús + arrastrar: seleccionar y copiar texto", 0)]
        lines += [("", 0), ("Símbolos", CYAN),
                  ("  ✔ último test perfecto · ✘ con fallos · · sin testear", 0),
                  ("  ● cambiado desde el último test", 0),
                  ("  ⏱ intento en marcha · 📝 examen", 0),
                  ("  ★ función clave para el examen · 🎯 cuántas tienes listas", 0),
                  ("", 0), ("Más detalles: ./libft_43.sh help", 0)]
        return lines[1:]

    def draw_help(self):
        lines = self.help_lines()
        win, height, width = self.popup(
            len(lines) + 2, 66, "Ayuda · ↑↓ desplazar · Esc cerrar")
        rows = height - 2
        self.help_scroll = max(0, min(self.help_scroll, len(lines) - rows))
        for i, (text, color) in enumerate(
                lines[self.help_scroll:self.help_scroll + rows]):
            self.win_put(win, 1 + i, 2, text,
                         self.attr(color, True) if color else 0)
        win.noutrefresh()

    def draw_picker(self):
        funcs = self.filtered()
        win, height, width = self.popup(
            len(self.funcs) + 4, 62,
            "Elegir función · ⏎ crear · Tab pista · Esc cerrar")
        self.win_put(win, 1, 2, f"buscar: ft_{self.filter}▏",
                     self.attr(YELLOW, True))
        rows = height - 3
        self.pick = max(0, min(self.pick, len(funcs) - 1))
        start = max(0, min(self.pick - rows // 2, len(funcs) - rows))
        for i, (part, name, count, state) in enumerate(
                funcs[start:start + rows]):
            sel = start + i == self.pick
            d = self.data.get(name, {})
            tags = []
            if d.get("ready", "-") != "-":
                tags.append("★ clave")
            if name in self.mtimes:
                tags.append("ya existe")
            line = f" {state} P{part}  {name:<18}{' · '.join(tags)}"
            base = curses.A_REVERSE if sel else 0
            self.win_put(win, 2 + i, 1, line.ljust(width - 2), base)
        win.noutrefresh()

    def draw_confirm(self):
        question = self.confirm[0]
        win, _, width = self.popup(5, text_width(question) + 6, "Confirmar")
        self.win_put(win, 2, 3, question, curses.A_BOLD)
        win.noutrefresh()

    # ---------- ventanas emergentes ----------

    def filtered(self):
        return [f for f in self.funcs if self.filter in f[1][3:]]

    def open_picker(self):
        self.load_stats()
        self.filter, self.pick = "", 0
        self.mode = "buscador"

    def open_help(self):
        self.help_scroll = 0
        self.mode = "ayuda"

    def key_picker(self, key):
        funcs = self.filtered()
        if key == 27:
            self.mode = None
        elif key == curses.KEY_UP:
            self.pick -= 1
        elif key == curses.KEY_DOWN:
            self.pick += 1
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            self.filter = self.filter[:-1]
            self.pick = 0
        elif key in ENTER_KEYS or key == 9:
            if funcs:
                name = funcs[self.pick][1]
                self.mode = None
                if key == 9:
                    self.enqueue(["tip", name], f"tip {name}")
                else:
                    self.enqueue(["new", name], f"nueva {name}")
        elif 32 < key < 127:
            self.filter += chr(key)
            self.pick = 0

    def key_actions(self, key):
        acts = self.actions()
        if key in (27, ord(" ")):
            self.mode = None
        elif key in (curses.KEY_UP, ord("k")):
            self.pick = max(0, self.pick - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            self.pick = min(len(acts) - 1, self.pick + 1)
        elif key in ENTER_KEYS:
            self.mode = None
            return acts[self.pick][4]() is not False
        else:
            # La tecla rápida también vale desde aquí.
            for _, k, _, _, fn in acts:
                if k == self.key_name(key) and k != "⏎":
                    self.mode = None
                    return fn() is not False
        return True

    def key_help(self, key):
        if key in (27, ord("?"), ord("q")):
            self.mode = None
        elif key in (curses.KEY_UP, ord("k")):
            self.help_scroll -= 1
        elif key in (curses.KEY_DOWN, ord("j")):
            self.help_scroll += 1
        elif key == curses.KEY_PPAGE:
            self.help_scroll -= 10
        elif key == curses.KEY_NPAGE:
            self.help_scroll += 10
        self.help_scroll = max(0, self.help_scroll)

    def ask(self, question, action):
        self.confirm = (question + "  (s/n)", action)
        self.mode = "confirmar"

    def key_confirm(self, key):
        if key in (ord("s"), ord("S"), ord("y"), ord("Y")):
            self.mode = None
            return self.confirm[1]() is not False
        if key in (ord("n"), ord("N"), 27):
            self.mode = None
        return True

    # ---------- teclas ----------

    @staticmethod
    def key_name(key):
        if key in ENTER_KEYS:
            return "⏎"
        return chr(key) if 0 <= key < 256 else ""

    def move_sel(self, delta):
        if not self.files:
            return
        idx = self.files.index(self.sel_name) if self.sel_name else 0
        self.sel_name = self.files[max(0, min(idx + delta,
                                              len(self.files) - 1))]

    def handle_key(self, key):
        """Devuelve False para salir."""
        modes = {"buscador": self.key_picker, "acciones": self.key_actions,
                 "ayuda": self.key_help, "confirmar": self.key_confirm}
        if self.mode in modes:
            return modes[self.mode](key) is not False

        h, _ = self.scr.getmaxyx()
        page = max(1, h - 8)
        name = self.key_name(key)
        if key in (curses.KEY_UP,) or name == "k":
            self.move_sel(-1)
        elif key in (curses.KEY_DOWN,) or name == "j":
            self.move_sel(1)
        elif key in (curses.KEY_PPAGE, curses.KEY_NPAGE, curses.KEY_HOME,
                     curses.KEY_END):
            self.pin_line = None
            if key == curses.KEY_PPAGE:
                self.scroll += page
            elif key == curses.KEY_NPAGE:
                self.scroll = max(0, self.scroll - page)
            elif key == curses.KEY_HOME:
                self.scroll = MAX_LINES * 10
            else:
                self.scroll = 0
        elif name == " ":
            self.pick = 0
            self.mode = "acciones"
        elif name == "u":
            self.show_tip(None)     # tip de la última sugerida (atajo viejo)
        elif VIM_PANE is None and name == "⏎" and self.sel_name:
            self.test(self.sel_name)
        else:
            for _, k, _, _, fn in self.actions():
                if k == name:
                    return fn() is not False
        return True

    def run(self):
        try:
            while True:
                self.poll_files()
                self.check_job()
                self.draw()
                key = self.scr.getch()
                if key == -1 or key == curses.KEY_RESIZE:
                    continue
                if not self.handle_key(key):
                    break
        finally:
            self.stop_job()


def main(scr):
    curses.curs_set(0)
    if USE_COLOR and curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 8):
            curses.init_pair(i, i, -1)
    scr.keypad(True)
    scr.timeout(150)
    App(scr).run()


if __name__ == "__main__":
    os.environ.setdefault("ESCDELAY", "25")
    # Si el locale del sistema no está instalado, usar uno UTF-8 genérico
    # para que los emojis y los ✔/✘ se vean bien.
    for loc in ("", "C.UTF-8", "en_US.UTF-8"):
        try:
            locale.setlocale(locale.LC_ALL, loc)
            break
        except locale.Error:
            pass
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
