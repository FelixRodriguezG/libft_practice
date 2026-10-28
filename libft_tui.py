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
import shutil
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
PALETTE = os.path.join(SCRIPT_DIR, ".libft_paleta")
# Dónde está el foco (menu, vim o nada): vim lo lee para apagarse sin foco.
FOCUS = os.path.join(SCRIPT_DIR, ".libft_foco")

# Panel de tmux con vim, si el menú se abrió con ./libft_43.sh menu.
VIM_PANE = os.environ.get("LIBFT_VIM_PANE")


TMUX_SESSION = "libft43"     # la sesión de ./libft_43.sh menu


def session_alive():
    """Si sigue abierta la sesión de tmux de ./libft_43.sh menu."""
    try:
        return subprocess.run(["tmux", "has-session", "-t", TMUX_SESSION],
                              capture_output=True).returncode == 0
    except OSError:
        return False


def vim_alive():
    """Si el panel de vim sigue abierto (se cierra al salir de vim)."""
    out = subprocess.run(["tmux", "list-panes", "-a", "-F", "#{pane_id}"],
                         capture_output=True, text=True).stdout
    return VIM_PANE in out.split()

MAX_LINES = 5000        # líneas de salida que se guardan
FOCUS_EVERY = 0.25      # segundos entre comprobaciones del foco en tmux
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
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

# Peticiones que puede hacer vim (F5, F6, F7, F8).
VIM_REQUESTS = ("test", "tip", "man", "main")

# Por debajo de este ancho, todo va en una columna.
STACK_BELOW = 100

# Órdenes cuya salida se lee desde el principio, no desde el final.
PINNED = ("tip", "nota", "casos", "progreso", "intentos", "man",
          "preparado", "modos")
# Órdenes de consulta que empiezan con la salida limpia.
CLEAN = ("tip", "man", "casos", "nota", "obsidian")

# Colores de cada fila del «43», como el degradado del logo de 42.
LOGO_COLORS = (6, 6, 4, 4, 5, 5, 5)

# Colores: 1 rojo, 2 verde, 3 amarillo, 4 azul, 5 magenta, 6 cian, 7 blanco.
RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = 1, 2, 3, 4, 5, 6, 7
DIM = 8     # no es un color: texto atenuado (\033[2m)

# Paletas (C en el menú): colores de 256 (y de 8, si la terminal no tiene
# más) para el cian, el azul y el magenta del menú, que son el acento, los
# separadores y el degradado del «43»; y el color del borde del panel activo
# en tmux. El verde de ✔ y el rojo de ✘ no cambian.
PALETTES = {
    "42": ({CYAN: (6, 6), BLUE: (4, 4), MAGENTA: (5, 5)}, "cyan"),
    "ámbar": ({CYAN: (214, 3), BLUE: (172, 3), MAGENTA: (167, 1)},
              "colour214"),
    "violeta": ({CYAN: (141, 5), BLUE: (99, 4), MAGENTA: (213, 5)},
                "colour141"),
}

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
            elif n == 2:
                color = DIM
            elif 31 <= n <= 37 or 91 <= n <= 97:
                color = n % 10
            elif n == 39:
                color = 0
        pos = m.end()
    if pos < len(line):
        segs.append((CONTROL.sub("", line[pos:]), color, bold))
    return segs


# Lo que va en el color por defecto de la terminal (en muchas, verde) se
# distingue: etiquetas al principio de línea («Motivo:»), comandos
# (libft_43.sh examen) y nombres de función (ft_memmove).
LABEL = re.compile(r"^(\s*)([^\W\d_][\w ¿?¡!]{0,28}:)(?=\s|$)")
WORDS = re.compile(r"(?P<cmd>(?:\./)?libft_43\.sh(?: (?:[a-z]+|ft_\w+|\d))*)"
                   r"|(?P<func>\bft_[a-z_]+\b)")


def colorize(segs):
    out = []
    for i, (text, color, bold) in enumerate(segs):
        if color:
            out.append((text, color, bold))
            continue
        if i == 0:
            m = LABEL.match(text)
            if m:
                out += [(m.group(1), 0, bold), (m.group(2), CYAN, True)]
                text = text[m.end():]
        pos = 0
        for m in WORDS.finditer(text):
            out.append((text[pos:m.start()], 0, bold))
            out.append((m.group(), MAGENTA, bold) if m.group("cmd")
                       else (m.group(), WHITE, True))
            pos = m.end()
        out.append((text[pos:], 0, bold))
    return [seg for seg in out if seg[0]]


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
    """Intentos en marcha: {nombre: (inicio, pistas, examen, pausa)}.
    pausa es cuándo se pausó (0: el tiempo corre)."""
    attempts = {}
    try:
        with open(ATTEMPTS, encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                if len(parts) in (4, 5):
                    attempts[parts[0]] = (
                        int(parts[1]), parts[2] == "1", parts[3] == "1",
                        int(parts[4]) if len(parts) == 5 else 0)
    except (OSError, ValueError):
        pass
    return attempts


def attempt_elapsed(attempt):
    """Segundos de un intento; en pausa, los que llevaba al pausarlo."""
    start, _, _, paused = attempt
    return (paused or int(time.time())) - start


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
        # Leyendo una nota que no cabe: ↑↓ desplazan la salida, no la
        # lista de archivos. Tab alterna; Esc (o la siguiente orden) lo quita.
        self.reading = False
        self.can_scroll = False     # la salida no cabe en su panel
        self.lock = threading.Lock()

        self.proc = None
        self.job_title = ""
        self.job_done = None
        self.job_start = 0
        self.step = None            # paso del test en marcha («⏳ …»)
        self.step_segs = None       # su línea en la salida, para cambiarla
        self.focused = True         # el foco está en el menú (no en vim)
        self.focus_written = None   # lo último escrito en FOCUS
        self.palette = "42"
        try:
            with open(PALETTE, encoding="utf-8") as f:
                name = f.read().strip()
            if name in PALETTES:
                self.palette = name
        except OSError:
            pass
        self.apply_palette()
        self.last_focus = 0
        self.titles = {}            # títulos de los paneles ya puestos
        self.last_test = ""         # último resultado de test (título de vim)
        self.last_test_name = None  # su función, para quitarlo si se borra
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
        self.vim_gone = False       # ya se ha avisado de que vim está cerrado
        if not os.environ.get("TMUX") and session_alive():
            self.status = (f"Tienes vim abierto en la sesión {TMUX_SESSION}: "
                           "⏎ vuelve a ella")

    # ---------- archivos e historial ----------

    def poll_files(self):
        now = time.time()
        if now - self.last_poll < POLL_EVERY:
            return
        self.last_poll = now
        if VIM_PANE and not self.vim_gone and not vim_alive():
            self.vim_gone = True
            self.status = "Has cerrado vim: ⏎ lo vuelve a abrir con el archivo"
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
        # Archivo borrado: su último test ya no vale (ni en el título de vim
        # ni en la barra de estado).
        if self.last_test_name and self.last_test_name not in mtimes:
            if self.status.startswith(self.last_test):
                self.status = ""
            self.last_test = ""
            self.last_test_name = None

        for name, when in list(self.changed.items()):
            if now - when < SAVE_SETTLE:
                continue
            del self.changed[name]
            if self.auto and name in mtimes:
                self.enqueue(["test", name], f"auto-test {name}", test=name)

    def read_requests(self):
        """Peticiones de vim (F5 test, F6 tip, F7 man, F8 tu main)."""
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
            elif cmd == "main":
                self.run_main(name)
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
        for name, (start, _, exam, _) in self.attempts.items():
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
        if args[:1] and args[0] in CLEAN:
            self.clear_output()
        self.add_line([])
        self.add_line([(f"── {title} · {stamp} ", CYAN, True)])
        self.scroll = 0
        self.pin_line = len(self.output) - 1 if args[:1] and args[0] in PINNED \
            else None
        self.reading = self.pin_line is not None
        self.job_title = title
        self.job_done = None
        self.job_start = time.time()
        self.step = None
        self.status = f"⏳ {title}…"
        # El man se formatea al ancho del panel de salida. LIBFT_TUI: el
        # script avisa de cada paso del test («::paso:: nombre»).
        env = dict(os.environ, MANWIDTH=str(max(40, self.out_width - 1)),
                   LIBFT_TUI="1")
        self.proc = subprocess.Popen(
            ["bash", SCRIPT, *args], cwd=self.cwd, env=env,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, start_new_session=True)
        threading.Thread(target=self.read_job, args=(self.proc,),
                         daemon=True).start()

    def read_job(self, proc):
        for raw in proc.stdout:
            line = raw.decode("utf-8", "replace")
            if line.startswith("::paso:: "):
                # Empieza un paso: «⏳ paso…» hasta que llegue su resultado.
                self.step = line[9:].strip()
                self.step_segs = [(f"  ⏳ {self.step}…", YELLOW, True)]
                self.add_line(self.step_segs)
                continue
            segs = colorize(parse_ansi(line))
            plain = "".join(seg[0] for seg in segs).strip()
            if self.step and plain[2:].startswith(self.step) \
                    and plain[:1] in "✔✘":
                self.replace_line(self.step_segs, segs)
                self.step = None
            else:
                self.add_line(segs)
        self.step = None
        self.job_done = proc.wait()

    def replace_line(self, old, new):
        """Cambia la línea old (la misma lista) de la salida por new."""
        with self.lock:
            for i in range(len(self.output) - 1, -1, -1):
                if self.output[i] is old:
                    self.output[i] = new
                    return
            self.output.append(new)

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
            self.last_test = self.status.split(" (")[0]
            name = self.job_title.split()[-1]
            self.last_test_name = name if name.startswith("ft_") else None
            if self.job_title.startswith("auto"):
                notify(self.status)
                if code != 0:
                    curses.beep()
        elif self.job_title.startswith("borrar"):
            self.status = f"{self.job_title}: hecho"
            if code == 0:
                self.after_delete(self.job_title.split()[-1])
        elif self.job_title.startswith("main"):
            self.status = (f"✔ {self.job_title}: terminó bien" if code == 0
                           else f"✘ {self.job_title}: falló (míralo abajo)")
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

    def run_main(self, name):
        """Compila y ejecuta tu main de name (la primera vez, lo crea)."""
        self.enqueue(["main", name], f"main {name}")

    def edit_main(self, name):
        """Abre en vim tu main de name (mains/main_ft_xxx.c)."""
        out = subprocess.run(["bash", SCRIPT, "editar-main", name],
                             cwd=self.cwd, capture_output=True, text=True)
        path = out.stdout.strip()
        if out.returncode != 0 or not path:
            self.status = f"✘ No he podido crear el main de {name}"
        elif VIM_PANE:
            self.open_in_vim(name, path=path)
        else:
            self.status = f"Tu main: {path} (b lo ejecuta)"

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

    def open_in_vim(self, name, reload=False, path=None, focus=True):
        """Abre name.c (o path) en el panel de vim y le pasa el foco. Con
        reload, descarta lo que hubiera en vim (archivo recién creado). Si
        has cerrado vim, vuelve a abrir su panel a la izquierda."""
        if not VIM_PANE or not name:
            return
        if not vim_alive():
            self.reopen_vim(name)
            return
        path = os.path.join(self.cwd, path or name + ".c").replace(" ", "\\ ")
        cmd = f":hide edit{'!' if reload else ''} {path}"
        try:
            for keys in (["Escape"], ["-l", cmd], ["Enter"]):
                subprocess.run(["tmux", "send-keys", "-t", VIM_PANE, *keys],
                               check=True, capture_output=True)
            if focus:
                subprocess.run(["tmux", "select-pane", "-t", VIM_PANE],
                               capture_output=True)
        except (OSError, subprocess.CalledProcessError):
            self.status = "✘ No encuentro el panel de vim (¿lo has cerrado?)"

    def enter_vim(self, name):
        """⏎: abre name.c en vim, y vim si no está abierto. Fuera de tmux
        cambia el menú por el espacio de trabajo (vim + menú), o vuelve a
        la sesión que siga abierta, con lo que tuvieras sin guardar."""
        if VIM_PANE:
            self.open_in_vim(name)
        elif os.environ.get("TMUX"):
            self.reopen_vim(name)
        elif self.proc or self.queue:
            self.status = "Hay un test en marcha: espera o páralo (s)"
        elif shutil.which("tmux"):
            curses.endwin()
            os.execv(SCRIPT, [SCRIPT, "menu", name])
        else:
            # Sin tmux: vim ocupa la terminal y al salir vuelve el menú.
            curses.endwin()
            subprocess.run(["vim", "-S", os.path.join(SCRIPT_DIR,
                                                      "libft_vim.vim"),
                            name + ".c"])
            self.scr.refresh()

    def reopen_vim(self, name):
        """Abre vim con name.c en un panel nuevo a la izquierda del menú."""
        global VIM_PANE
        try:
            out = subprocess.run(
                ["tmux", "split-window", "-hb", "-l", "55%",
                 "-t", os.environ.get("TMUX_PANE", ""), "-c", self.cwd,
                 "-P", "-F", "#{pane_id}",
                 "vim", "-S", os.path.join(SCRIPT_DIR, "libft_vim.vim"),
                 name + ".c"],
                check=True, capture_output=True, text=True)
        except (OSError, subprocess.CalledProcessError):
            self.status = "✘ No he podido volver a abrir vim"
            return
        VIM_PANE = out.stdout.strip()
        self.vim_gone = False
        self.status = f"vim abierto de nuevo con {name}.c"

    def poll_focus(self):
        """Si el foco está en el menú: el panel activo de la ventana activa
        y con alguien conectado. Fuera de tmux, siempre."""
        pane = os.environ.get("TMUX_PANE")
        now = time.time()
        if not pane or now - self.last_focus < FOCUS_EVERY:
            return
        self.last_focus = now
        try:
            out = subprocess.run(
                ["tmux", "list-panes", "-t", pane, "-F", "#{pane_id} "
                 "#{pane_active}#{window_active}#{session_attached}"],
                capture_output=True, text=True).stdout
        except OSError:
            return
        active = [line.split()[0] for line in out.splitlines()
                  if re.match(r"\S+ 11[1-9]", line)]
        self.focused = pane in active
        where = "menu" if self.focused else \
            "vim" if VIM_PANE in active else "nada"
        if VIM_PANE and where != self.focus_written:
            self.write_focus(where)

    def apply_palette(self):
        """Pone los colores de la paleta en el menú y en el borde de tmux."""
        pairs, border = PALETTES[self.palette]
        if USE_COLOR and curses.has_colors():
            for pair, (rich, basic) in pairs.items():
                curses.init_pair(pair, rich if curses.COLORS >= 256 else basic,
                                 -1)
        if VIM_PANE and os.environ.get("TMUX_PANE"):
            win = ["-w", "-t", os.environ["TMUX_PANE"]]
            for opt, value in (("@libft_color", border),
                               ("pane-active-border-style", f"fg={border}")):
                subprocess.run(["tmux", "set", *win, opt, value],
                               capture_output=True)

    def next_palette(self):
        names = list(PALETTES)
        self.palette = names[(names.index(self.palette) + 1) % len(names)]
        self.apply_palette()
        try:
            with open(PALETTE, "w", encoding="utf-8") as f:
                f.write(self.palette + "\n")
        except OSError:
            pass
        self.status = f"Paleta: {self.palette} (C para cambiarla)"

    def close_all(self):
        def close():
            self.stop_job()
            if vim_alive():
                # Guarda en vim (los archivos con nombre) antes de cerrar.
                for keys in (["Escape"], ["-l", ":silent! wall"], ["Enter"]):
                    subprocess.run(["tmux", "send-keys", "-t", VIM_PANE,
                                    *keys], capture_output=True)
                time.sleep(0.5)
            self.write_focus(None)
            # Al cerrar la sesión de ./libft_43.sh menu, tmux se apaga sin
            # llegar al hook de la pausa: se pausa aquí (y sigue al volver).
            session = subprocess.run(
                ["tmux", "display", "-p", "-t", os.environ.get("TMUX_PANE", ""),
                 "#{session_name}"], capture_output=True, text=True).stdout
            if session.strip() == TMUX_SESSION:
                subprocess.run(["bash", SCRIPT, "autopausa", "on"],
                               cwd=self.cwd, capture_output=True)
            # La ventana de vim y el menú (si es la única, toda la sesión).
            subprocess.run(["tmux", "kill-window", "-t",
                            os.environ.get("TMUX_PANE", "")],
                           capture_output=True)
            return False
        self.ask("¿Cerrar vim y el menú? Lo de vim se guarda.", close)

    def write_focus(self, where):
        """Deja dónde está el foco en FOCUS (None: lo borra)."""
        self.focus_written = where
        try:
            if where is None:
                os.remove(FOCUS)
            else:
                with open(FOCUS, "w", encoding="utf-8") as f:
                    f.write(where + "\n")
        except OSError:
            pass

    def set_title(self, pane, text):
        """Título del panel en su borde (@libft_title, ver libft_43.sh)."""
        if self.titles.get(pane) == text:
            return
        self.titles[pane] = text
        try:
            subprocess.run(["tmux", "set", "-p", "-t", pane, "@libft_title",
                            text], capture_output=True)
        except OSError:
            pass

    def update_titles(self):
        """Menú: «menú». Vim: el test en marcha o su último resultado, para
        verlo sin cambiar de panel."""
        pane = os.environ.get("TMUX_PANE")
        if not pane:
            return
        self.set_title(pane, "menú")
        if not VIM_PANE:
            return
        text = "vim"
        if self.proc:
            secs = int(time.time() - self.job_start)
            step = f" · {self.step}" if self.step else ""
            text += f" · ⏳ {self.job_title}{step} · {secs}s"
        elif self.last_test:
            text += f" · {self.last_test}"
        self.set_title(VIM_PANE, text)

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
        self.reading = False

    def surrender(self):
        exam = self.exam()
        self.ask(f"¿Rendirte en el examen de {exam[0]}?",
                 lambda: self.enqueue(["rendirse"], "rendirse") or True)

    def cancel(self, name):
        self.ask(f"¿Cancelar el cronómetro de {name}? El tiempo no se guarda.",
                 lambda: self.enqueue(["cancelar", name],
                                      f"cancelar {name}") or True)

    def delete(self, name):
        self.ask(f"¿Borrar {name}.c? Se guarda una copia en intentos/ y se "
                 "cancela su cronómetro.",
                 lambda: self.enqueue(["borrar", name],
                                      f"borrar {name}") or True)

    def after_delete(self, name):
        """Vim deja el archivo borrado y pasa a otro (sin quitarte el foco
        del menú)."""
        rest = [f for f in self.files if f != name]
        if not VIM_PANE or not vim_alive():
            return
        if rest:
            self.open_in_vim(rest[0], focus=False)
            return
        try:
            for keys in (["Escape"], ["-l", ":enew"], ["Enter"]):
                subprocess.run(["tmux", "send-keys", "-t", VIM_PANE, *keys],
                               capture_output=True)
        except OSError:
            pass

    def reset_counter(self):
        self.ask("¿Poner a cero las veces que ha salido cada función? "
                 "El historial y los tiempos no se tocan.",
                 lambda: self.enqueue(["reset"], "reset") or True)

    def reset_all(self):
        self.ask("¿Borrar TODO el progreso: historial, tiempos, sugerencias e "
                 "intentos en marcha? No se puede deshacer. Tus ft_*.c e "
                 "intentos/ se quedan.",
                 lambda: self.enqueue(["reset", "todo"], "reset todo") or True)

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
        add(g, "⏎", "Abrir en vim",
            "Abre el archivo en vim y te lleva allí. Si vim no está abierto, "
            "lo abre (o vuelve a la sesión de vim que siga abierta).",
            lambda: self.enter_vim(sel), ok=sel)
        add(g, "t", "Testear",
            "Norminette, libftTester con valgrind y las reglas del subject. "
            "En vim: F5.", lambda: self.test(sel), ok=sel)
        add(g, "m", "Man / nota",
            "La página de man de la función original. En las Partes 2 y 3 "
            "(no tienen man), el pseudocódigo y su nota de Obsidian, que "
            "cuentan como pista; en examen, solo su ficha del subject. En "
            "vim: F7.",
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
        attempt = self.attempts.get(sel)
        add(g, "z", "Reanudar el cronómetro" if attempt and attempt[3]
            else "Pausar el cronómetro",
            "Congela el tiempo del intento (por ejemplo, para descansar); "
            "pulsa otra vez para que siga contando.",
            lambda: self.run_on("pausa", sel), ok=attempt)
        add(g, "x", "Cancelar el cronómetro",
            "Lo para y lo quita sin guardar el tiempo, hasta el próximo "
            "intento. El archivo no se borra.",
            lambda: self.cancel(sel), ok=attempt)
        add(g, "b", "Ejecutar tu main",
            "Compila tu main (mains/main_ft_xxx.c) con este archivo y el "
            "resto de tu libft y lo ejecuta con valgrind. La primera vez lo "
            "crea vacío. No cuenta para el historial. En vim: F8.",
            lambda: self.run_main(sel), ok=sel)
        add(g, "B", "Editar tu main",
            "Abre en vim tu main de esta función (lo crea si no existe). "
            "Vuelve a tu ft_xxx.c con ⏎ en el menú o :b# en vim.",
            lambda: self.edit_main(sel), ok=sel)
        add(g, "d", "Borrar el archivo",
            "Quita este ft_xxx.c de la lista. No se pierde: se guarda en "
            "intentos/ (v para verlo). Se cancela su cronómetro; el "
            "historial no cambia.", lambda: self.delete(sel), ok=sel)
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
        add(g, "M", "Modos de resolución",
            "Cómo funcionan la práctica, el examen y los tests sin "
            "cronómetro, y qué cuenta para el progreso y para «¿Preparado?».",
            lambda: self.enqueue(["modos"], "modos"))
        add(g, "p", "Progreso de las 43",
            "Estado, días resueltas, mejor tiempo y cuándo toca repasar.",
            lambda: self.enqueue(["progreso"], "progreso"))
        add(g, "H", "Historial completo", "Todos los tests que has hecho.",
            lambda: self.enqueue(["historial"], "historial"))

        g = "Menú"
        add(g, "c", "Limpiar la salida", "", self.clear_output)
        add(g, "0", "Poner a cero las sugerencias",
            "Cuántas veces ha salido cada función. Las que salieron y no "
            "testeaste vuelven a salir más. No borra el historial ni los "
            "tiempos.", self.reset_counter)
        add(g, "R", "Empezar desde cero",
            "Borra el historial, los tiempos, las sugerencias y los intentos "
            "en marcha: el progreso y «¿Preparado?» vuelven a empezar. Tu "
            "código (ft_*.c e intentos/) no se toca.", self.reset_all)
        add(g, "C", "Cambiar la paleta de colores",
            f"Ahora: {self.palette}. Pasa a la siguiente: "
            f"{' → '.join(PALETTES)}. Se recuerda para la próxima vez.",
            self.next_palette)
        add(g, "?", "Ayuda", "Teclas y símbolos.", self.open_help)
        add(g, "q", "Salir", "", self.quit)
        add(g, "Q", "Cerrar todo (vim y menú)",
            "Guarda lo que tengas en vim y cierra vim y el menú a la vez. El "
            "cronómetro se pausa hasta que vuelvas.", self.close_all,
            ok=VIM_PANE)
        return acts

    def footer_keys(self):
        """Las pocas teclas que más se usan ahora mismo."""
        short = {"r": "sugerir", "n": "elegir", "E": "examen", "t": "test",
                 "i": "pista", "m": "man", "s": "parar", "x": "cancelar",
                 "z": "pausa",
                 "⏎": "abrir en vim"}
        if not self.sel_name:
            keys = ["r", "n", "E"]
        elif self.exam():
            keys = ["⏎", "t", "m", "E"]
            short["E"] = "rendirse"
        else:
            keys = ["⏎", "t", "i", "m"]
            attempt = self.attempts.get(self.sel_name)
            if attempt:
                keys += ["z", "x"]
                if attempt[3]:
                    short["z"] = "seguir"
            else:
                keys.append("r")
        if self.proc:
            keys.insert(0, "s")
        available = {a[1] for a in self.actions()}
        items = [(k, short[k]) for k in keys if k in available]
        return items + [("espacio", "acciones"), ("?", "ayuda")]

    # ---------- dibujo ----------

    def put(self, y, x, text, attr=0, width=None):
        if not self.focused:
            attr |= curses.A_DIM    # sin foco, el menú se apaga
        h, w = self.scr.getmaxyx()
        if y < 0 or y >= h or x >= w:
            return
        width = w - x if width is None else min(width, w - x)
        try:
            self.scr.addstr(y, x, clip(text, width), attr)
        except curses.error:
            pass    # escribir en la última celda da error, pero se pinta

    def attr(self, color, bold=False):
        if color == DIM:
            return curses.A_DIM | (curses.A_BOLD if bold else 0)
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
        """Barra de título con el estilo de la cabecera de 42: /* … */
        En color con el foco en el menú; apagada con el foco en vim."""
        bar = curses.A_REVERSE
        head = bar | (self.attr(CYAN) if self.focused else curses.A_DIM)
        self.put(0, 0, " " * w, head)
        self.put(0, 0, " /* libft · 43 */" if self.focused
                 else " /* libft · 43 */  (foco en vim)", head | curses.A_BOLD)
        parts = []
        exam = self.exam()
        if exam:
            parts.append((f" 📝 EXAMEN {exam[0]} "
                          f"{fmt_time(attempt_elapsed(self.attempts[exam[0]]))} ",
                          self.attr(RED, True) | bar))
        ready, total = self.ready
        if total:
            done = ready == total
            parts.append((" 🎯 ¡preparado! " if done
                          else f" 🎯 examen {ready}/{total} ",
                          bar | self.attr(GREEN, True) if done else head))
        if self.auto:
            parts.append((" auto-test ", self.attr(GREEN, True) | bar))
        if self.queue:
            parts.append((f" cola: {len(self.queue)} ", head))
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
            # Con el foco en vim, el «43» se apaga.
            attr = (self.attr(color, i == len(self.logo) - 1)
                    if self.focused else curses.A_DIM)
            self.put(top + i, 1, line, attr, width - 2)
        x = logo_w + 3
        if width - x >= 12:
            s = self.states
            side = [(1, "libft · 43", self.attr(CYAN, True) if self.focused
                     else curses.A_DIM),
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
            self.put(y, left + 4, name, base | self.attr(WHITE, True),
                     width - 4)
            x = left + 4 + name_w + 1
            if self.is_stale(name):
                self.put(y, x, "●", base | self.attr(YELLOW, True))
            x += 2
            attempt = self.attempts.get(name)
            if attempt:
                # Intento en marcha: cronómetro en vez del último resultado.
                exam, paused = attempt[2], attempt[3]
                clock = ("⏸ " if paused else "📝 " if exam else "⏱ ") + \
                    fmt_time(attempt_elapsed(attempt))
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
            _, hints, exam, paused = attempt
            state = ("⏸ en pausa" if paused else
                     "📝 examen" if exam else "⏱ en marcha")
            text = (f"{state}: {fmt_time(attempt_elapsed(attempt))} · "
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

        # El modo y qué cuenta si el test pasa ahora (M: cómo funciona).
        for line in wrap_text(self.mode_text(name, attempt, d), width - 2)[:2]:
            self.put(y, left + 1, line, curses.A_DIM, width - 2)
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

    @staticmethod
    def mode_text(name, attempt, d):
        """Modo de resolución de name y qué cuenta si el test pasa ahora."""
        key = d.get("ready", "-") != "-"
        if attempt and attempt[2]:
            return "Examen · si pasa, cuenta para «¿Preparado?» · M: modos"
        if attempt and attempt[1]:
            return ("Práctica con pistas · si pasa, cuenta para el progreso"
                    + (", no para «¿Preparado?»" if key else "")
                    + " · M: modos")
        if attempt:
            return ("Práctica sin pistas · si pasa, "
                    + ("cuenta para «¿Preparado?»" if key
                       else "se guarda el tiempo") + " · M: modos")
        return ("Sin cronómetro · el test cuenta para el progreso"
                + (", no para «¿Preparado?» (r o n para cronometrar)"
                   if key else "") + " · M: modos")

    def draw_output(self, top, left, height, width):
        self.out_width = width
        with self.lock:
            lines = list(self.output)
        title = "Salida"
        if self.proc:
            spin = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[int(time.time() * 8) % 10]
            title = f"Salida {spin} {self.job_title}"
        if not lines:
            self.rule(top, left, width, title)
            self.draw_welcome(top + 1, left, width)
            return

        # Solo se envuelven las líneas necesarias, empezando por el final.
        rows_h = height - 1
        if self.pin_line is not None:
            pinned = sum(len(wrap(segs, width - 1))
                         for segs in lines[self.pin_line:])
            self.scroll = max(0, pinned - rows_h)
        # Una fila de más: para saber si queda algo por encima (can_scroll)
        # aunque estés al final.
        rows_needed = rows_h + self.scroll + 1
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
        self.can_scroll = len(rows) > rows_h
        more = f"↓ {self.scroll} más" if self.scroll else ""
        if self.can_scroll:
            more = " · ".join(filter(None, [
                more, "↑↓ desplazar · Tab archivos" if self.reading
                else "Tab: ↑↓ en la salida"]))
        self.rule(top, left, width, title, more)
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

    def job_text(self):
        """El trabajo en marcha: «⠹ test ft_x · libftTester · 4s»."""
        secs = int(time.time() - self.job_start)
        spin = SPINNER[int(time.time() * 8) % len(SPINNER)]
        step = f" · {self.step}" if self.step else ""
        return f"{spin} {self.job_title}{step} · {secs}s"

    def draw_status(self, y, w):
        if self.proc:
            self.put(y, 0, " " + self.job_text(), self.attr(YELLOW, True),
                     w - 1)
            return
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
                  ("  Tab  con una salida larga, ↑↓ jk la desplazan;", 0),
                  ("       Tab (o Esc) las devuelve a los archivos", 0),
                  ("  espacio  menú de acciones", 0)]
        if VIM_PANE:
            lines += [("", 0), ("En vim", CYAN),
                      ("  F5 guardar y testear · F6 pista · F7 man · F8 tu main", 0),
                      ("  Ctrl-b + flecha (o clic): cambiar de panel", 0),
                      ("  Mayús + arrastrar: seleccionar y copiar texto", 0)]
        lines += [("", 0), ("Símbolos", CYAN),
                  ("  ✔ último test perfecto · ✘ con fallos · · sin testear", 0),
                  ("  ● cambiado desde el último test", 0),
                  ("  ⏱ intento en marcha · ⏸ en pausa · 📝 examen", 0),
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
        up = key == curses.KEY_UP or name == "k"
        down = key == curses.KEY_DOWN or name == "j"
        if self.reading and self.can_scroll and (up or down):
            self.pin_line = None
            self.scroll = self.scroll + 1 if up else max(0, self.scroll - 1)
        elif up:
            self.move_sel(-1)
        elif down:
            self.move_sel(1)
        elif key == 9 and self.can_scroll:
            self.reading = not self.reading
        elif key == 27:
            self.reading = False
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
                self.poll_focus()
                self.update_titles()
                self.draw()
                key = self.scr.getch()
                if key == -1 or key == curses.KEY_RESIZE:
                    continue
                if not self.handle_key(key):
                    break
        finally:
            self.stop_job()
            if self.focus_written:
                self.write_focus(None)      # sin menú, vim no se apaga


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
    # tmux anuncia «screen» (8 colores) aunque maneja 256: para las paletas.
    if os.environ.get("TMUX") and os.environ.get("TERM") in ("screen", "tmux"):
        for term in ("tmux-256color", "screen-256color"):
            if subprocess.run(["infocmp", term],
                              capture_output=True).returncode == 0:
                os.environ["TERM"] = term
                break
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
