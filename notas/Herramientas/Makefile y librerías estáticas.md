---
tags: [herramientas, makefile, make, ar, libft]
---
# Makefile y librerías estáticas

← Inicio · Herramientas

> Un **Makefile** es un fichero de reglas que le dice a la herramienta `make` cómo construir tu proyecto (compilar los `.c`, empaquetar la librería…) y, sobre todo, **qué hace falta rehacer** cuando cambias algo. Una **librería estática** (`.a`) es un paquete de ficheros objeto (`.o`) que luego se une a tus programas. En 42 todos los proyectos de C se entregan con Makefile, y un Makefile mal hecho (relink, tabulaciones) puede suspenderte el proyecto entero.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Fichero objeto** (`.o`) | El resultado de compilar **un** `.c` sin enlazarlo todavía: código máquina con «huecos» para las funciones de otros ficheros. Ver Cómo compila C |
| **Enlazar** (*link*) | Unir varios `.o` (y librerías) en un ejecutable, rellenando esos huecos |
| **Objetivo** (*target*) | Lo que quieres construir con una regla: normalmente un fichero (`libft.a`) |
| **Prerrequisito** (*prerequisite*) | Lo que hace falta para construir el objetivo (`ft_strlen.o`) |
| **Receta** (*recipe*) | Los comandos de terminal que construyen el objetivo |
| **Relink** | Que `make` vuelva a compilar o empaquetar **sin que nada haya cambiado**. En 42 es un error grave |

## Qué es un Makefile y cómo funciona

Un Makefile no es un script de Bash que se ejecuta de arriba abajo. Es un **árbol de dependencias basado en fechas de modificación** (*timestamps*): cada fichero del disco guarda cuándo se modificó por última vez, y `make` las compara.

Cuando ejecutas `make`:
1. Comprueba la fecha de modificación del **archivo que quieres crear** (objetivo).
2. Comprueba la fecha de los **archivos necesarios para crearlo** (prerrequisitos).
3. Si algún prerrequisito es más reciente que el objetivo (o el objetivo aún no existe), ejecuta los comandos para crearlo o actualizarlo. Si nada ha cambiado, no hace nada.

Si ejecutas `make` sin decir qué objetivo quieres, construye **la primera regla** del Makefile. Por eso la primera suele ser `all`.

## Estructura básica de una regla

Toda regla sigue siempre este formato:

```make
objetivo: prerrequisito1 prerrequisito2
	comando_en_la_terminal
```

* **Objetivo (*target*):** casi siempre es un archivo que se va a generar (`libft.a`, `main.o`) o una orden abstracta (`clean`, `fclean`).
* **Prerrequisitos (*prerequisites*):** archivos que deben existir o actualizarse antes de que esta regla pueda ejecutarse.
* **Comandos (*recipe*):** órdenes de terminal que `make` ejecuta para transformar los prerrequisitos en el objetivo.

## El tabulador: la regla de oro que no perdona

> [!warning] Make exige un tabulador real
> Make se creó en 1976 y exige un carácter de tabulación real (`\t`) al inicio de cada línea de comando.

* Si usas **4 espacios** en vez de una tabulación, `make` fallará inmediatamente con:
  ```text
  Makefile:XX: *** missing separator.  Stop.
  ```
* **Consejo en editores:** configura tu editor para que en los `Makefile` respete siempre el carácter `Tab` real y no lo sustituya por espacios. Con la configuración de Vim (`set noexpandtab`) ya es así.

## Líneas largas con `\` y el error «missing separator»

En un Makefile, pulsar `Enter` significa «aquí termina esta instrucción». Cuando listas 20 o 30 archivos fuente, no quieres una línea infinita, pero tampoco puedes dar `Enter` a secas.

### La solución: barra invertida (`\`)

La barra invertida al final de la línea le indica a `make`: *«ignora este salto de línea y lee la siguiente línea como parte de la misma instrucción»*.

```make
# ✅ Correcto: la barra une las líneas en una sola lista continua
SRCS = srcs/ft_putchar.c \
       srcs/ft_putstr.c \
       srcs/ft_strlen.c

# ❌ Incorrecto: la segunda línea queda huérfana y make dará "missing separator"
SRCS = srcs/ft_putchar.c
       srcs/ft_putstr.c
```

### El fallo invisible: el espacio después de la barra

Nunca dejes un espacio después de la barra invertida (`\` + espacio + `Enter`). Entonces la barra ya no está al final de la línea, así que no une nada: la siguiente línea vuelve a quedar huérfana y da el mismo error. Como el espacio no se ve, cuesta mucho encontrarlo. En Vim, `:set list` muestra los espacios finales (el `.vimrc` de Vim los borra al guardar los `.c` y `.h`, pero no los Makefile).

## Variables: definición, expansión y modos de asignación

Las variables evitan repetir texto y permiten cambiar las banderas de compilación en un solo lugar. Para usarlas se escriben entre paréntesis con `$`: `$(NOMBRE_VARIABLE)`.

Hay cuatro formas de asignar valores:

```make
# 1. Asignación diferida / recursiva (=)
# Se evalúa en el momento en que se USA la variable, no donde se declara.
CC = cc

# 2. Asignación inmediata (:=)
# Se evalúa exactamente en la línea donde se escribe. Es más predecible.
SRC_DIR := srcs

# 3. Asignación condicional (?=)
# Asigna el valor SOLO si la variable no tenía ya uno (por ejemplo, del entorno).
CFLAGS ?= -Wall -Wextra -Werror

# 4. Concatenación (+=)
# Añade texto al final de la variable existente, separándolo con un espacio.
CFLAGS += -g
```

> [!tip] Variables desde la terminal
> Una variable escrita al llamar a `make` **sustituye** a la del Makefile, aunque esta use `=`: `make CFLAGS="-Wall -Wextra -Werror -g"`. Así se compila con `-g` para [[Depurar con gdb]] sin tocar el Makefile.

## Variables automáticas (`$@`, `$<`, `$^`…)

`make` ofrece atajos que representan los nombres de los archivos de la regla que se está ejecutando:

| Variable | Qué significa | Ejemplo práctico |
| :--- | :--- | :--- |
| `$@` | El **nombre del objetivo** actual | En `libft.a: $(OBJS)`, `$@` vale `libft.a` |
| `$<` | El **primer prerrequisito** de la lista | En `%.o: %.c`, `$<` es el archivo fuente `.c` |
| `$^` | **Todos los prerrequisitos** juntos (sin duplicados) | En `$(NAME): $(OBJS)`, `$^` son todos los `.o` |
| `$?` | Solo los prerrequisitos **más nuevos que el objetivo** | Útil para saber qué ficheros han cambiado |

Además, en una **regla de patrón** el símbolo **`%`** hace de comodín: `%.o: %.c` significa «cualquier `algo.o` se construye a partir de `algo.c`». No es una variable automática, pero casi siempre aparece junto a ellas.

**Ejemplo de regla de patrón con variables automáticas:**
```make
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
# Para ft_strlen.o se traduce como: cc -Wall -Wextra -Werror -c ft_strlen.c -o ft_strlen.o
```

> [!warning] El `.c` tiene que ir primero
> Si escribes `%.o: $(HEADER) %.c`, `$<` vale `libft.h` y el compilador intentará compilar el header. Pon siempre el `.c` como primer prerrequisito.

## Manipulación de listas: `addprefix` y sustitución de sufijos

Escribir `srcs/` delante de cada archivo es tedioso y propenso a errores. `make` incluye funciones para automatizarlo.

### `addprefix`: prefijar rutas automáticamente

```make
SRC_DIR = srcs
FILES   = ft_putchar.c ft_putstr.c ft_strlen.c

# addprefix agrega la carpeta a cada elemento de la lista
SRCS    = $(addprefix $(SRC_DIR)/, $(FILES))
# Resultado: srcs/ft_putchar.c srcs/ft_putstr.c srcs/ft_strlen.c
```

### Sustitución de sufijos: de `.c` a `.o`

Para obtener la lista de ficheros objeto, sustituye la extensión en una sola línea:
```make
OBJS = $(SRCS:.c=.o)
# Transforma cada 'srcs/archivo.c' en 'srcs/archivo.o'
```

> [!warning] Nada de comodines
> La [[La Norma|Norma]] exige que **todos los archivos fuente estén nombrados explícitamente** en el Makefile. Por eso no se aceptan `SRCS = *.c` ni `$(wildcard src/*.c)`, aunque funcionen.

## La bandera `-I` y los cambios en los headers

Error muy común: compilas con `-Iincludes`, cambias una estructura o una constante en tu `.h`, ejecutas `make` y responde `Nothing to be done`.

### Por qué pasa

`-Iincludes` solo le dice al **compilador** (`cc`) en qué carpeta buscar los `#include "..."` (ver Preprocesador y headers). Pero **`make` no lee el interior de los `.c`**: solo mira la lista de prerrequisitos de la regla. Si el header no está en esa lista, `make` no sabe que existe.

```make
# ❌ INCORRECTO: si editas libft.h, make no se entera y no recompila
%.o: %.c
	$(CC) $(CFLAGS) -Iincludes -c $< -o $@

# ✅ CORRECTO: libft.h es prerrequisito explícito; si cambia, se recompilan los .o
HEADER = includes/libft.h

%.o: %.c $(HEADER)
	$(CC) $(CFLAGS) -Iincludes -c $< -o $@
```

## Librerías estáticas y el comando `ar`

Una librería estática (`.a`, de *archive*) es simplemente un **archivo contenedor** (sin comprimir) que empaqueta varios ficheros objeto (`.o`) juntos. Cuando compilas un programa con `libft.a`, el enlazador copia dentro del ejecutable solo los `.o` que contienen las funciones que usas.

Para generarla en 42 se usa `ar` (el subject de libft prohíbe `libtool`):
```make
ar rcs libft.a $(OBJS)
```

* **`r` (*replace*):** si el `.o` ya estaba dentro del `.a`, lo sustituye; si no estaba, lo añade.
* **`c` (*create*):** crea el `.a` sin avisar si todavía no existe.
* **`s` (*symbol index*):** crea o actualiza un índice de símbolos (los nombres de funciones y variables que contiene), para que el enlazador encuentre rápido cada función. Hace lo mismo que el comando `ranlib`.

Para usarla al compilar un programa:

```bash
cc -Wall -Wextra -Werror main.c libft.a -o prog
# o, si está en otra carpeta: -L carpeta -lft  (busca carpeta/libft.a)
```

> [!tip] Ver qué hay dentro
> `ar t libft.a` lista los `.o` que contiene. `nm libft.a` muestra los símbolos (las funciones definidas aparecen con una `T`).

## Reglas falsas: por qué hace falta `.PHONY`

Si creas una carpeta o un archivo llamado `clean` dentro de tu proyecto y luego ejecutas `make clean`:
1. `make` buscará el objetivo `clean`.
2. Verá que ya existe un archivo o carpeta llamado `clean` en el disco.
3. Como `clean` no tiene prerrequisitos, pensará que ya está «al día» y responderá:
   ```text
   make: 'clean' is up to date.
   ```
4. **Tus comandos de borrado nunca se ejecutarán.**

Para indicar que un objetivo es una **acción** y no un archivo real, se declara con `.PHONY` (*phony* = falso):
```make
.PHONY: all clean fclean re bonus
```

## El relink: qué es, por qué suspende y cómo evitarlo

> [!danger] Proyecto no funcional
> Según la [[La Norma|Norma]], si el Makefile hace relink el proyecto se considera **no funcional**: es un 0 en la evaluación.

### Qué es el relink

Hacer relink significa que `make` ejecuta comandos de compilación o empaquetado **cuando nada en el código ha cambiado**.

```text
$ make
cc -c src/ft_strlen.c -o src/ft_strlen.o
ar rcs libft.a src/ft_strlen.o
$ make
ar rcs libft.a src/ft_strlen.o      ← ❌ no has tocado nada y volvió a empaquetar
```

La respuesta correcta ante un segundo `make` inmediato es:
```text
$ make
make: Nothing to be done for 'all'.
```

> [!question] Pregunta típica de evaluación
> El evaluador ejecuta `make` dos veces seguidas (y, si hay bonus, `make bonus` dos veces). Si la segunda vez sale cualquier comando de compilación o de `ar`, hay relink.

### Las causas más comunes de relink

1. **Una regla que depende de un objetivo `.PHONY` en vez de un archivo real.** Si pones `$(NAME): all`, como `all` es PHONY, `make` siempre lo considera desactualizado y vuelve a construir.
2. **Una regla cuyo objetivo no es el fichero que crea.** Si la regla se llama `$(NAME)` pero la receta genera otro nombre, el objetivo nunca existe y la regla se ejecuta siempre.
3. **Una carpeta como prerrequisito normal** (`$(OBJ_DIR)/%.o: ... $(OBJ_DIR)`). La fecha de una carpeta cambia cada vez que se crea un fichero dentro, así que parece «más nueva». Crea la carpeta dentro de la receta con `mkdir -p` (ver [[#Carpeta de objetos con mkdir -p]]).
4. **La trampa de la regla `bonus`.** Si `bonus` vuelve a ejecutar `ar` sin control, cada `make bonus` empaqueta otra vez. Se soluciona con un **archivo centinela** (ver [[#Plantilla con bonus sin relink]]).

## Carpeta de objetos con mkdir -p

Tener los `.o` mezclados con los `.c` ensucia el repositorio. Lo habitual es compilarlos en una carpeta separada llamada `obj/` u `.objs/` (y añadirla al `.gitignore`, ver [[Git para 42]]).

Para que `cc` no falle con `No such file or directory`, hay que asegurarse de que la carpeta destino existe, con `mkdir -p` (`-p` crea las carpetas intermedias y no da error si ya existen):

```make
SRC_DIR = src
OBJ_DIR = obj
HEADER  = includes/libft.h

SRCS    = $(SRC_DIR)/ft_strlen.c $(SRC_DIR)/ft_putchar.c
# Reemplaza la ruta 'src/' por 'obj/' y la extensión '.c' por '.o'
OBJS    = $(SRCS:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

# Compilación de objetos creando la carpeta sobre la marcha
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c $(HEADER)
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -Iincludes -c $< -o $@
```
La función `$(dir $@)` extrae la carpeta del archivo objeto que se va a crear (por ejemplo, `obj/`).

## Silenciar comandos con @ y mostrar mensajes

Por defecto, `make` imprime cada comando antes de ejecutarlo. Para una salida más limpia:

* **`@` al inicio del comando:** `make` lo ejecuta sin imprimirlo.
* **`echo` con colores ANSI** (secuencias como `\033[0;33m`, que la terminal interpreta como «cambia a amarillo»):

```make
clean:
	@$(RM) $(OBJS)
	@echo "\033[0;33mArchivos objeto eliminados.\033[0m"

fclean: clean
	@$(RM) $(NAME)
	@echo "\033[0;31mLibrería $(NAME) eliminada.\033[0m"
```

> [!note] `echo` y los colores
> `make` ejecuta las recetas con `/bin/sh`. En Ubuntu es `dash`, cuyo `echo` interpreta `\033`; con otros shells puede imprimirse tal cual. `printf "\033[0;33m...\033[0m\n"` funciona igual en todos.

> [!tip] No escondas los errores
> El `@` oculta el comando, no los errores del compilador. Mientras desarrollas, quitar los `@` ayuda a ver exactamente qué se está ejecutando.

## Plantilla completa para libft

Esta plantilla cumple la Norma, no hace relink y recompila si cambia el header. Los números de los comentarios son solo para organizar el fichero.

### Estructura de carpetas de ejemplo

```text
mi_proyecto/
├── Makefile
├── includes/
│   └── libft.h
└── src/
    ├── ft_putchar.c
    ├── ft_putstr.c
    └── ft_strlen.c
```

> [!warning] En libft, todo en la raíz
> El subject de libft (v19.3) pide que **todos los archivos estén en la raíz del repositorio**, y `libft.a` también. Para libft, quita `src/` e `includes/` (sin `addprefix`, y `-I.` como en tu Makefile real). La estructura con carpetas sirve para proyectos posteriores.

### Código del Makefile

```make
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: estudiante <estudiante@student.42barcel    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/09/27 12:00:00 by estudiante        #+#    #+#              #
#    Updated: 2026/09/27 12:00:00 by estudiante       ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# ========================================== #
# 1. NOMBRE DEL BINARIO O LIBRERÍA           #
# ========================================== #
NAME        = libft.a

# ========================================== #
# 2. HERRAMIENTAS Y BANDERAS                 #
# ========================================== #
CC          = cc
CFLAGS      = -Wall -Wextra -Werror
AR          = ar rcs
RM          = rm -f

INC_DIR     = includes
SRC_DIR     = src

# Flag de inclusión para el compilador y archivo de dependencia para make
INCLUDES    = -I $(INC_DIR)
HEADER      = $(INC_DIR)/libft.h

# ========================================== #
# 3. ARCHIVOS FUENTE Y OBJETOS               #
# ========================================== #
SRC_FILES   = ft_putchar.c \
              ft_putstr.c \
              ft_strlen.c

SRCS        = $(addprefix $(SRC_DIR)/, $(SRC_FILES))
OBJS        = $(SRCS:.c=.o)

# ========================================== #
# 4. REGLAS PRINCIPALES                      #
# ========================================== #

# Primera regla: es la que se ejecuta al teclear solo 'make'
all: $(NAME)

# Creación de la librería estática (depende de que existan los .o)
$(NAME): $(OBJS)
	$(AR) $@ $^
	@echo "Librería $(NAME) creada con éxito."

# Regla de patrón: cada .c genera su .o correspondiente
# El header está listado para recompilar si se modifica
%.o: %.c $(HEADER)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# ========================================== #
# 5. REGLAS DE LIMPIEZA                      #
# ========================================== #

clean:
	$(RM) $(OBJS)
	@echo "Objetos temporales eliminados."

fclean: clean
	$(RM) $(NAME)
	@echo "$(NAME) eliminado por completo."

re: fclean all

# ========================================== #
# 6. PHONY TARGETS                           #
# ========================================== #
.PHONY: all clean fclean re
```

## Plantilla con bonus sin relink

> [!info] libft v19.3 no tiene bonus
> En el subject de libft v19.3 las listas enlazadas son la **Parte 3, obligatoria**: van en `SRC_FILES` como el resto. En versiones anteriores eran el bonus, y otros proyectos sí tienen parte bonus. Las instrucciones generales del subject piden entonces una regla `bonus` y que los ficheros bonus se llamen `*_bonus.c` / `*_bonus.h`. Esta plantilla sirve para esos casos.

### El truco del archivo centinela (`.bonus`)

Quieres que `make bonus` compile la parte obligatoria y la bonus, pero **sin recompilar ni volver a empaquetar si vuelves a escribir `make bonus`**. El problema es que `bonus` es una acción (PHONY), no un fichero, así que `make` no tiene una fecha con la que comparar.

La solución es usar un archivo oculto vacío llamado `.bonus` como objetivo real: se crea con `touch` al terminar, y su fecha sirve para saber si hace falta repetir el trabajo.

```make
# ========================================== #
# VARIABLES BÁSICAS                          #
# ========================================== #
NAME        = libft.a
CC          = cc
CFLAGS      = -Wall -Wextra -Werror
AR          = ar rcs
RM          = rm -f

INC_DIR     = includes
SRC_DIR     = src
INCLUDES    = -I $(INC_DIR)
HEADER      = $(INC_DIR)/libft.h

# ========================================== #
# ARCHIVOS OBLIGATORIOS Y BONUS              #
# ========================================== #
FILES_MANDATORY = ft_putchar.c \
                  ft_strlen.c

FILES_BONUS     = ft_lstnew_bonus.c \
                  ft_lstadd_front_bonus.c

SRCS_MANDATORY  = $(addprefix $(SRC_DIR)/,$(FILES_MANDATORY))
SRCS_BONUS      = $(addprefix $(SRC_DIR)/,$(FILES_BONUS))

OBJS_MANDATORY  = $(SRCS_MANDATORY:.c=.o)
OBJS_BONUS      = $(SRCS_BONUS:.c=.o)

# ========================================== #
# REGLAS                                     #
# ========================================== #
.PHONY: all clean fclean re bonus

all: $(NAME)

# Regla estándar: solo compila la parte obligatoria
$(NAME): $(OBJS_MANDATORY)
	$(AR) $@ $^

# Regla bonus: depende del archivo centinela .bonus
bonus: .bonus

# .bonus depende de los objetos obligatorios Y de los bonus
# Si ninguno ha cambiado, la receta no se ejecuta y no hay relink
.bonus: $(OBJS_MANDATORY) $(OBJS_BONUS)
	$(AR) $(NAME) $^
	@touch .bonus

%.o: %.c $(HEADER)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	$(RM) $(OBJS_MANDATORY) $(OBJS_BONUS) .bonus

fclean: clean
	$(RM) $(NAME)

re: fclean all
```

> [!warning] Limitación del centinela
> Si borras `libft.a` a mano pero no `.bonus`, `make bonus` dirá que no hay nada que hacer. Usa siempre `make fclean`, que borra los dos.

## Relacionadas

[[La Norma]] · Cómo compila C · Preprocesador y headers · [[Depurar con gdb]] · [[Git para 42]] · Vim · [[libft - Índice]]

## Referencias

- [GNU make manual](https://www.gnu.org/software/make/manual/make.html) — funcionamiento general de `make`.
- [GNU make: Rule Syntax](https://www.gnu.org/software/make/manual/html_node/Rule-Syntax.html) y [Recipe Syntax](https://www.gnu.org/software/make/manual/html_node/Recipe-Syntax.html) — objetivos, prerrequisitos y el tabulador obligatorio.
- [GNU make: Splitting Long Lines](https://www.gnu.org/software/make/manual/html_node/Splitting-Lines.html) — la barra invertida al final de línea.
- [GNU make: The Two Flavors of Variables](https://www.gnu.org/software/make/manual/html_node/Flavors.html) y [Setting Variables](https://www.gnu.org/software/make/manual/html_node/Setting.html) — `=`, `:=`, `?=`.
- [GNU make: Overriding Variables](https://www.gnu.org/software/make/manual/html_node/Overriding.html) — variables pasadas desde la línea de comandos.
- [GNU make: Automatic Variables](https://www.gnu.org/software/make/manual/html_node/Automatic-Variables.html) y [Pattern Rules](https://www.gnu.org/software/make/manual/html_node/Pattern-Rules.html) — `$@`, `$<`, `$^`, `$?` y `%`.
- [GNU make: Substitution References](https://www.gnu.org/software/make/manual/html_node/Substitution-Refs.html) y [Functions for File Names](https://www.gnu.org/software/make/manual/html_node/File-Name-Functions.html) — `$(SRCS:.c=.o)`, `addprefix`, `dir`.
- [GNU make: Phony Targets](https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html) — `.PHONY`.
- [`man 1 ar`](https://man7.org/linux/man-pages/man1/ar.1.html) — modificadores `r`, `c`, `s` y `t`.
- La Norma v4, capítulo III.11 «Makefile» (`Normativa 42/es.norm-2.pdf`) — reglas obligatorias, relink y fuentes nombradas explícitamente.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — `ar` obligatorio, `libtool` prohibido, todo en la raíz, ficheros `_bonus.{c/h}`.
