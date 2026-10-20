#!/bin/bash
# Sugiere una función de la libft para practicar y crea ft_xxx.c con el
# prototipo listo para empezar. Elige más a menudo las que has fallado o
# nunca has hecho, y vuelve a sacar las que dominas para repasarlas.
# Uso: ./libft_43.sh [orden] (./libft_43.sh help para la ayuda)
#   [1|2|3]: sugiere una función (de una parte o de todas).
#   examen [1|2|3]: como sugerir, pero sin pistas hasta resolverla.
#   rendirse: abandona el examen y vuelve a permitir las pistas.
#   pausa [ft_xxx]: pausa el cronómetro del intento (otra vez: sigue).
#   cancelar [ft_xxx]: quita el cronómetro sin guardar el tiempo.
#   new ft_xxx: crea el archivo de una función concreta.
#   test [ft_xxx ...]: norminette, libftTester y reglas del subject.
#   tip [ft_xxx] [2]: puntos clave (2: pseudocódigo) de tus notas.
#   nota | casos | obsidian [ft_xxx]: nota entera, casos límite, Obsidian.
#   progreso: estado de las 43 funciones.
#   preparado: si estás listo para el examen (funciones clave).
#   man [ft_xxx]: man de la original o el subject (vale en examen).
#   intentos [ft_xxx]: intentos en marcha o versiones guardadas.
#   menu [ft_xxx]: vim y el menú juntos en tmux. tui: solo el menú.
#   cabecera [ft_xxx ...]: rehace la cabecera con el «43».
#   historial [ft_xxx], lista, reset, help.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
COUNTS="$SCRIPT_DIR/.libft_counts"
HISTORY="$SCRIPT_DIR/.libft_historial"
LAST="$SCRIPT_DIR/.libft_ultima"
ATTEMPTS="$SCRIPT_DIR/.libft_intentos"
AUTOPAUSE="$SCRIPT_DIR/.libft_autopausa"
ARCHIVE_DIR="intentos"

# Rutas y datos de cada uno. Los valores por defecto se cambian en
# config.sh (copia de config.example.sh), que no se sube a git.
LIBFT_DIR="$HOME/libft"
TESTER_DIR="$HOME/libftTester"
NOTES_DIR="$SCRIPT_DIR/notas"
SUBJECT_PDF=""
MAIL42="$USER@student.42barcelona.com"
# shellcheck source=config.example.sh
[ -f "$SCRIPT_DIR/config.sh" ] && . "$SCRIPT_DIR/config.sh"
EDGE_NOTE=$(find "$NOTES_DIR" -name 'libft - Edge cases y tests por función.md' \
	-print -quit 2> /dev/null)

touch "$COUNTS" "$HISTORY" "$ATTEMPTS"

# Para practicar hace falta la libft terminada: el test la usa como base y
# solo sustituye la función practicada. Comprueba que estén libft.h y las
# 43 funciones (y libftTester, con $1 = test).
check_setup() {
	local missing=() entry

	if [ ! -f "$LIBFT_DIR/libft.h" ]; then
		echo -e "\033[1;31mNo encuentro tu libft en $LIBFT_DIR\033[0m"
		echo "Pon la ruta de tu libft terminada en LIBFT_DIR, en $SCRIPT_DIR/config.sh"
		echo "(cp config.example.sh config.sh si aún no lo tienes)."
		return 1
	fi
	for entry in "${PART1[@]}" "${PART2[@]}" "${PART3[@]}"; do
		[ -f "$LIBFT_DIR/${entry%%|*}.c" ] || missing+=("${entry%%|*}")
	done
	if [ ${#missing[@]} -gt 0 ]; then
		echo -e "\033[1;31mTu libft ($LIBFT_DIR) no está terminada: faltan ${#missing[@]} funciones.\033[0m"
		echo "  ${missing[*]}"
		echo "Esta herramienta es para practicar con la libft acabada (examen o defensa)."
		return 1
	fi
	if [ "$1" = test ] && [ ! -d "$TESTER_DIR/tests" ]; then
		echo -e "\033[1;31mNo encuentro libftTester en $TESTER_DIR\033[0m"
		echo "  git clone https://github.com/Tripouille/libftTester.git $TESTER_DIR"
		echo "o pon su ruta en TESTER_DIR, en $SCRIPT_DIR/config.sh"
		return 1
	fi
}

# Funciones externas que el subject permite usar en cada función.
declare -A ALLOWED=(
	[ft_calloc]="malloc" [ft_strdup]="malloc"
	[ft_substr]="malloc" [ft_strjoin]="malloc" [ft_strtrim]="malloc"
	[ft_split]="malloc free" [ft_itoa]="malloc" [ft_strmapi]="malloc"
	[ft_putchar_fd]="write" [ft_putstr_fd]="write"
	[ft_putendl_fd]="write" [ft_putnbr_fd]="write"
	[ft_lstnew]="malloc" [ft_lstdelone]="free" [ft_lstclear]="free"
	[ft_lstmap]="malloc free"
)

# Funciones clave para el examen: las más complejas y representativas de
# cada categoría. Estás preparado cuando las has resuelto todas sin pistas
# (o en examen) en los últimos READY_DAYS días, sin ningún fallo después.
READY_DAYS=14
EXAM_SET=(
	"Caracteres|ft_isalnum"
	"Memoria|ft_memmove"
	"Cadenas|ft_strlcat ft_strnstr"
	"Conversión|ft_atoi ft_itoa"
	"Memoria dinámica|ft_calloc"
	"Cadenas nuevas|ft_split ft_strtrim ft_substr"
	"Punteros a función|ft_strmapi"
	"Escritura en fd|ft_putnbr_fd"
	"Listas|ft_lstnew ft_lstadd_front ft_lstsize ft_lstlast ft_lstadd_back ft_lstdelone ft_lstclear ft_lstiter ft_lstmap"
)

# Resultados del modo test, para el resumen final.
SUMMARY=()
TOTAL_OK=0
TOTAL_KO=0

# Guarda una línea del resumen: nombre, resultado y si ha pasado (0) o no.
# Si se pasa un cuarto argumento, también la guarda en el historial.
add_summary() {
	local mark
	if [ "$3" -eq 0 ]; then
		mark="✔"
		SUMMARY+=("$(printf '\033[32m✔\033[0m %-18s %s' "$1" "$2")")
	else
		mark="✘"
		SUMMARY+=("$(printf '\033[31m✘\033[0m %-18s %s' "$1" "$2")")
	fi
	if [ -n "$4" ]; then
		printf '%s  %s %-18s %s\n' "$(date '+%Y-%m-%d %H:%M')" "$mark" "$1" "$2" >> "$HISTORY"
	fi
}

# Pasos del test. El menú (LIBFT_TUI) muestra «⏳ paso…» mientras dura y lo
# cambia por la línea de step_done al acabar.
step() {
	if [ -n "$LIBFT_TUI" ]; then echo "::paso:: $1"; fi
}

# Resultado de un paso: $1 nombre, $2 estado (0 bien), $3 detalle opcional.
step_done() {
	local detail="${3:+: $3}"

	if [ "$2" -eq 0 ]; then
		echo -e "  \033[32m✔\033[0m $1\033[2m$detail\033[0m"
	else
		echo -e "  \033[1;31m✘ $1$detail\033[0m"
	fi
}

# Casos de libftTester: el código de cada uno, sacado de su .cpp (lo que va
# entre un caso y el anterior, y lo que comprueba), con su resultado.
# $1: el .cpp del test, $2: su salida sin colores.
show_cases() {
	python3 - "$1" "$2" <<'EOF'
import re
import sys

SKIP = ("//", "/*", "#", "title(", "signal(", "write(1", "showLeaks", "free(",
        "return", "{", "}", "int iTest", "int main", "extern", "using")


def call_args(line, start):
    # Lo que va entre los paréntesis de la llamada que empieza en start.
    depth, quote = 0, None
    for i in range(start, len(line)):
        c = line[i]
        if quote:
            if c == "\\":
                continue
            if c == quote and line[i - 1] != "\\":
                quote = None
        elif c in "\"'":
            quote = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return line[line.index("(", start) + 1:i]
    return line[start:]


def short(text, width):
    return text if len(text) <= width else text[:width - 1] + "…"


def find_check(line):
    # Lo que comprueba el check() o mcheck() de la línea, o None.
    m = re.search(r"\b(m?check)\s*\(", line)
    if not m:
        return None
    args = call_args(line, m.start(1))
    if m.group(1) == "mcheck":
        ptr, _, size = args.partition(",")
        args = f"malloc de {ptr.strip()}: {size.strip()} bytes"
    return args


# Los casos van numerados en un comentario: /* 3 */, /* 15 autor */,
# /* autor 15 */ o /* 1 2 3 4 */ delante de un bucle con el check dentro.
cases, setup, loop = [], [], None
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    m = re.match(r"\s*/\*([^*]*)\*/(.*)", line)
    nums = re.findall(r"\b\d+\b", m.group(1)) if m else []
    if nums:
        check = find_check(m.group(2))
        if check is None:
            loop = (nums, m.group(2).strip())
            continue
        for num in nums:
            cases.append((num, check, " ".join(setup)))
        setup = []
        continue
    check = find_check(line) if loop else None
    if check is not None:
        nums, head = loop
        for i, num in enumerate(nums, 1):
            cases.append((num, f"{check} (vuelta {i})",
                          " ".join(setup + [head])))
        setup, loop = [], None
        continue
    text = re.sub(r"\s*(free\([^)]*\);|showLeaks\(\);)", "", line.strip())
    if text and not text.startswith(SKIP):
        setup.append(text)

log = open(sys.argv[2], encoding="utf-8", errors="replace").read()
results = dict(re.findall(r"(\d+)\.(M?OK|M?KO)", log))
for num, check, before in cases:
    res = results.get(num)
    if res is None:
        print(f"      \033[2m· {num:>2}  {short(check, 90)} (no se ejecutó)\033[0m")
    elif res.endswith("OK"):
        code = f"{before} → {check}" if before else check
        print(f"      \033[32m✔\033[0m \033[2m{num:>2}\033[0m  {short(code, 100)}")
    else:
        if before:
            print(f"      \033[1;31m✘ {num:>2}\033[0m  {before}")
            print(f"            \033[31m→ {check}\033[0m")
        else:
            print(f"      \033[1;31m✘ {num:>2}  {check}\033[0m")
for num in sorted(set(results) - {c[0] for c in cases}, key=int):
    mark = "\033[32m✔\033[0m" if results[num].endswith("OK") else "\033[1;31m✘\033[0m"
    print(f"      {mark} {num:>2}  (caso sin anotar en el .cpp)")
if "LEAKS.KO" in log:
    print("      \033[1;31m✘ fugas de memoria (LEAKS.KO)\033[0m")
if "SIGSEGV" in log:
    last = max(map(int, results), default=0)
    print(f"      \033[1;31m✘ SIGSEGV en el caso {last + 1}\033[0m")
EOF
}

# Pasa norminette al archivo y deja el resultado en NORM.
check_norm() {
	local out

	if ! command -v norminette > /dev/null; then
		NORM="norma no comprobada"
		return 0
	fi
	out=$(norminette "$1" 2>&1)
	if grep -qE '^Error|: Error!' <<< "$out"; then
		echo "$out"
		NORM="norma KO"
		return 1
	fi
	NORM="norma OK"
	return 0
}

show_history() {
	if [ ! -s "$HISTORY" ]; then
		echo "Todavía no hay historial."
		return
	fi
	if [ -n "$1" ]; then
		grep -E " ${1%.c} " "$HISTORY" || echo "No hay historial de ${1%.c}."
	else
		cat "$HISTORY"
	fi
}

# ---------- intentos y tiempo de resolución ----------
# .libft_intentos tiene una línea por intento en marcha:
#   nombre inicio(epoch) pistas(0/1) examen(0/1) [pausa(epoch, 0: no)]
# Al reanudar, el inicio se adelanta lo que ha durado la pausa.

fmt_time() {
	printf '%dm%02ds' $(($1 / 60)) $(($1 % 60))
}

attempt_get() {
	awk -v n="$1" '$1 == n { print; exit }' "$ATTEMPTS"
}

attempt_del() {
	grep -v "^$1 " "$ATTEMPTS" > "$ATTEMPTS.tmp"
	mv "$ATTEMPTS.tmp" "$ATTEMPTS"
}

attempt_set() {
	attempt_del "$1"
	echo "$*" >> "$ATTEMPTS"
}

# Segundos de intento con inicio $1 y pausa $2 (en pausa no avanza).
attempt_elapsed() {
	if [ "${2:-0}" -gt 0 ]; then
		echo $(($2 - $1))
	else
		echo $(($(date +%s) - $1))
	fi
}

# Pausa el intento de $1 o, si ya está en pausa, lo reanuda.
attempt_pause() {
	local start hints exam paused now

	read -r _ start hints exam paused <<< "$(attempt_get "$1")"
	if [ -z "$start" ]; then
		echo "No hay ningún intento en marcha de $1."
		return 1
	fi
	now=$(date +%s)
	if [ "${paused:-0}" -gt 0 ]; then
		start=$((start + now - paused))
		attempt_set "$1" "$start" "$hints" "$exam" 0
		echo -e "\033[1;33m▶ $1: el tiempo vuelve a contar" \
			"(llevas $(fmt_time $((now - start))))\033[0m"
	else
		attempt_set "$1" "$start" "$hints" "$exam" "$now"
		echo -e "\033[1;33m⏸ $1 en pausa con $(fmt_time $((now - start)))\033[0m"
		echo "Para seguir: $(basename "$0") pausa $1"
	fi
}

# Al cerrar la ventana de la sesión (o salir con Ctrl-b d) se pausa el
# cronómetro que esté corriendo ($1 = on); al volver, sigue ($1 = off).
# Las pausas que hagas tú no se tocan.
auto_pause() {
	local name paused

	if [ "$1" = on ]; then
		name=$(awk '$5 == "" || $5 == 0 { print $1; exit }' "$ATTEMPTS")
		[ -z "$name" ] && return
		attempt_pause "$name" > /dev/null
		echo "$name" > "$AUTOPAUSE"
	elif [ -s "$AUTOPAUSE" ]; then
		name=$(cat "$AUTOPAUSE")
		rm -f "$AUTOPAUSE"
		read -r _ _ _ _ paused <<< "$(attempt_get "$name")"
		[ "${paused:-0}" -gt 0 ] && attempt_pause "$name" > /dev/null
	fi
	return 0
}

# Nombre de la función con el examen en marcha (vacío si no hay).
exam_name() {
	awk '$4 == 1 { print $1; exit }' "$ATTEMPTS"
}

# Antes de mostrar una pista: la bloquea en examen y, si hay un intento en
# marcha, lo marca como resuelto con pistas.
use_hint() {
	local start hints exam paused

	read -r _ start hints exam paused <<< "$(attempt_get "$1")"
	[ -z "$start" ] && return 0
	if [ "$exam" = 1 ]; then
		echo -e "\033[1;31m📝 Modo examen: no hay pistas de $1.\033[0m"
		echo "El man sí está permitido: $(basename "$0") man $1"
		echo "Para ver las pistas, abandona el examen: $(basename "$0") rendirse"
		return 1
	fi
	[ "$hints" = 1 ] && return 0
	attempt_set "$1" "$start" 1 0 "${paused:-0}"
	echo -e "\033[2m(este intento contará como resuelto con pistas)\033[0m"
}

show_attempts() {
	if [ ! -s "$ATTEMPTS" ]; then
		echo "No hay intentos en marcha."
	else
		echo -e "\033[1;36m⏱ Intentos en marcha\033[0m"
		awk -v now="$(date +%s)" '{
			s = ($5 > 0 ? $5 : now) - $2
			printf "  %-18s %dm%02ds%s%s%s\n", $1, s / 60, s % 60,
				($3 ? "  con pistas" : ""), ($4 ? "  \033[1;31m📝 examen\033[0m" : ""),
				($5 > 0 ? "  ⏸ en pausa" : "")
		}' "$ATTEMPTS"
	fi
	if [ -d "$ARCHIVE_DIR" ]; then
		echo -e "\n\033[1;36m🗂 Versiones guardadas en $ARCHIVE_DIR/\033[0m"
		find "$ARCHIVE_DIR" -name 'ft_*.c' -printf '%f\n' \
			| sed -E 's/_[0-9]{8}-[0-9]{6}\.c$//' | sort | uniq -c \
			| awk '{ printf "  %-18s %d\n", $2, $1 }'
	fi
}

# ---------- estadísticas y elección de función ----------

# Una línea por función, separada por tabuladores:
#   parte nombre veces_sugerida estado peso motivo días_con_✔ mejor_tiempo
#   categoría_examen preparación días_desde_el_último_✔_sin_pistas
# Estados: · sin hacer, ✘ falló el último test, ⟳ toca repasar, ✔ dominada.
# Preparación (solo funciones clave): lista, falla, caducada o pendiente.
# Repetición espaciada: tras 1, 2, 3… días distintos con ✔ seguidos, la
# función vuelve a tocar a los 1, 3, 7, 14, 30 y 60 días.
function_stats() {
	local p entry keys=""

	for entry in "${EXAM_SET[@]}"; do
		for p in ${entry#*|}; do
			keys="$keys$p=${entry%%|*};"
		done
	done

	for p in 1 2 3; do
		declare -n part="PART$p"
		for entry in "${part[@]}"; do
			echo "$p ${entry%%|*}"
		done
	done | awk -v today="$(date +%F)" -v last="$(cat "$LAST" 2>/dev/null)" \
		-v keys="$keys" -v ready_days="$READY_DAYS" '
	function days(date,   d, y, m) {
		split(date, d, "-")
		y = d[1]; m = d[2]
		if (m <= 2) { y--; m += 12 }
		return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d[3]
	}
	function ndays(k) { return k == 1 ? "1 día" : k " días" }
	BEGIN {
		split("1 3 7 14 30 60", iv, " ")
		OFS = "\t"
		nk = split(keys, kv, ";")
		for (i = 1; i < nk; i++) {
			split(kv[i], pair, "=")
			cat[pair[1]] = pair[2]
		}
	}
	FILENAME == ARGV[1] { count[$1] = $2; next }
	FILENAME == ARGV[2] {
		n = $4
		tested[n] = 1
		if ($3 == "✘") {
			mark[n] = "✘"; streak[n] = 0; lastok[n] = ""
			delete nohint[n]
			next
		}
		if ($0 ~ /sin pistas/) nohint[n] = $1
		mark[n] = "✔"
		if (!((n, $1) in okday)) { okday[n, $1] = 1; okdays[n]++ }
		if ($1 != lastok[n]) streak[n]++
		lastok[n] = $1
		if ($0 !~ /con pistas/ && match($0, /tiempo [0-9]+m[0-9]+s/)) {
			split(substr($0, RSTART + 7, RLENGTH - 8), t, "m")
			secs = t[1] * 60 + t[2]
			if (!(n in best) || secs < best[n]) best[n] = secs
		}
		next
	}
	{
		n = $2
		c = (n in count) ? count[n] : 0
		if (!(n in tested)) {
			st = "·"; w = c ? 3 : 5
			why = c ? "sugerida pero sin testear" : "nunca la has hecho"
		} else if (mark[n] == "✘") {
			st = "✘"; w = 8; why = "falló el último test"
		} else {
			k = streak[n] < 6 ? streak[n] : 6
			ago = days(today) - days(lastok[n])
			if (ago >= iv[k]) {
				st = "⟳"; w = 4; why = "toca repasar (último ✔ hace " ndays(ago) ")"
			} else {
				st = "✔"; w = 1; why = iv[k] - ago == 1 ? "repaso mañana" : "repaso en " iv[k] - ago " días"
			}
		}
		ago = (n in nohint) ? days(today) - days(nohint[n]) : -1
		if (!(n in cat)) r = "-"
		else if (mark[n] == "✘") r = "falla"
		else if (ago < 0) r = "pendiente"
		else r = (ago <= ready_days) ? "lista" : "caducada"
		# Las funciones clave que aún no tienes listas salen más.
		if (r != "-" && r != "lista") w += 2
		if (n == last) w = 0
		print $1, n, c, st, w, why, okdays[n] + 0, (n in best) ? best[n] : -1,
			(n in cat) ? cat[n] : "", r, ago
	}' "$COUNTS" "$HISTORY" -
}

# Elige una función al azar según los pesos; $1 limita a una parte.
# Con $2 = 1 (examen) solo elige funciones clave, primero las que no
# tienes listas.
pick_function() {
	function_stats | awk -F'\t' -v part="$1" -v exam="$2" -v seed="$RANDOM$RANDOM" '
	BEGIN {
		srand(seed)
		ew["falla"] = 8; ew["pendiente"] = 6; ew["caducada"] = 4; ew["lista"] = 1
	}
	exam == 1 && $10 == "-" { next }
	part == "" || $1 == part {
		line[++n] = $0
		w[n] = (exam == 1) ? ($5 ? ew[$10] : 0) : $5
		total += w[n]
	}
	END {
		if (total == 0)
			for (i = 1; i <= n; i++) { w[i] = 1; total++ }
		r = rand() * total
		for (i = 1; i <= n; i++)
			if ((r -= w[i]) < 0) { print line[i]; exit }
		print line[n]
	}'
}

show_progress() {
	function_stats | awk -F'\t' '
	BEGIN {
		color["✔"] = 32; color["⟳"] = 33; color["✘"] = 31; color["·"] = 2
		title[1] = "Parte 1 · libc"; title[2] = "Parte 2 · adicionales"
		title[3] = "Parte 3 · listas"
	}
	{
		total[$4]++
		if ($1 != part) { part = $1; out = out "\n\033[1;36m" title[part] "\033[0m\n" }
		extra = ($7 ? sprintf("%2d %s ✔", $7, $7 == 1 ? "día " : "días") : "         ")
		extra = extra ($8 >= 0 ? sprintf("  mejor %dm%02ds", $8 / 60, $8 % 60) : "              ")
		out = out sprintf("  \033[1;%sm%s\033[0m %-16s %s  \033[2m%s\033[0m\n",
			color[$4], $4, $2, extra, $6)
	}
	END {
		printf "\033[1;36m📊 Progreso\033[0m  "
		printf "\033[32m✔ %d dominadas\033[0m · \033[33m⟳ %d por repasar\033[0m · ", total["✔"], total["⟳"]
		printf "\033[31m✘ %d con fallos\033[0m · · %d sin hacer\n", total["✘"], total["·"]
		printf "%s", out
	}'
}

# ¿Preparado para el examen? Estado de las funciones clave por categoría.
show_readiness() {
	function_stats | awk -F'\t' -v ready_days="$READY_DAYS" '
	$9 == "" { next }
	{
		if (!($9 in seen)) { seen[$9] = 1; order[++nc] = $9 }
		total++
		if ($10 == "lista") {
			ready++
			text = "sin pistas hace " ($11 == 0 ? "menos de 1 día" : $11 == 1 ? "1 día" : $11 " días")
			if ($8 >= 0) text = text sprintf(" · mejor %dm%02ds", $8 / 60, $8 % 60)
			line = sprintf("  \033[1;32m✔\033[0m %-16s \033[2m%s\033[0m", $2, text)
		} else {
			missing = missing " " $2
			if ($10 == "falla")
				line = sprintf("  \033[1;31m✘\033[0m %-16s falló el último test", $2)
			else if ($10 == "caducada")
				line = sprintf("  \033[1;33m⌛\033[0m %-16s sin pistas hace %d días: repásala", $2, $11)
			else
				line = sprintf("  \033[2m·\033[0m %-16s \033[2maún no la has resuelto sin pistas\033[0m", $2)
		}
		lines[$9] = lines[$9] line "\n"
	}
	END {
		if (ready == total)
			verdict = "\033[1;32m✅ Preparado\033[0m"
		else if (ready >= total * 0.75)
			verdict = "\033[1;33m🟡 Casi preparado\033[0m"
		else
			verdict = "\033[1;31m🔴 Todavía no\033[0m"
		printf "\033[1;36m🎯 Examen:\033[0m %s · %d/%d funciones clave listas\n", verdict, ready, total
		printf "\033[2mLista = resuelta sin pistas en los últimos %d días y sin fallos después.\033[0m\n", ready_days
		for (i = 1; i <= nc; i++)
			printf "\n\033[1;36m%s\033[0m\n%s", order[i], lines[order[i]]
		if (missing != "")
			printf "\nTe faltan:%s\nPara practicarlas: libft_43.sh examen\n", missing
	}'
}

# Página de man de la función original (Parte 1) o su ficha del subject
# (Partes 2 y 3). Se puede consultar en modo examen.
show_man() {
	local name="$1" orig="${1#ft_}" page

	if [[ " ${PART1[*]} " == *" $name|"* ]]; then
		# man 3 strlcpy da la página de AVR: entonces se usa la de libbsd.
		page=$(LC_ALL=C.UTF-8 man -w -s 3 "$orig" 2>/dev/null)
		[[ -z "$page" || "$page" == *avr* ]] \
			&& page=$(LC_ALL=C.UTF-8 man -w -s 3bsd "$orig" 2>/dev/null)
		if [ -n "$page" ]; then
			LC_ALL=C.UTF-8 MANWIDTH="${MANWIDTH:-80}" man -l "$page" 2>/dev/null | LC_ALL=C.UTF-8 col -bx
		else
			echo "No está instalada la página de man de $orig."
		fi
		case "$name" in
			ft_calloc)
				echo -e "\n\033[1;36m📜 Subject\033[0m"
				echo "Si nmemb o size es 0, entonces calloc() debe devolver un puntero"
				echo "único que pueda pasarse con éxito a free()." ;;
			ft_is*)
				echo -e "\n\033[1;36m📜 Subject\033[0m"
				echo "El valor de retorno debe ser 1 si el carácter cumple la condición"
				echo "comprobada y 0 si no la cumple." ;;
		esac
		return 0
	fi
	if [ ! -f "$SUBJECT_PDF" ] || ! command -v pdftotext > /dev/null; then
		# Sin el PDF: las citas del subject de la nota de la función.
		page=$(find_note "$name" 2> /dev/null) && {
			echo -e "\033[1;36m📜 Subject: $name\033[0m \033[2m(citado en tus notas;" \
				"pon SUBJECT_PDF en config.sh para ver la ficha original)\033[0m"
			show_note "$page" subject
			return 0
		}
		echo "No puedo leer el subject: pon su ruta en SUBJECT_PDF (config.sh)" \
			"e instala pdftotext."
		return 1
	fi
	echo -e "\033[1;36m📜 Subject: $name\033[0m"
	pdftotext -layout "$SUBJECT_PDF" - | awk -v n="$name" '
		$0 ~ "Nombre de fun- +" n "$" { p = 1 }
		p && /Nombre de fun-/ && $0 !~ n "$" { exit }
		p && /^\f?(Capítulo|IV\.)/ { exit }
		p && /^\f?Libft / { next }
		p && !/^ *[0-9]+ *$/ { print }' | cat -s
}

# ---------- espacio de trabajo: vim + menú en tmux ----------

TMUX_SESSION="libft43"

# Si en la sesión queda vim pero no el menú, vuelve a poner el menú a su
# derecha.
restore_menu() {
	local panes vim_pane

	panes=$(tmux list-panes -s -t "$TMUX_SESSION" -F '#{pane_id} #{pane_current_command}')
	grep -q ' python3$' <<< "$panes" && return
	vim_pane=$(awk '$2 ~ /^n?vim$/ { print $1; exit }' <<< "$panes")
	[ -z "$vim_pane" ] && return
	tmux split-window -h -l 45% -t "$vim_pane" -c "$PWD" \
		-e "LIBFT_VIM_PANE=$vim_pane" python3 "$SCRIPT_DIR/libft_tui.py"
	tmux select-pane -t "$vim_pane"
}

# Bordes de la ventana $1: cada panel con su título encima (lo pone el
# menú en @libft_title) y el que tiene el foco, en color.
style_window() {
	tmux set -w -t "$1" pane-border-status top
	# El color del panel activo (@libft_color) lo cambia el menú con la paleta.
	if [ -z "$(tmux show -wv -t "$1" @libft_color 2> /dev/null)" ]; then
		tmux set -w -t "$1" @libft_color cyan
		tmux set -w -t "$1" pane-active-border-style fg=cyan
	fi
	tmux set -w -t "$1" pane-border-format \
		'#{?pane_active,#[fg=black#,bg=#{@libft_color}#,bold] ▶ #{@libft_title} #[default],#[fg=colour244] #{@libft_title} }'
	tmux set -w -t "$1" pane-border-style fg=colour240
}

# Hooks de la sesión: pausa automática al desconectarse y vuelta al
# conectarse (auto_pause).
set_pause_hooks() {
	local cmd

	cmd=$(printf '%q' "$SCRIPT_DIR/libft_43.sh")
	tmux set-hook -t "$TMUX_SESSION" client-detached "run-shell -b '$cmd autopausa on'"
	tmux set-hook -t "$TMUX_SESSION" client-attached "run-shell -b '$cmd autopausa off'"
}

# Abre vim (izquierda) y el menú (derecha) en la misma ventana de tmux, con
# $1.c en vim si se indica. Si la sesión ya existe, vuelve a ella (con lo
# que tuvieras sin guardar). Sin tmux, abre solo el menú.
start_workspace() {
	local file="" vim_pane

	if ! command -v tmux > /dev/null; then
		echo "No está tmux: abro solo el menú."
		exec python3 "$SCRIPT_DIR/libft_tui.py"
	fi
	if [ -z "$TMUX" ] && tmux has-session -t "$TMUX_SESSION" 2> /dev/null; then
		restore_menu
		set_pause_hooks
		style_window "$TMUX_SESSION"
		exec tmux attach -t "$TMUX_SESSION"
	fi

	# Empieza por la función pedida o la última sugerida, si está aquí.
	[ -n "$1" ] && [ -f "${1%.c}.c" ] && file="${1%.c}.c"
	[ -z "$file" ] && [ -s "$LAST" ] && [ -f "$(cat "$LAST").c" ] && file="$(cat "$LAST").c"
	[ -z "$file" ] && file=$(find . -maxdepth 1 -name 'ft_*.c' -printf '%f\n' | sort | head -1)

	if [ -n "$TMUX" ]; then
		# Ya estás dentro de tmux: una ventana nueva en tu sesión.
		vim_pane=$(tmux new-window -n "$TMUX_SESSION" -c "$PWD" -P -F '#{pane_id}' \
			vim -S "$SCRIPT_DIR/libft_vim.vim" $file)
	else
		vim_pane=$(tmux new-session -d -s "$TMUX_SESSION" -c "$PWD" \
			-x "$(tput cols 2> /dev/null || echo 160)" \
			-y "$(tput lines 2> /dev/null || echo 45)" -P -F '#{pane_id}' \
			vim -S "$SCRIPT_DIR/libft_vim.vim" $file)
		tmux set -t "$TMUX_SESSION" mouse on
		tmux set -s focus-events on     # vim sabe cuándo pasas al menú
		set_pause_hooks
	fi
	tmux split-window -h -l 45% -t "$vim_pane" -c "$PWD" \
		-e "LIBFT_VIM_PANE=$vim_pane" python3 "$SCRIPT_DIR/libft_tui.py"
	style_window "$vim_pane"
	tmux select-pane -t "$vim_pane"
	[ -z "$TMUX" ] && exec tmux attach -t "$TMUX_SESSION"
}

# ---------- notas de Obsidian ----------

# Nombre de función a partir del argumento (con o sin ft_ y .c).
# Sin argumento: la última función sugerida o creada.
resolve_name() {
	local name="${1%.c}"

	if [ -z "$name" ]; then
		[ -s "$LAST" ] || { echo "Todavía no se ha sugerido ninguna función." >&2; return 1; }
		name=$(cat "$LAST")
	fi
	[[ "$name" == ft_* ]] || name="ft_$name"
	echo "$name"
}

# Ruta de la nota de Obsidian de una función.
find_note() {
	local note

	note=$(find "$NOTES_DIR" -name "$1.md" -print -quit 2>/dev/null)
	if [ -z "$note" ]; then
		echo -e "\033[1;31mNo hay nota de $1 en $NOTES_DIR\033[0m" >&2
		return 1
	fi
	echo "$note"
}

# Muestra una nota de Obsidian en la terminal, con colores. Modos:
#   tip: resumen y puntos clave · pseudo: cómo implementarla
#   full: la nota entera · casos: la sección $3 de la nota de casos límite
#   subject: prototipo y lo que dice el subject (vale en examen)
show_note() {
	awk -v mode="$2" -v fname="$3" '
	function plain(s,   m) {
		gsub(/<br>/, " ", s)
		while (match(s, /\[\[[^]|]*\|[^]]*\]\]/)) {
			m = substr(s, RSTART + 2, RLENGTH - 4)
			sub(/^[^|]*\|/, "", m)
			s = substr(s, 1, RSTART - 1) m substr(s, RSTART + RLENGTH)
		}
		while (match(s, /\[\[[^]]*\]\]/))
			s = substr(s, 1, RSTART - 1) substr(s, RSTART + 2, RLENGTH - 4) \
				substr(s, RSTART + RLENGTH)
		while (match(s, /\*\*[^*]+\*\*/))
			s = substr(s, 1, RSTART - 1) "\033[1m" \
				substr(s, RSTART + 2, RLENGTH - 4) "\033[22m" \
				substr(s, RSTART + RLENGTH)
		return s
	}
	# El texto entre comillas invertidas es código: se aparta antes de
	# dar formato al resto y se vuelve a poner en amarillo y sin tocar.
	function inline(s,   code, n, i, mark, at) {
		n = 0
		while (match(s, /`[^`]+`/)) {
			code[++n] = substr(s, RSTART + 1, RLENGTH - 2)
			s = substr(s, 1, RSTART - 1) "\001" n "\002" substr(s, RSTART + RLENGTH)
		}
		s = plain(s)
		for (i = 1; i <= n; i++) {
			mark = "\001" i "\002"
			at = index(s, mark)
			s = substr(s, 1, at - 1) "\033[33m" code[i] "\033[39m" \
				substr(s, at + length(mark))
		}
		return s
	}
	function emit(s) {
		if (mode == "full" || (mode == "casos" && incasos && !skip) \
			|| (mode == "tip" && (section == "resumen" || section ~ /^Puntos clave/)) \
			|| (mode == "pseudo" && section == "Cómo implementarla") \
			|| (mode == "subject" && section ~ /^(Prototipo|Requisitos del subject|Comportamiento según el subject)$/))
			print s
	}
	BEGIN {
		icon["tip"] = "💡"; icon["warning"] = "⚠ "; icon["danger"] = "⛔"
		icon["note"] = "📝"; icon["info"] = "ℹ "; icon["quote"] = "❝ "
		icon["question"] = "❓"; icon["example"] = "🧪"
		color["tip"] = 32; color["warning"] = 33; color["danger"] = 31
		color["question"] = 35
	}
	NR == 1 && /^---$/ { front = 1; next }
	front { if (/^---$/) front = 0; next }
	{
		line = $0
		quoted = sub(/^> ?/, "", line)
		if (!quoted) { type = ""; skip = 0 }
		bar = quoted ? "\033[" ((type in color) ? color[type] : 34) "m│\033[0m " : ""
	}
	line ~ /^```/ { code = !code; next }
	code { emit(bar "    \033[36m" line "\033[0m"); next }
	!quoted && mode == "casos" && line ~ /^##/ {
		incasos = (line == "### " fname)
		if (incasos)
			print "\033[1;36m🧪 Casos límite de " fname "\033[0m"
		next
	}
	!quoted && /^# / {
		section = "resumen"
		if (mode == "full") print "\033[1;36m" substr(line, 3) "\033[0m"
		next
	}
	!quoted && /^## / { section = substr(line, 4); emit("\n\033[1;36m── " section "\033[0m"); next }
	!quoted && /^### / { emit("\033[1m" substr(line, 5) "\033[0m"); next }
	quoted && match(line, /^\[![a-z]+\][-+]? ?/) {
		type = substr(line, 3, index(line, "]") - 3)
		if (mode == "casos" && type == "example") { skip = 1; next }
		c = (type in color) ? color[type] : 34
		emit("\033[1;" c "m" icon[type] " " inline(substr(line, RLENGTH + 1)) "\033[0m")
		next
	}
	section == "resumen" && line ~ /^\[\[/ { next }
	mode == "casos" && line ~ /^(Nota: |---$)/ { next }
	{ emit(bar inline(line)) }
	' "$1" | cat -s
}

# Cabecera de 42 para los archivos nuevos, para que pasen la norminette.
# Dibujo de la derecha de la cabecera: 7 líneas de 22 caracteres como máximo.
# No uses las secuencias de comentario de C (barra+asterisco) dentro del dibujo.
HEADER_ART=(
  "       :::      :::::::: "
  "      :+:     :+:   :+:"
  "    +:+            +:+ "
  "  +#  +#+        +#++:  "
  "+#+#+#+#+#         +#+"  
  "     +#+    #+#    +#+"  
  "     ###     ########   "
)

# $1: nombre del archivo. $2 y $3 (opcionales): fechas de Created y
# Updated (AAAA/MM/DD HH:MM:SS); por defecto, ahora.
header42() {
	local now by i
	local left=()
	now=$(date '+%Y/%m/%d %H:%M:%S')
	by="$USER <$MAIL42>"
	left=("" "$1" "" "By: $by" "" \
		"Created: ${2:-$now} by $USER" "Updated: ${3:-$now} by $USER")
	echo "/* ************************************************************************** */"
	echo "/*                                                                            */"
	for i in "${!left[@]}"; do
		printf "/*   %-48.48s%-25.25s*/\n" "${left[$i]}" "${HEADER_ART[$i]}"
	done
	echo "/*                                                                            */"
	echo "/* ************************************************************************** */"
}

# Une las líneas de un archivo separadas por « · ».
join_lines() {
	awk 'NR > 1 { printf " · " } { printf "%s", $0 }' "$1"
}

# Comprueba las reglas del subject que libftTester no mira y deja el
# resultado en SUBJ. Usa el .o y libft.a ya compilados en $2.
# Una regla del subject: $1 qué se comprueba, $2 el problema (vacío: bien).
subj_case() {
	if [ -z "$2" ]; then
		SUBJ_CASES+=("$(printf '      \033[32m✔\033[0m %s' "$1")")
	else
		SUBJ_CASES+=("$(printf '      \033[1;31m✘ %s\033[0m\033[31m: %s\033[0m' "$1" "$2")")
		SUBJ_BAD=1
	fi
}

# Reglas del subject que libftTester no mira. Deja cada una en SUBJ_CASES,
# el resumen en SUBJ y devuelve 1 si alguna falla.
check_subject() {
	local name="$1" build="$2" file="$1.c" obj="$2/$1.o"
	local bad sym check

	SUBJ_CASES=()
	SUBJ_BAD=0
	bad=""
	for sym in $(nm -u "$obj" | awk '{ print $NF }' | grep -v -e '^ft_' -e '^_'); do
		[[ " ${ALLOWED[$name]} " == *" $sym "* ]] || bad="$bad $sym"
	done
	subj_case "solo funciones autorizadas${ALLOWED[$name]:+ (${ALLOWED[$name]})}" \
		"${bad:+usa$bad}"

	bad=$(nm --defined-only "$obj" | awk -v n="$name" '$2 == "T" && $3 != n { printf " %s", $3 }')
	subj_case "funciones auxiliares con static" "${bad:+sin static:$bad}"

	bad=$(nm --defined-only "$obj" | awk '$2 ~ /^[BbCDdGgSs]$/ && $3 !~ /\./ { printf " %s", $3 }')
	subj_case "sin variables globales" "${bad:+hay$bad}"

	bad=""
	grep -qw restrict "$file" && bad="usa restrict"
	subj_case "sin restrict" "$bad"

	check="$build/subject_check"
	case "$name" in
		ft_isalpha|ft_isdigit|ft_isalnum|ft_isascii|ft_isprint)
			cat > "$check.c" <<'EOC'
#include <stdio.h>

int	FT(int c);

#define STR2(x) #x
#define STR(x) STR2(x)

int	main(void)
{
	int	c;
	int	r;
	int	bad;

	bad = 0;
	c = -1;
	while (c < 256 && bad < 3)
	{
		r = FT(c);
		if (r != 0 && r != 1)
		{
			printf("%s(%d) devuelve %d\n", STR(FT), c, r);
			bad++;
		}
		c++;
	}
	return (bad != 0);
}
EOC
			bad=""
			cc -DFT="$name" "$check.c" -L "$build" -lft -o "$check" \
				&& { "$check" > "$check.log" || bad=$(join_lines "$check.log"); }
			subj_case "devuelve 1 o 0 (de -1 a 255)" "$bad" ;;
		ft_calloc)
			cat > "$check.c" <<'EOC'
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

void	*ft_calloc(size_t nmemb, size_t size);

int	main(void)
{
	void	*p[3];
	int		bad;

	bad = 0;
	p[0] = ft_calloc(0, 0);
	p[1] = ft_calloc(0, 8);
	p[2] = ft_calloc(8, 0);
	if (!p[0] || !p[1] || !p[2])
	{
		printf("con nmemb o size 0 devuelve NULL, no un puntero liberable\n");
		bad = 1;
	}
	free(p[0]);
	free(p[1]);
	free(p[2]);
	p[0] = ft_calloc(SIZE_MAX / 2 + 2, 2);
	if (p[0])
	{
		printf("ft_calloc(SIZE_MAX / 2 + 2, 2) no devuelve NULL: "
			"falta controlar el desbordamiento de nmemb * size\n");
		bad = 1;
		free(p[0]);
	}
	return (bad);
}
EOC
			bad=""
			cc "$check.c" -L "$build" -lft -o "$check" \
				&& { valgrind -q --leak-check=full --error-exitcode=3 "$check" > "$check.log" 2>&1 \
				|| bad=$(join_lines "$check.log"); }
			subj_case "con 0 devuelve un puntero liberable y controla el desbordamiento" "$bad" ;;
	esac

	if [ "$SUBJ_BAD" -eq 0 ]; then
		SUBJ="subject OK"
		return 0
	fi
	SUBJ="subject KO"
	return 1
}

# Si hay un intento en marcha de $1: con $2 = 0 (test superado) guarda el
# tiempo en TIMING y cierra el intento; si no, solo dice cuánto llevas.
attempt_result() {
	local start hints exam paused elapsed

	TIMING=""
	read -r _ start hints exam paused <<< "$(attempt_get "$1")"
	[ -z "$start" ] && return
	elapsed=$(attempt_elapsed "$start" "$paused")
	if [ "$2" -ne 0 ]; then
		echo -e "\033[33m⏱ Llevas $(fmt_time $elapsed) con $1" \
			"$([ "${paused:-0}" -gt 0 ] && echo "(en pausa)")\033[0m"
		return
	fi
	TIMING="tiempo $(fmt_time $elapsed), $([ "$hints" = 1 ] && echo con || echo sin) pistas"
	[ "$exam" = 1 ] && TIMING="$TIMING, examen"
	attempt_del "$1"
	echo -e "\033[1;32m🏁 $1 resuelta en $(fmt_time $elapsed)" \
		"($([ "$hints" = 1 ] && echo con || echo sin) pistas$([ "$exam" = 1 ] && echo ", examen"))\033[0m"
}

# Compila libft.a con tu libft real, sustituyendo la función practicada,
# y ejecuta el test de libftTester correspondiente.
test_function() {
	local name="${1%.c}"
	local file="$name.c"
	local build ok ko segv status norm_status subj_status

	echo -e "\033[1;36m🧪 $name\033[0m"
	if [ ! -f "$file" ]; then
		echo -e "\033[1;31m$file no existe en $(pwd)\033[0m"
		add_summary "$name" "no existe" 1
		return 1
	fi
	if [ ! -f "$TESTER_DIR/tests/${name}_test.cpp" ]; then
		echo -e "\033[1;31mlibftTester no tiene test para $name\033[0m"
		add_summary "$name" "sin test" 1
		return 1
	fi

	step "norminette"
	check_norm "$file"
	norm_status=$?
	step_done "norminette" $norm_status "$([ "$NORM" = "norma no comprobada" ] && echo "no está instalada")"

	build=$(mktemp -d)
	cp "$LIBFT_DIR"/ft_*.c "$LIBFT_DIR/libft.h" "$build/"
	cp "$file" "$build/"
	step "compilar"
	(
		cd "$build" || exit 1
		for src in ft_*.c; do
			cc -Wall -Wextra -Werror -c "$src" -o "${src%.c}.o" || exit 2
		done
		ar rcs libft.a ft_*.o
		clang++ -g3 -ldl -gdwarf-4 -std=c++11 \
			-I "$TESTER_DIR/utils" -I "$build" \
			"$TESTER_DIR"/utils/{sigsegv,color,check,leaks}.cpp \
			"$TESTER_DIR/tests/${name}_test.cpp" \
			-L "$build" -lft -o a.out || exit 2
	)
	status=$?
	step_done "compilar" $status
	if [ $status -ne 0 ]; then
		rm -rf "$build"
		attempt_result "$name" 1
		add_summary "$name" "no compila, $NORM" 1 history
		return 1
	fi

	step "libftTester + valgrind"
	(cd "$build" && valgrind -q --leak-check=full --error-exitcode=3 ./a.out > out.log)
	status=$?

	# Quita los colores y cuenta los resultados de libftTester.
	sed 's/\x1b\[[0-9;]*m//g' "$build/out.log" > "$build/plain.log"
	ok=$(grep -oE '[0-9]+\.M?OK' "$build/plain.log" | wc -l)
	ko=$(grep -oE '[0-9]+\.M?KO|LEAKS\.KO' "$build/plain.log" | wc -l)
	segv=$(grep -c 'SIGSEGV' "$build/plain.log")
	local result="$ok OK, $ko KO"
	[ "$segv" -gt 0 ] && result="$result, SIGSEGV"
	[ $status -eq 3 ] && result="$result, errores de valgrind"
	[ "$ko" -eq 0 ] && [ "$segv" -eq 0 ] && [ $status -eq 0 ]
	step_done "libftTester + valgrind" $? "$result"
	show_cases "$TESTER_DIR/tests/${name}_test.cpp" "$build/plain.log"

	step "reglas del subject"
	check_subject "$name" "$build"
	subj_status=$?
	step_done "reglas del subject" $subj_status
	printf '%s\n' "${SUBJ_CASES[@]}"
	rm -rf "$build"

	TOTAL_OK=$((TOTAL_OK + ok))
	TOTAL_KO=$((TOTAL_KO + ko + segv))
	result="$result, $NORM, $SUBJ"

	if [ "$ko" -eq 0 ] && [ "$segv" -eq 0 ] && [ $status -eq 0 ] \
		&& [ $norm_status -eq 0 ] && [ $subj_status -eq 0 ]; then
		attempt_result "$name" 0
		[ -n "$TIMING" ] && result="$result, $TIMING"
		add_summary "$name" "$result" 0 history
		return 0
	fi
	attempt_result "$name" 1
	add_summary "$name" "$result" 1 history
	return 1
}

print_summary() {
	local line passed=0

	echo
	echo -e "\033[1;36m📋 Resumen\033[0m"
	for line in "${SUMMARY[@]}"; do
		echo -e "  $line"
		[[ "$line" == *"✔"* ]] && passed=$((passed + 1))
	done
	echo "  ----------------------------------------"
	echo -e "  Tests: \033[32m$TOTAL_OK OK\033[0m, \033[31m$TOTAL_KO KO\033[0m"
	echo "  Funciones perfectas: $passed/${#SUMMARY[@]}"
}

PART1=(
	"ft_isalpha|int ft_isalpha(int c);"
	"ft_isdigit|int ft_isdigit(int c);"
	"ft_isalnum|int ft_isalnum(int c);"
	"ft_isascii|int ft_isascii(int c);"
	"ft_isprint|int ft_isprint(int c);"
	"ft_strlen|size_t ft_strlen(const char *s);"
	"ft_memset|void *ft_memset(void *s, int c, size_t n);"
	"ft_bzero|void ft_bzero(void *s, size_t n);"
	"ft_memcpy|void *ft_memcpy(void *dest, const void *src, size_t n);"
	"ft_memmove|void *ft_memmove(void *dest, const void *src, size_t n);"
	"ft_strlcpy|size_t ft_strlcpy(char *dst, const char *src, size_t size);"
	"ft_strlcat|size_t ft_strlcat(char *dst, const char *src, size_t size);"
	"ft_toupper|int ft_toupper(int c);"
	"ft_tolower|int ft_tolower(int c);"
	"ft_strchr|char *ft_strchr(const char *s, int c);"
	"ft_strrchr|char *ft_strrchr(const char *s, int c);"
	"ft_strncmp|int ft_strncmp(const char *s1, const char *s2, size_t n);"
	"ft_memchr|void *ft_memchr(const void *s, int c, size_t n);"
	"ft_memcmp|int ft_memcmp(const void *s1, const void *s2, size_t n);"
	"ft_strnstr|char *ft_strnstr(const char *big, const char *little, size_t len);"
	"ft_atoi|int ft_atoi(const char *nptr);"
	"ft_calloc|void *ft_calloc(size_t nmemb, size_t size);"
	"ft_strdup|char *ft_strdup(const char *s);"
)

PART2=(
	"ft_substr|char *ft_substr(char const *s, unsigned int start, size_t len);"
	"ft_strjoin|char *ft_strjoin(char const *s1, char const *s2);"
	"ft_strtrim|char *ft_strtrim(char const *s1, char const *set);"
	"ft_split|char **ft_split(char const *s, char c);"
	"ft_itoa|char *ft_itoa(int n);"
	"ft_strmapi|char *ft_strmapi(char const *s, char (*f)(unsigned int, char));"
	"ft_striteri|void ft_striteri(char *s, void (*f)(unsigned int, char*));"
	"ft_putchar_fd|void ft_putchar_fd(char c, int fd);"
	"ft_putstr_fd|void ft_putstr_fd(char *s, int fd);"
	"ft_putendl_fd|void ft_putendl_fd(char *s, int fd);"
	"ft_putnbr_fd|void ft_putnbr_fd(int n, int fd);"
)

PART3=(
	"ft_lstnew|t_list *ft_lstnew(void *content);"
	"ft_lstadd_front|void ft_lstadd_front(t_list **lst, t_list *new);"
	"ft_lstsize|unsigned int ft_lstsize(t_list *lst);"
	"ft_lstlast|t_list *ft_lstlast(t_list *lst);"
	"ft_lstadd_back|void ft_lstadd_back(t_list **lst, t_list *new);"
	"ft_lstdelone|void ft_lstdelone(t_list *lst, void (*del)(void *));"
	"ft_lstclear|void ft_lstclear(t_list **lst, void (*del)(void *));"
	"ft_lstiter|void ft_lstiter(t_list *lst, void (*f)(void *));"
	"ft_lstmap|t_list *ft_lstmap(t_list *lst, void *(*f)(void *), void (*del)(void *));"
)

# Crea NAME.c con la cabecera y el prototipo PROTO y empieza a contar el
# tiempo del intento ($3 = 1: en modo examen). Si ya existe y tiene código,
# lo guarda antes en intentos/ para que empieces desde cero.
create_file() {
	local file="$1.c" definition body saved others

	# La norma pide un tabulador entre el tipo de retorno y el nombre.
	[[ "${2%;}" =~ ^(.*[^\ *])\ (\**ft_.*)$ ]]
	definition="${BASH_REMATCH[1]}"$'\t'"${BASH_REMATCH[2]}"
	body=$(printf '#include "libft.h"\n\n%s\n{\n\n}' "$definition")

	if [ -e "$file" ] && [ "$(tail -n +13 "$file")" != "$body" ]; then
		mkdir -p "$ARCHIVE_DIR"
		saved="$ARCHIVE_DIR/$1_$(date '+%Y%m%d-%H%M%S').c"
		mv "$file" "$saved"
		echo -e "Intento anterior guardado en \033[1;35m$saved\033[0m"
	fi
	{ header42 "$file"; echo; echo "$body"; } > "$file"
	# Un solo cronómetro: el intento nuevo cancela el que hubiera.
	others=$(awk -v n="$1" '$1 != n { printf " %s", $1 }' "$ATTEMPTS")
	[ -n "$others" ] && echo -e "\033[2m⏹ Cronómetro cancelado:$others\033[0m"
	: > "$ATTEMPTS"
	rm -f "$AUTOPAUSE"
	attempt_set "$1" "$(date +%s)" 0 "${3:-0}"
	echo "$1" > "$LAST"
	echo -e "Creado: \033[1;35m$file\033[0m (el tiempo empieza a contar)"
}

# Rehace la cabecera de un archivo con el «43» de HEADER_ART, conservando
# sus fechas. El plugin de cabecera de 42 de vim reescribe al guardar las
# líneas del nombre y de Updated con el logo de 42; esto lo deja como nuevo.
# Solo toca archivos de práctica: los que llevan el «43» en la línea 5, que
# el plugin no reescribe. Las cabeceras de 42 de tus proyectos no cambian.
fix_header() {
	local file="$1" created updated fixed art

	if ! sed -n 1p "$file" | grep -q '^/\* \*\{74\} \*/$' \
		|| ! created=$(sed -n 8p "$file" | grep -oE 'Created: [0-9/]+ [0-9:]+'); then
		echo -e "\033[33m$file no tiene cabecera de 42: no se toca.\033[0m"
		return 1
	fi
	art="${HEADER_ART[2]}"
	art="${art#"${art%%[! ]*}"}"
	if ! sed -n 5p "$file" | grep -qF "${art%"${art##*[! ]}"}"; then
		echo -e "\033[33m$file tiene la cabecera de 42 de un proyecto: no se toca.\033[0m"
		return 1
	fi
	updated=$(sed -n 9p "$file" | grep -oE 'Updated: [0-9/]+ [0-9:]+')
	fixed=$({ header42 "$file" "${created#Created: }" "${updated#Updated: }"; tail -n +12 "$file"; })
	if [ "$fixed" = "$(cat "$file")" ]; then
		echo "$file: la cabecera ya está bien."
		return 0
	fi
	printf '%s\n' "$fixed" > "$file"
	echo -e "\033[32m$file: cabecera arreglada.\033[0m"
}

# Busca el prototipo de una función.
find_proto() {
	local entry

	for entry in "${PART1[@]}" "${PART2[@]}" "${PART3[@]}"; do
		[ "${entry%%|*}" = "$1" ] && { echo "${entry#*|}"; return 0; }
	done
	return 1
}

# Sugiere una función ($1: parte o vacío; $2 = 1: modo examen).
suggest() {
	local label="Todas" pick name count state why

	[ -n "$1" ] && label="Parte $1"
	pick=$(pick_function "$1" "$2")
	IFS=$'\t' read -r _ name count state _ why _ <<< "$pick"
	count=$((count + 1))
	grep -v "^$name " "$COUNTS" > "$COUNTS.tmp"
	echo "$name $count" >> "$COUNTS.tmp"
	mv "$COUNTS.tmp" "$COUNTS"
	[ "$state" = "✔" ] && why="ya la dominas, repaso extra ($why)"

	if [ "$2" = 1 ]; then
		echo -e "\033[1;31m📝 Examen ($label)\033[0m"
	else
		echo -e "\033[1;36m🎲 Libft ($label)\033[0m"
	fi
	echo -e "Hoy toca: \033[1;32m$name\033[0m"
	echo -e "Prototipo: \033[0;33m$(find_proto "$name")\033[0m"
	echo "Motivo: $why · sugerida $count $([ "$count" = 1 ] && echo vez || echo veces)"
	create_file "$name" "$(find_proto "$name")" "$2"
	if [ "$2" = 1 ]; then
		echo -e "\033[1;31mSin pistas hasta que pase el test (man sí:" \
			"$(basename "$0") man). Para abandonar: $(basename "$0") rendirse\033[0m"
	else
		echo -e "Pista: \033[1m$(basename "$0") tip\033[0m muestra los puntos clave."
	fi
}

case "$1" in
	""|1|2|3) suggest "$1" ;;
	examen)
		name=$(exam_name)
		if [ -n "$name" ]; then
			read -r _ start _ _ paused <<< "$(attempt_get "$name")"
			echo -e "\033[1;31m📝 Examen en marcha: $name\033[0m," \
				"llevas $(fmt_time "$(attempt_elapsed "$start" "$paused")")."
			echo "Para abandonarlo: $(basename "$0") rendirse"
			exit 0
		fi
		[[ "$2" =~ ^[123]?$ ]] || { echo "Uso: $0 examen [1|2|3]"; exit 1; }
		suggest "$2" 1 ;;
	rendirse)
		name=$(exam_name)
		[ -z "$name" ] && { echo "No hay ningún examen en marcha."; exit 0; }
		read -r _ start _ _ paused <<< "$(attempt_get "$name")"
		attempt_set "$name" "$start" 1 0 "${paused:-0}"
		echo "Examen de $name abandonado: ya puedes ver las pistas."
		echo "El tiempo sigue contando y el intento contará como con pistas." ;;
	pausa)
		name=$(resolve_name "$2") || exit 1
		rm -f "$AUTOPAUSE"      # una pausa tuya manda sobre la automática
		attempt_pause "$name" ;;
	autopausa) auto_pause "$2" ;;    # desde los hooks de tmux
	cancelar)
		name=$(resolve_name "$2") || exit 1
		read -r _ start _ exam _ <<< "$(attempt_get "$name")"
		[ -z "$start" ] && { echo "$name no tiene el cronómetro en marcha."; exit 0; }
		attempt_del "$name"
		echo "⏹ Cronómetro de $name cancelado$([ "$exam" = 1 ] && echo " (y el examen)"):" \
			"el tiempo no se guarda."
		echo "$name.c sigue en su sitio. El cronómetro vuelve con el próximo intento." ;;
	reset) rm -f "$COUNTS"; echo "Contador de sugerencias a cero." ;;
	help|-h|--help) cat "$SCRIPT_DIR/docs/manual.md" ;;
	test)
		check_setup test || exit 1
		shift
		[ $# -eq 0 ] && set -- ft_*.c
		[ "$1" = "ft_*.c" ] && { echo "No hay ft_*.c en $(pwd)"; exit 1; }
		failed=0
		for fn in "$@"; do
			test_function "$fn" || failed=1
		done
		print_summary
		exit $failed ;;
	historial) show_history "$2" ;;
	new)
		# Crea el archivo de una función concreta, sin contar como sugerencia.
		[ -z "$2" ] && { echo "Uso: $0 new ft_xxx"; exit 1; }
		name=$(resolve_name "$2")
		proto=$(find_proto "$name") \
			|| { echo -e "\033[1;31m$name no es una función de la libft\033[0m"; exit 1; }
		echo -e "Prototipo: \033[0;33m$proto\033[0m"
		create_file "$name" "$proto" ;;
	lista)
		# Una línea por función: parte, nombre, veces sugerida y estado.
		# Una línea por función: parte, nombre, veces sugerida, estado y
		# preparación para el examen (- si no es clave).
		function_stats | awk -F'\t' '{ print $1, $2, $3, $4, $10 }' ;;
	progreso) show_progress ;;
	datos)
		# Para el menú: una línea por función, separada por tabuladores:
		# parte nombre veces estado preparación mejor_tiempo categoría prototipo
		for entry in "${PART1[@]}" "${PART2[@]}" "${PART3[@]}"; do
			printf '%s\t%s\n' "${entry%%|*}" "${entry#*|}"
		done | awk -F'\t' -v OFS='\t' '
			NR == FNR { proto[$1] = $2; next }
			{ print $1, $2, $3, $4, $10, $8, $9, proto[$2] }' - <(function_stats) ;;
	cabecera)
		# Arregla la cabecera de los archivos (sin nombres: todos los ft_*.c).
		shift
		[ $# -eq 0 ] && set -- ft_*.c
		[ "$1" = "ft_*.c" ] && { echo "No hay ft_*.c en $(pwd)"; exit 1; }
		for fn in "$@"; do
			fn="$(resolve_name "$fn").c"
			if [ -f "$fn" ]; then
				fix_header "$fn"
			else
				echo "$fn no existe."
			fi
		done ;;
	preparado) show_readiness ;;
	man)
		name=$(resolve_name "$2") || exit 1
		find_proto "$name" > /dev/null \
			|| { echo -e "\033[1;31m$name no es una función de la libft\033[0m"; exit 1; }
		show_man "$name" ;;
	intentos)
		if [ -z "$2" ]; then
			show_attempts
			exit 0
		fi
		name=$(resolve_name "$2")
		if ! ls "$ARCHIVE_DIR/${name}"_*.c > /dev/null 2>&1; then
			echo "No hay versiones guardadas de $name en $(pwd)/$ARCHIVE_DIR."
			exit 0
		fi
		echo -e "\033[1;36m🗂 Versiones de $name\033[0m"
		ls -1 "$ARCHIVE_DIR/${name}"_*.c
		echo "Para compararlas: diff <versión> $name.c" ;;
	tip|nota|casos|obsidian)
		# Pistas de tus notas de Obsidian (bloqueadas en modo examen).
		level=1
		if [[ "$2" =~ ^[12]$ ]]; then level="$2"; arg="$3"; else arg="$2"; level="${3:-1}"; fi
		name=$(resolve_name "$arg") || exit 1
		use_hint "$name" || exit 1
		if [ "$1" = casos ]; then
			[ -f "$EDGE_NOTE" ] || { echo "No encuentro $EDGE_NOTE"; exit 1; }
			show_note "$EDGE_NOTE" casos "$name"
			exit 0
		fi
		note=$(find_note "$name") || exit 1
		case "$1" in
			tip)
				if [ "$level" = 2 ]; then
					echo -e "\033[1;36m🧩 Cómo implementar $name\033[0m"
					show_note "$note" pseudo
				else
					echo -e "\033[1;36m💡 Puntos clave de $name\033[0m"
					show_note "$note" tip
					echo -e "\n\033[2mPseudocódigo: $(basename "$0") tip $name 2" \
						"(en el menú, i otra vez)\033[0m"
				fi ;;
			nota) show_note "$note" full ;;
			obsidian)
				url="obsidian://open?path=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))' "$note")"
				xdg-open "$url" > /dev/null 2>&1 &
				echo "Abriendo $name en Obsidian…" ;;
		esac ;;
	tui) check_setup && exec python3 "$SCRIPT_DIR/libft_tui.py" ;;
	menu) check_setup && start_workspace "$2" ;;
	*) echo "Orden desconocida: $1 (mira $0 help)"; exit 1 ;;
esac
