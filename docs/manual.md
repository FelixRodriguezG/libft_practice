# Manual de libft_43

Este es el manual completo (`./libft_43.sh help`). Para instalarlo y
empezar, mira el [README](../README.md).

Script para practicar la libft: te sugiere una función (dando prioridad a
las que fallas o no has hecho), te crea el archivo con el prototipo, mide
cuánto tardas en resolverla y la testea con libftTester y con las reglas
del subject. Las pistas salen de tus notas de Obsidian.

## Uso rápido

```bash
./libft_43.sh menu             # vim y el menú juntos en tmux (recomendado)
./libft_43.sh tui              # solo el menú
./libft_43.sh [1|2|3]          # sugiere una función (de una parte o de todas)
./libft_43.sh examen [1|2|3]   # una función clave, sin pistas hasta resolverla
./libft_43.sh preparado        # ¿estás listo para el examen?
./libft_43.sh man [ft_xxx]     # man de la original o ficha del subject
./libft_43.sh rendirse         # abandona el examen
./libft_43.sh pausa [ft_xxx]   # pausa el cronómetro (otra vez: sigue)
./libft_43.sh cancelar [ft_xxx] # quita el cronómetro sin guardar el tiempo
./libft_43.sh new ft_xxx       # crea el archivo de una función concreta
./libft_43.sh test [ft_xxx…]   # testea (sin nombres: todos los ft_*.c)
./libft_43.sh tip [ft_xxx]     # puntos clave (sin nombre: la última sugerida)
./libft_43.sh tip [ft_xxx] 2   # el pseudocódigo
./libft_43.sh casos [ft_xxx]   # casos límite que debes probar
./libft_43.sh nota [ft_xxx]    # la nota de Obsidian entera
./libft_43.sh obsidian [ft_xxx]  # abre la nota en Obsidian
./libft_43.sh progreso         # estado de las 43 funciones
./libft_43.sh modos            # cómo funciona cada modo y qué cuenta para qué
./libft_43.sh intentos [ft_xxx]  # intentos en marcha / versiones guardadas
./libft_43.sh historial [ft_xxx] # resultados de tests anteriores
./libft_43.sh cabecera [ft_xxx…] # rehace la cabecera con el «43» (sin nombres: todas)
./libft_43.sh lista            # parte, nombre, veces sugerida y estado
./libft_43.sh reset            # pone a cero las veces que ha salido cada función
./libft_43.sh reset todo       # borra todo el progreso y empiezas desde cero
./libft_43.sh help             # esta ayuda (también -h o --help)
```

Donde se pide un nombre vale `ft_memmove`, `memmove` o `ft_memmove.c`.

## Vim y el menú juntos

```bash
./libft_43.sh menu
```

Abre una sesión de tmux (`libft43`) con dos paneles en la misma ventana:
**vim a la izquierda** y **el menú a la derecha**. Usa la carpeta desde la
que lo lanzas, igual que el script.

- Vim es el tuyo, con tu `.vimrc` (y el plugin de la cabecera de 42). Se
  abre con la última función sugerida, si está en la carpeta.
- En el menú, **⏎ abre el archivo seleccionado en vim** (y `t` lo testea).
  Si has salido de vim (`:q`), ⏎ lo vuelve a abrir a la izquierda.
- Si has abierto el menú solo (`./libft_43.sh tui` o `./libft_tui.py`), ⏎
  también abre vim: dentro de tmux, en un panel a la izquierda; fuera, el
  menú se cambia por vim y el menú juntos. Si la sesión `libft43` sigue
  abierta (por ejemplo, porque cerraste la ventana), el menú te avisa y ⏎
  te devuelve a ella, con lo que tuvieras sin guardar en vim. Si en esa
  sesión falta el menú, vuelve a aparecer al lado de vim.
- Al sugerir (`r`, `1` `2` `3`), crear (`n`) o empezar un examen (`E`), el
  archivo nuevo se abre solo en vim, listo para escribir.
- Atajos que solo existen en esta sesión de vim (`libft_vim.vim`; tu
  `.vimrc` no cambia):

| Tecla en vim | Acción |
|--------------|--------|
| `F5` | Guarda y testea el archivo en el menú |
| `F6` | Tip de la función (`F6` otra vez: el pseudocódigo) |
| `F7` | Man de la función original (o su ficha del subject) |

- Para cambiar de panel: `Ctrl-b` y una flecha, o un clic (el ratón está
  activado en esta sesión). Con la rueda se desplaza la salida.
- **Dónde está el foco:** cada panel lleva su título encima; el que tiene el
  foco va en color y con ▶. Además, la barra `/* libft · 43 */` del menú va
  en color con el foco en el menú y se apaga («foco en vim») si no. El
  panel sin foco se oscurece: el menú se atenúa y vim pierde los colores de
  sintaxis y pone el texto en gris (vuelve todo al darle el foco).
- **Paleta de colores:** `C` en el menú pasa por 42 (cian), ámbar y
  violeta. Cambia el acento, el «43» y el borde del panel activo; el verde
  de ✔ y el rojo de ✘ no cambian. Se recuerda para la próxima vez.
- **Colores de la salida:** los nombres de función van en blanco, las
  etiquetas del principio de línea (`Motivo:`, `Te faltan:`) en el color de
  acento, los comandos (`libft_43.sh examen`) en el secundario de la paleta
  y lo secundario atenuado. El resto usa el color de tu terminal.
- **El test, desde vim:** el título de vim muestra el test en marcha
  (`vim · ⏳ test ft_strlen · libftTester · 4s`) y luego su resultado
  (`vim · ✔ test ft_strlen: todo OK`), así que con F5 no hace falta cambiar
  de panel.
- Para seleccionar y copiar texto (por ejemplo, un error del compilador):
  **Mayús + arrastrar**, porque tmux se queda con el ratón.
- **Vim guarda solo**: tras 3 segundos sin escribir, al cambiar de archivo
  y al pasar al menú. Si cierras la ventana sin querer, no pierdes nada. No
  guarda encima de un archivo que haya cambiado fuera de vim (por ejemplo,
  si el script lo acaba de crear de nuevo). Con el auto-test (`a`), cada
  autoguardado lanza un test.
- Si cierras la ventana o sales de tmux con `Ctrl-b d`, la sesión sigue
  abierta y **el cronómetro se pausa solo**: `./libft_43.sh menu` te
  devuelve a ella y el cronómetro sigue donde estaba. Si lo habías pausado
  tú, sigue en pausa.
- Para cerrarla del todo: **`Q` en el menú** guarda lo de vim y cierra vim
  y el menú a la vez (el cronómetro se pausa hasta que vuelvas). También
  vale `:qa` en vim y `q` en el menú, o `tmux kill-session -t libft43`.
- Si ya estás dentro de tmux, se abre en una ventana nueva de tu sesión.
- Sin tmux instalado, `menu` abre solo el menú.

Cuando el panel es estrecho, el menú pone la lista de archivos encima de
la salida en vez de al lado.

## Menú interactivo

```bash
./libft_43.sh tui        # solo el menú (o: python3 libft_tui.py)
```

Ábrelo en una ventana (o un panel de tmux) y trabaja en otra: no hace falta
volver a lanzar el script. Con `./libft_43.sh menu` sale junto a vim.

**No hace falta aprenderse las teclas:**

- La **barra de abajo** enseña solo las 4 o 5 teclas útiles en cada momento
  (sin archivos, con uno seleccionado, durante un examen…).
- **Espacio** abre el menú de acciones: todas, agrupadas, con una frase que
  explica cada una. Se elige con ↑↓ y ⏎, o con su tecla rápida, que sale al
  lado para que la vayas aprendiendo.
- **?** abre la ayuda: las teclas por grupos y qué significa cada símbolo.
- Mientras la salida está vacía, muestra los primeros pasos.

**Qué hay en pantalla:**

- Arriba, la barra de título: `/* libft · 43 */`, el examen en marcha con su
  tiempo, 🎯 cuántas funciones clave tienes listas y si el auto-test está
  activado. A pantalla completa, además, el «43» con tu progreso al lado.
- **Tus archivos**: los `ft_*.c` con su último resultado resumido (✔ todo OK
  o lo que falló), o el cronómetro si hay un intento en marcha (⏱, o 📝 en
  examen). Un ● amarillo indica que el archivo ha cambiado desde su último
  test.
- **La ficha** de la función seleccionada: prototipo, el intento en marcha
  o el último resultado completo, si es clave para el examen (★) y su
  estado, y tu mejor tiempo.
- **Salida**: lo que devuelven los comandos. Las notas, el man y el
  progreso se muestran desde el principio; los tests, desde el final. Si
  subes para leer, lo que va llegando no te mueve el texto: se cuenta como
  «↓ N más» y `Fin` te lleva al final.

Con la variable `NO_COLOR` (`NO_COLOR=1 ./libft_43.sh tui`) no usa colores;
el estado se sigue viendo por los símbolos, la negrita y la selección en
vídeo inverso.

| Grupo | Tecla | Acción |
|-------|-------|--------|
| Practicar | `r` / `1` `2` `3` | Sugerir una función (todas o de una parte) |
| | `n` | Elegir una función: escribe para filtrar, ⏎ la crea, Tab muestra su pista |
| | `E` | Empezar un examen; con uno en marcha, rendirse (pide confirmación) |
| Con la función seleccionada | `⏎` | Abrirla en vim (si vim no está abierto, lo abre) |
| | `t` | Testearla |
| | `m` | Man de la original o ficha del subject (permitido en examen) |
| | `i` | Pista; `i` otra vez: el pseudocódigo |
| | `e` | Casos límite |
| | `o` / `O` | Nota completa / abrirla en Obsidian |
| | `h` / `v` | Su historial / sus versiones guardadas |
| | `z` | Pausar el cronómetro de su intento; `z` otra vez: sigue contando |
| | `x` | Cancelar su cronómetro sin guardar el tiempo (pide confirmación) |
| Probar | `T` | Testear todos los `ft_*.c` |
| | `a` | Auto-test: cada vez que guardas se testea solo y te avisa en el escritorio |
| | `s` | Parar el test en marcha |
| Ver | `P` | ¿Preparado para el examen? |
| | `M` | Modos de resolución: práctica, examen y sin cronómetro |
| | `p` / `H` | Progreso de las 43 / historial completo |
| Menú | `c` / `0` | Limpiar la salida / poner a cero las sugerencias (pide confirmación) |
| | `R` | Empezar desde cero: borra todo el progreso (pide confirmación) |
| | `C` | Cambiar la paleta de colores: 42, ámbar, violeta |
| | `q` / `Q` | Salir del menú / cerrar vim y el menú a la vez (guarda lo de vim) |
| | `espacio` / `?` | Acciones / ayuda |
| Moverse | `↑↓` `jk` | Elegir archivo |
| | `RePág` `AvPág` `Inicio` `Fin` | Desplazar la salida |
| | `↑↓` `jk` con una nota larga | Desplazar la nota (pista, man, nota, progreso…) línea a línea; `Esc` devuelve las flechas a los archivos |

Solo necesita Python 3 (usa `curses`, que viene incluido). El aviso del
auto-test usa `notify-send`; si no está, solo suena un pitido cuando falla.

## Partes

| Parte | Contenido | Ejemplos |
|-------|-----------|----------|
| 1 | Funciones de libc | `ft_strlen`, `ft_memmove`, `ft_atoi`, `ft_calloc` |
| 2 | Funciones adicionales | `ft_split`, `ft_itoa`, `ft_strtrim`, `ft_putnbr_fd` |
| 3 | Listas | `ft_lstnew`, `ft_lstadd_back`, `ft_lstmap` |

Las tres partes son obligatorias (no hay bonus).

## Sugerir una función

```bash
./libft_43.sh [1|2|3]
```

```
🎲 Libft (Todas)
Hoy toca: ft_putnbr_fd
Prototipo: void ft_putnbr_fd(int n, int fd);
Motivo: nunca la has hecho · sugerida 1 vez
Creado: ft_putnbr_fd.c (el tiempo empieza a contar)
Pista: libft_43.sh tip muestra los puntos clave.
```

### Cómo elige la función

No es un sorteo uniforme: según tu historial, cada función tiene un peso.

| Estado | Peso | Cuándo |
|--------|------|--------|
| ✘ con fallos | 8 | Su último test falló |
| · sin hacer | 5 | Nunca la has testeado (3 si ya salió y no la testeaste) |
| ⟳ por repasar | 4 | La dominas, pero ya toca repasarla |
| ✔ dominada | 1 | Aún no toca repasarla (puede salir, pero poco) |

Las funciones clave del examen que aún no tienes listas suman 2 al peso.
La última función sugerida no repite seguida.

Para el repaso se usa **repetición espaciada**: cada día distinto en que
la resuelves bien seguido, el siguiente repaso se aleja: 1, 3, 7, 14, 30 y
60 días. Si un test falla, la cuenta vuelve a empezar.

Ya no hay límite de sugerencias. El contador (`.libft_counts`) se usa
para que las funciones que nunca han salido salgan más que las que salieron
y no testeaste; `reset` lo pone a cero.

### El archivo

Crea `ft_xxx.c` en la carpeta actual, listo para empezar, con la cabecera
de 42 y un tabulador entre el tipo y el nombre (como pide la norma):

```c
/* ************************************************************************** */
/*                                                                            */
/*                                                          :::      :::::::: */
/*   ft_putnbr_fd.c                                        :+:     :+:   :+:  */
/*                                                       +:+            +:+   */
/*   By: felixrod <felixrod@student.42barcelona.com>   +#  +#+        +#++:   */
/*                                                   +#+#+#+#+#         +#+   */
/*   Created: 2026/10/20 04:22:58 by felixrod             +#+    #+#    +#+   */
/*   Updated: 2026/10/20 04:22:58 by felixrod             ###     ########    */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	ft_putnbr_fd(int n, int fd)
{

}
```

**Siempre empiezas desde cero.** Si el archivo ya existe y tiene código, el
intento anterior se guarda en `intentos/ft_xxx_AAAAMMDD-HHMMSS.c` y se crea
uno vacío. Si solo tenía la plantilla, se sustituye sin guardarlo.

El email de la cabecera es `$USER@student.42barcelona.com`; se cambia en
`MAIL42`, al principio del script.

En lugar del logo de 42, la cabecera lleva un «43» en ASCII (el mismo que
sale en el menú). Para cambiar el dibujo, edita `HEADER_ART` en el script:
7 líneas de 22 caracteres como máximo. No uses las secuencias de comentario
de C (barra seguida de asterisco o asterisco seguido de barra), porque
romperían la compilación.

Esta cabecera con el «43» la escribe el propio script y **solo aparece en los
archivos de práctica que genera**. No cambia la configuración de tu editor:
el plugin de cabecera de 42 (`:Stdheader` o F1 en vim) sigue igual y en el
resto de proyectos la cabecera sale con el logo de 42 de siempre.

El plugin de cabecera de 42 de vim reescribe al guardar las líneas del
nombre y de `Updated:` con el logo de 42, y la cabecera queda mezclada:

- En la sesión de `./libft_43.sh menu` no pasa: `libft_vim.vim` las vuelve a
  escribir con el «43» justo después del plugin (y `Updated:` se actualiza).
- Si guardas con vim fuera de esa sesión, `./libft_43.sh cabecera` las
  arregla, conservando las fechas de `Created:` y `Updated:` y sin tocar el
  código. Los archivos sin cabecera de 42 no se tocan.

La norminette acepta las dos versiones; solo cambia cómo se ve.

## Modos de resolución

| Modo | Cómo se empieza | Pistas | Si pasa, cuenta para |
|------|-----------------|--------|----------------------|
| ⏱ Práctica | `r`, `1` `2` `3`, `n` | Sí, pero el intento queda «con pistas» | Sin pistas: progreso y «¿Preparado?». Con pistas: solo progreso |
| 📝 Examen | `E` | No hasta que pase (el man sí) | Progreso y «¿Preparado?» |
| · Sin cronómetro | `t` sin intento en marcha | Sí | Solo progreso (no se sabe si usaste pistas) |

La ficha de la función seleccionada dice siempre en qué modo estás y qué
contará si el test pasa ahora (por ejemplo, `Práctica sin pistas · si pasa,
cuenta para «¿Preparado?»`). `M` en el menú (o `./libft_43.sh modos`) lo
explica entero.

## Tiempo de resolución

Cada archivo creado por el script (al sugerir, con `new` o en examen) empieza
un **intento** y pone el cronómetro en marcha. La primera vez que su test
sale perfecto, el tiempo se guarda en el historial, junto con si usaste
pistas (`tip`, `casos`, `nota` u `obsidian` durante el intento):

```
2026-10-20 18:40  ✔ ft_memmove   4 OK, 0 KO, norma OK, subject OK, tiempo 12m30s, sin pistas
```

Mientras no pase, cada test te dice cuánto llevas. El tiempo es de reloj
(desde que se creó el archivo), salvo cuando lo pausas o cuando cierras la
ventana de `./libft_43.sh menu`, que lo pausa solo hasta que vuelves. Los
archivos que no ha creado el script no cronometran.

**Solo hay un cronómetro a la vez**: al empezar un intento nuevo (`r`, `n`,
`E`), el que hubiera en marcha se cancela.

Si vas a parar un rato, **pausa el cronómetro** (`z` en el menú) y vuelve a
pulsar `z` para seguir: el tiempo final no cuenta la pausa. Si no vas a
terminar la función, **cancela el cronómetro** (`x`): se para y desaparece,
no se guarda ningún tiempo y el archivo se queda como está. Vuelve con el
próximo intento.

```bash
./libft_43.sh pausa memset      # pausa el intento (otra vez: sigue)
./libft_43.sh cancelar memset   # lo quita sin guardar el tiempo
./libft_43.sh intentos          # intentos en marcha y versiones guardadas
./libft_43.sh intentos memmove  # versiones guardadas de una función
```

## Modo examen

```bash
./libft_43.sh examen [1|2|3]
```

Elige una de las **funciones clave** (ver abajo), primero las que no tienes
listas: con fallos, luego pendientes y luego caducadas. Hasta que su test
salga perfecto, `tip`, `casos`, `nota` y `obsidian` están bloqueados para
esa función. El **man sí está permitido**, como en el examen real. Solo
puede haber un examen a la vez; `examen` con uno en marcha te dice cuánto
llevas.

Si te atascas, `./libft_43.sh rendirse` vuelve a permitir las pistas.
El tiempo sigue contando y el intento cuenta como con pistas.

## ¿Preparado para el examen?

```bash
./libft_43.sh preparado
```

Para estar preparado no hace falta repetir las 43 funciones, solo las
**funciones clave**: las más complejas y representativas de cada categoría.

| Categoría | Funciones clave |
|-----------|-----------------|
| Caracteres | `ft_isalnum` |
| Memoria | `ft_memmove` |
| Cadenas | `ft_strlcat`, `ft_strnstr` |
| Conversión | `ft_atoi`, `ft_itoa` |
| Memoria dinámica | `ft_calloc` |
| Cadenas nuevas | `ft_split`, `ft_strtrim`, `ft_substr` |
| Punteros a función | `ft_strmapi` |
| Escritura en fd | `ft_putnbr_fd` |
| Listas | las 9 |

Una función clave está **lista** (✔) si la has resuelto desde cero **sin
pistas** (o en examen) en los últimos 14 días y no ha fallado ningún test
después. Si no:

- ✘ su último test falló;
- ⌛ caducada: la resolviste sin pistas hace más de 14 días;
- · pendiente: aún no la has resuelto sin pistas. Las funciones que hiciste
  antes de que existiera el cronómetro cuentan como pendientes.

El veredicto es ✅ preparado (todas listas), 🟡 casi (al menos el 75 %) o
🔴 todavía no. Para cambiar las funciones clave o los días, edita
`EXAM_SET` y `READY_DAYS` al principio del script.

## Man y subject

```bash
./libft_43.sh man memmove   # man 3 memmove
./libft_43.sh man split     # la ficha de ft_split del subject
```

- Parte 1: la página de man de la función original (`memmove`, o `malloc`
  para `calloc`). Para `strlcpy`, `strlcat` y `strnstr` usa la de libbsd.
  En `ft_calloc` y `ft_is*` añade la regla del subject.
- Partes 2 y 3: no tienen man, así que muestra su ficha del subject
  (prototipo, parámetros, valor devuelto, funciones autorizadas y
  descripción), sacada del PDF (`SUBJECT_PDF` en `config.sh`, necesita
  `pdftotext`). Sin el PDF, muestra el prototipo y las citas del subject
  que hay en la nota de la función.

Se puede consultar en modo examen y no cuenta como pista.

## Pistas de tus notas de Obsidian

```bash
./libft_43.sh tip memmove      # nivel 1: resumen y puntos clave
./libft_43.sh tip memmove 2    # nivel 2: cómo implementarla (pseudocódigo)
./libft_43.sh casos memmove    # casos límite que tienes que probar
./libft_43.sh nota memmove     # la nota entera
./libft_43.sh obsidian memmove # la abre en Obsidian
```

Lee las notas de `NOTES_DIR` (por defecto, `notas/` del repositorio;
busca `ft_xxx.md` en todas sus subcarpetas):

- **Nivel 1**: el resumen bajo el título y la sección «Puntos clave y casos
  límite», con los errores típicos.
- **Nivel 2**: «Cómo implementarla», con el pseudocódigo. Va aparte para
  que no veas la solución sin querer.
- **casos**: el happy path y los edge cases de la función en
  «libft - Edge cases y tests por función» (sin los `main`).

Muestra los callouts (`> [!tip]`, `> [!warning]`…) con colores y quita los
`[[enlaces]]` y el formato de Markdown. Las notas no se modifican.

Para que `obsidian` abra la nota, la carpeta de notas tiene que estar
abierta como bóveda en Obsidian (por ejemplo, «Abrir carpeta como bóveda»
→ `notas/`).

**Usar tus propias notas.** Pon tu bóveda en `NOTES_DIR`. Cada función
necesita una nota `ft_xxx.md` con estas secciones (como las de `notas/`):

- `# ft_xxx` y justo debajo una cita `> …` con el resumen;
- `## Puntos clave y casos límite` (puede tener `### Errores típicos`);
- `## Cómo implementarla`;
- `## Prototipo` y `## Comportamiento según el subject` (las usa `man` sin
  el PDF).

Los casos límite salen de una nota llamada «libft - Edge cases y tests por
función», con una sección `### ft_xxx` por función.

## Modo test

```bash
./libft_43.sh test                    # todos los ft_*.c de la carpeta actual
./libft_43.sh test ft_strlen          # una función
./libft_43.sh test ft_atoi ft_split   # varias
```

Para cada función:

1. **norminette**: la pasa a tu archivo y muestra los errores si los hay.
2. **compilar**: copia tu libft real a una carpeta temporal, sustituye esa
   función por tu versión de práctica (algunos tests usan otras funciones,
   como `ft_lstnew`) y compila con `-Wall -Wextra -Werror`.
3. **libftTester + valgrind**: ejecuta su test con `valgrind` para detectar
   fugas, y enseña **cada caso** con su ✔/✘ y su código, sacado del `.cpp`
   del tester: lo que prepara y lo que comprueba.
4. **reglas del subject**: las que libftTester no mira (abajo), una a una.
5. Borra la carpeta temporal. Tu libft real y el tester no se modifican.

Cada paso sale con su ✔ o ✘. En el menú, el paso en marcha se ve como
`⏳ libftTester + valgrind…`, y la barra de estado lo dice con los segundos
que lleva (`⠹ test ft_strtrim · libftTester + valgrind · 4s`):

```
🧪 ft_strtrim
  ✔ norminette
  ✔ compilar
  ✘ libftTester + valgrind: 16 OK, 2 KO
      ✔  1  char * s = ft_strtrim("   xxxtripouille", " x"); → !strcmp(s, "tripouille")
      ✔  2  malloc de s: strlen("tripouille") + 1 bytes
      …
      ✘ 17  s = ft_strtrim("ababa", "a");
            → !strcmp(s, "bab")
      ✘ 18  malloc de s: 4 bytes
  ✔ reglas del subject
      ✔ solo funciones autorizadas (malloc)
      ✔ funciones auxiliares con static
      ✔ sin variables globales
      ✔ sin restrict
```

`malloc de s: N bytes` (los `MOK`/`MKO`) comprueba que reservas justo lo
necesario. Si el programa se cae, los casos que no llegan a ejecutarse salen
con `·` y se indica en qué caso fue el SIGSEGV.

### Reglas del subject

| Regla | Cómo se comprueba |
|-------|-------------------|
| Solo las funciones externas autorizadas | `nm -u` del `.o`: aparte de tus `ft_*`, solo se admite lo que el subject permite a esa función (`malloc`, `free`, `write`) |
| Funciones auxiliares `static` | `nm`: no puede haber otra función global además de la tuya |
| Sin variables globales | `nm`: no puede haber variables en `.data` ni `.bss` |
| Sin `restrict` | Se busca la palabra en tu archivo |
| `ft_is*` devuelven 1 o 0 | Se prueban todos los valores de -1 a 255 |
| `ft_calloc` con 0 | `nmemb` o `size` a 0 debe dar un puntero que se pueda liberar |
| `ft_calloc` sin desbordamiento | `ft_calloc(SIZE_MAX / 2 + 2, 2)` debe devolver `NULL` (`man 3 calloc`) |

Si una regla falla sale con ✘ y el motivo, y el resultado pone `subject KO`.

Ojo: si el compilador puede calcular una llamada sin hacerla (por ejemplo
`strlen("a")`), `nm` no la ve.

### Resultado

```
📋 Resumen
  ✘ ft_atoi            no compila, norma KO
  ✔ ft_lstsize         3 OK, 0 KO, norma OK, subject OK, tiempo 4m12s, sin pistas
  ✘ ft_strchr          4 OK, 1 KO, errores de valgrind, norma OK, subject OK
  ✘ ft_isalpha         8 OK, 0 KO, norma OK, subject KO
  ----------------------------------------
  Tests: 15 OK, 1 KO
  Funciones perfectas: 1/4
```

Una función es perfecta (✔) si no tiene ningún KO, ni SIGSEGV, ni fugas
(`LEAKS.KO`), ni errores de valgrind, pasa la norminette y cumple las reglas
del subject. Los KO de memoria (`MKO`) también cuentan como KO.

Hacer un test no cuenta como sugerencia.

## Progreso

```bash
./libft_43.sh progreso
```

Las 43 funciones por partes, con su estado (✔ ⟳ ✘ ·), los días distintos
en que las has resuelto, tu mejor tiempo sin pistas y cuándo toca repasar.

## Historial

Cada vez que testeas una función, el resultado se guarda en
`.libft_historial`, junto al script:

```bash
./libft_43.sh historial              # todo el historial
./libft_43.sh historial ft_strlen    # solo una función
```

`reset` no borra el historial. Para empezar desde cero, `reset todo` (o
`R` en el menú) borra el historial, los tiempos, las sugerencias y los
intentos en marcha. Tus `ft_*.c` e `intentos/` se quedan: están en la
carpeta actual, que podría ser tu libft real.

## Qué archivos toca el script

Solo escribe en la carpeta del script y en la carpeta desde la que lo
ejecutas:

- `ft_xxx.c` e `intentos/`: los archivos de práctica y tus versiones
  anteriores, en la carpeta actual.
- Junto al script: `.libft_historial` (resultados), `.libft_counts`
  (sugerencias), `.libft_ultima` (última función sugerida),
  `.libft_intentos` (intentos en marcha), `.libft_autopausa` (cronómetro
  pausado al cerrar la ventana), `.libft_paleta` (la paleta elegida),
  `.libft_foco` (dónde está el foco, para que vim se apague) y
  `.libft_peticiones` (lo que vim pide al menú con F5–F7; el menú lo vacía
  al leerlo).

No modifica tu libft real (`LIBFT_DIR`), ni libftTester (`TESTER_DIR`), ni
tus notas (`NOTES_DIR`): el modo test copia los archivos a una carpeta
temporal y la borra al terminar.

## Configuración

Las rutas se cambian en `config.sh`, junto al script (cópialo de
`config.example.sh`; no se sube a git):

| Variable | Por defecto | Qué es |
|----------|-------------|--------|
| `LIBFT_DIR` | `$HOME/libft` | Tu libft terminada (obligatoria) |
| `TESTER_DIR` | `$HOME/libftTester` | Clon de libftTester |
| `NOTES_DIR` | `notas/` del repositorio | Las notas de Obsidian |
| `SUBJECT_PDF` | (ninguno) | El subject, para `man` de las Partes 2 y 3 |
| `MAIL42` | `$USER@student.42barcelona.com` | El email de la cabecera |

Al abrir el menú y al testear, el script comprueba que en `LIBFT_DIR` estén
`libft.h` y las 43 funciones, y que exista libftTester. Si falta algo, dice
qué y no sigue.

## Requisitos

`bash`, `cc`, `clang++`, `ar`, `nm`, `valgrind`, `python3` y `man`; `tmux`
y `vim` para `menu`; `pdftotext` (opcional) para la ficha del subject;
`rich` (opcional, `pip install --user rich`) para ver las notas con
formato completo (tablas, listas, enlaces; sin él se ven con un formato
más sencillo); y
`norminette` (si no está instalada, el test sigue funcionando y pone
`norma no comprobada`). En los ordenadores de 42 Barcelona suele estar todo instalado.
