---
tags: [herramientas, gdb, lldb, debug, c]
---
# Depurar con gdb

← Inicio · Herramientas

> **Depurar** (*debugging*) es encontrar por qué un programa no hace lo que esperas. Un **depurador** como `gdb` (*GNU Debugger*) te deja ejecutar tu programa **a cámara lenta**: pararlo en la línea que quieras, avanzar línea a línea y mirar qué valor tiene cada variable en ese momento. Así ves **qué hace de verdad** tu código, no lo que crees que hace.

> [!info] En los Mac de 42
> En macOS no hay `gdb`: se usa **`lldb`**, que funciona igual con algunos comandos distintos. Al final de la nota tienes una [[#Equivalencias gdb ↔ lldb|tabla de equivalencias]]. Todo lo demás de esta nota (compilar con `-g`, el método, los ejemplos) vale igual.

## ¿Por qué no basta con `printf`?

Llenar el código de `printf` funciona, pero cada prueba exige editar, recompilar y volver a ejecutar, y solo ves lo que imprimiste. Con gdb:

- Paras el programa **donde quieras sin tocar el código**.
- Ves **todas** las variables, no solo las que imprimiste.
- Si crashea, te dice **la línea exacta** y quién llamó a esa función.
- Puedes **cambiar un valor** a mitad de ejecución para probar una idea.

## Vocabulario básico

| Término | Qué significa |
|---|---|
| **Bug** | Un error en el programa: crashea o da un resultado incorrecto |
| **Breakpoint** (punto de parada) | Una línea o función donde le pides a gdb que **pare** el programa |
| **Paso** (*step*) | Ejecutar **una sola línea** y volver a parar |
| **Pila de llamadas** (*call stack*) | La lista de funciones que se están ejecutando: `main` llamó a `f`, que llamó a `g`… |
| **Frame** (marco) | Cada función de esa lista, con sus propias variables |
| **Segfault** (`SIGSEGV`) | El programa intentó acceder a memoria que no le pertenece (p. ej. un puntero `NULL`) y el sistema lo mató con esa señal |
| **Símbolos de depuración** | La información que añade `-g`: qué línea del código es cada instrucción y cómo se llaman tus variables |
| **Optimización** | Cambios que hace el compilador para que el programa vaya más rápido (reordenar o eliminar instrucciones). Ver Cómo compila C |

---

## Paso obligatorio: compilar con `-g`

> [!danger] Sin `-g`, gdb está ciego
> **Antes de depurar tienes que compilar con la bandera `-g`.** Es el error más común: si te lo saltas, gdb no puede enseñarte tu código, ni tus variables, ni los números de línea.

```bash
cc -Wall -Wextra -Werror -g -O0 main.c -o prog
```

| Bandera | Para qué sirve |
|---|---|
| **`-g`** | Guarda dentro del ejecutable un «mapa» que relaciona cada instrucción de la máquina con **tu línea de código** y cada dirección de memoria con **el nombre de tu variable** |
| **`-O0`** | Desactiva las optimizaciones del compilador, para que el programa haga los pasos **en el mismo orden que los escribiste**. Es lo que se usa por defecto si no pones ninguna `-O`, pero conviene ponerla explícitamente |

### Qué pasa si se te olvida

El mismo programa (el del [[#Caso 1: el programa crashea (segfault)|caso 1]]), primero **sin** `-g`:

```text
$ cc -Wall -Wextra -Werror count.c -o count
$ gdb -q ./count
Reading symbols from ./count...
(No debugging symbols found in ./count)          ← aviso: no hay -g
(gdb) run
Program received signal SIGSEGV, Segmentation fault.
0x000000000040116a in count_char ()              ← ni línea ni variables
(gdb) break 11
No compiled code for line 11 in the current file.
Make breakpoint pending on future shared library load? (y or [n]) n
(gdb) info locals
No symbol table info available.
```

Y **con** `-g`:

```text
$ cc -Wall -Wextra -Werror -g count.c -o count
$ gdb -q ./count
Reading symbols from ./count...
(gdb) run
Program received signal SIGSEGV, Segmentation fault.
0x000000000040116a in count_char (s=0x0, c=97 'a') at count.c:8
8		while (*s)                                   ← línea exacta y valores
```

> [!tip] ¿Mi ejecutable tiene `-g`?
> Usa el comando `file`. Si aparece **`with debug_info`**, está compilado con `-g`:
> ```text
> $ file count
> count: ELF 64-bit LSB executable, x86-64, ..., with debug_info, not stripped
> ```

### Reglas para no equivocarte

1. **Todos los archivos con `-g`**, también tu librería. Si tu programa usa `libft.a` y la libft se compiló sin `-g`, gdb no podrá entrar en tus funciones `ft_` (ver el [[#Problemas típicos y cómo resolverlos|problema 3]]).
2. **Si cambias el código, recompila** antes de volver a lanzar gdb. Si no, gdb ejecuta la versión vieja y te enseña líneas que ya no coinciden.
3. **En un proyecto con Makefile**, puedes añadir `-g` sin tocar el Makefile pasándolo desde la terminal. Haz `fclean` antes, para que se recompile todo:
   ```bash
   make fclean
   make CFLAGS="-Wall -Wextra -Werror -I. -g"
   ```
   Funciona porque una variable que escribes en la línea de comandos **sustituye** a la del Makefile. Por eso, si tu Makefile pone más cosas en `CFLAGS` (como `-I.` en tu libft), inclúyelas también: si no, se pierden.
4. **Lo normal es no dejar `-g` en el Makefile que entregas**: usa las banderas que pida el subject (ver [[Makefile y librerías estáticas]]).

---

## Los comandos imprescindibles

Con estos diez puedes depurar casi cualquier cosa. Entre paréntesis, su abreviatura:

| Comando | Qué hace |
|---|---|
| `gdb ./prog` | Abre el programa en gdb **sin ejecutarlo todavía** |
| `break función` / `break línea` (`b`) | Pone un breakpoint |
| `run` (`r`) | Ejecuta el programa (hasta el primer breakpoint o hasta el final) |
| `next` (`n`) | Ejecuta la línea actual y para en la siguiente. Si la línea llama a una función, la ejecuta entera **sin entrar** |
| `step` (`s`) | Como `next`, pero **entra** dentro de la función que se llama |
| `continue` (`c`) | Sigue ejecutando hasta el siguiente breakpoint |
| `print variable` (`p`) | Muestra el valor de una variable o expresión |
| `backtrace` (`bt`) | Muestra la pila de llamadas: quién llamó a quién |
| `finish` | Termina la función actual y vuelve a la que la llamó |
| `quit` (`q`) | Sale de gdb |

> [!tip] Dos trucos que ahorran mucho tiempo
> - **Pulsar Enter sin escribir nada repite el último comando.** Escribe `next` una vez y luego solo Enter, Enter, Enter…
> - **`gdb -tui ./prog`** abre el modo visual: el código arriba con la línea actual marcada y la consola abajo. Para principiantes ayuda mucho. Si la pantalla se descoloca, pulsa `Ctrl + L`.

**Argumentos del programa:** si tu programa se ejecuta como `./prog hola 42`, en gdb haces `run hola 42`, o lo abres directamente con `gdb --args ./prog hola 42`.

---

## Caso 1: el programa crashea (segfault)

Este programa cuenta cuántas `'a'` hay en el primer argumento:

```c
#include <stddef.h>

static size_t	count_char(const char *s, char c)
{
	size_t	n;

	n = 0;
	while (*s)
	{
		if (*s == c)
			n++;
		s++;
	}
	return (n);
}

int	main(int argc, char **argv)
{
	size_t	n;

	(void)argc;
	n = count_char(argv[1], 'a');
	return ((int)n);
}
```

Con `./count banana` funciona. Pero sin argumentos:

```text
$ ./count
zsh: segmentation fault  ./count
```

El sistema solo dice que ha crasheado, no dónde ni por qué. Vamos con gdb:

**Paso 1: compilar con `-g` y ejecutar dentro de gdb.**

```text
$ cc -Wall -Wextra -Werror -g count.c -o count
$ gdb -q ./count
(gdb) run
Program received signal SIGSEGV, Segmentation fault.
0x000000000040116a in count_char (s=0x0, c=97 'a') at count.c:8
8		while (*s)
```

gdb para justo en la línea que crashea, la 8, y nos da una pista enorme: **`s=0x0`**. `0x0` es `NULL` (ver [[Carácter nulo y puntero NULL]]), y `*s` intenta leer la dirección 0, que ningún programa puede leer (ver [[Punteros en C]]).

**Paso 2: ¿quién llamó con `NULL`?** `backtrace` muestra la pila de llamadas. La de arriba (`#0`) es donde estamos; las de abajo, quién nos llamó:

```text
(gdb) bt
#0  0x000000000040116a in count_char (s=0x0, c=97 'a') at count.c:8
#1  0x0000000000401138 in main (argc=1, argv=0x7fffffffdf48) at count.c:22
```

**Paso 3: subir a `main` y mirar sus variables.** Con `frame 1` (o `up`) te colocas en el marco de `main`:

```text
(gdb) frame 1
#1  0x0000000000401138 in main (argc=1, argv=0x7fffffffdf48) at count.c:22
22		n = count_char(argv[1], 'a');
(gdb) p argc
$1 = 1
(gdb) p argv[1]
$2 = 0x0
```

**Diagnóstico:** `argc` vale 1 (solo el nombre del programa), así que `argv[1]` es `NULL` y nadie lo comprobó. **Solución:** comprobar `argc` antes de usar `argv[1]` (ver [[Control de errores en C]]).

> [!summary] Receta para cualquier segfault
> 1. `run` → gdb para en la línea del crash.
> 2. Mira los valores que muestra: un `0x0` suele ser el culpable.
> 3. `bt` → quién llamó a quién.
> 4. `frame N` → sube a la función que pasó el valor malo, y `p` de sus variables.

---

## Caso 2: el programa no crashea, pero da un resultado incorrecto

Es el caso más habitual y el más difícil, porque no hay ningún mensaje que te diga dónde mirar. Este programa debería contar las palabras de `"hola que tal"` (3):

```c
#include <stdio.h>

static int	count_words(const char *s)
{
	int	words;
	int	i;

	words = 0;
	i = 0;
	while (s[i])
	{
		if (s[i] != ' ' && s[i + 1] == ' ')
			words++;
		i++;
	}
	return (words);
}

int	main(void)
{
	printf("%d\n", count_words("hola que tal"));
	return (0);
}
```

```text
$ ./words
2
```

La idea del código es: «cuento una palabra cada vez que una letra va seguida de un espacio». Hay que comprobar **cuándo se cumple de verdad** esa condición.

**Paso 1: parar cada vez que se cuenta una palabra.** El `words++` está en la línea 13:

```text
(gdb) break 13
Breakpoint 1 at 0x4011c7: file words.c, line 13.
(gdb) run
Breakpoint 1, count_words (s=0x402008 "hola que tal") at words.c:13
13				words++;
(gdb) p i
$1 = 3
(gdb) p s[i]
$2 = 97 'a'
```

Ha contado la palabra al llegar a la `a` de `hola` (posición 3). Correcto. Seguimos:

```text
(gdb) continue
Breakpoint 1, count_words (s=0x402008 "hola que tal") at words.c:13
13				words++;
(gdb) p i
$3 = 7
(gdb) p s[i]
$4 = 101 'e'
(gdb) continue
2
[Inferior 1 (process 950955) exited normally]
```

La `e` de `que` también cuenta, pero **después ya no vuelve a parar**: la palabra `tal` nunca se cuenta.

**Paso 2: mirar qué pasa con la última letra.** `tal` termina en la posición 11. Borramos el breakpoint anterior con `delete` y ponemos un **breakpoint condicional** que solo pare cuando `i` valga 11. Después, `run` vuelve a ejecutar el programa desde el principio:

```text
(gdb) delete
(gdb) break 12 if i == 11
Breakpoint 2 at 0x401198: file words.c, line 12.
(gdb) run
Breakpoint 2, count_words (s=0x402008 "hola que tal") at words.c:12
12			if (s[i] != ' ' && s[i + 1] == ' ')
(gdb) p s[i]
$5 = 108 'l'
(gdb) p s[i + 1]
$6 = 0 '\000'
```

**Diagnóstico:** después de la última `l` no viene un espacio sino el **`'\0'`** del final de la cadena, así que la condición `s[i + 1] == ' '` es falsa. **Solución:** contar también cuando lo siguiente es el final:

```c
if (s[i] != ' ' && (s[i + 1] == ' ' || s[i + 1] == '\0'))
```

Ahora devuelve `3`.

> [!summary] Receta para un resultado incorrecto
> 1. Escribe tu **hipótesis**: «esto debería pasar en tal momento».
> 2. Pon un breakpoint donde debería pasar y comprueba con `p` si de verdad pasa.
> 3. Busca **el primer momento** en que un valor no es el que esperabas: el bug está justo antes.
> 4. Prueba con casos límite: cadena vacía, un solo elemento, el **último** elemento…

---

## Más herramientas útiles

### Ver variables

| Comando | Qué muestra |
|---|---|
| `info locals` | Todas las variables locales de la función actual |
| `info args` | Los parámetros que recibió la función |
| `display i` | Muestra `i` **automáticamente cada vez que el programa para** (ideal con `next`) |
| `undisplay 1` | Deja de mostrar el display número 1 |
| `p *ptr` | Lo que hay donde apunta `ptr` |
| `p arr[0]@5` | 5 elementos seguidos desde `arr[0]` (para ver un array o un buffer) |
| `p/x n` · `p/d n` · `p/c n` | `n` en hexadecimal, decimal o como carácter |
| `ptype s` | El tipo de `s` |
| `set var i = 0` | Cambia el valor de una variable para probar una idea |

```text
(gdb) display n
1: n = 0
(gdb) display *s
2: *s = 98 'b'
(gdb) next
1: n = 0
2: *s = 97 'a'
(gdb) p s[0]@3
$2 = "ana"
```

> [!note] Una variable con un valor raro
> Si haces `p` de una variable **antes** de que se le asigne nada, verás basura (por ejemplo `n = 100`): es lo que hubiera antes en esa memoria. No es un fallo de gdb, sino la razón por la que nunca hay que usar una variable sin inicializar (ver [[Segmentos de memoria en C]]).

### Breakpoints

| Comando | Qué hace |
|---|---|
| `break count_char` | Para al entrar en esa función |
| `break count.c:11` | Para en la línea 11 de `count.c` (útil con varios archivos) |
| `break 11 if n == 2` | Para solo cuando se cumple la condición. Ideal en bucles |
| `info breakpoints` | Lista los breakpoints con su número |
| `delete 2` / `delete` | Borra el breakpoint 2 / todos |
| `disable 2` / `enable 2` | Lo desactiva o lo reactiva sin borrarlo |
| `until 15` | Sigue hasta la línea 15 (para salir de un bucle de golpe) |

### Watchpoints: ¿quién cambia esta variable?

`watch n` para el programa **cada vez que `n` cambia** y te enseña el valor anterior y el nuevo. Es perfecto cuando una variable acaba con un valor que no esperabas y no sabes en qué línea ocurre:

```text
(gdb) watch n
Hardware watchpoint 2: n
(gdb) continue
Old value = 0
New value = 1
count_char (s=0x7fffffffe39f "anana", c=97 'a') at count.c:12
12			s++;
```

---

## Depurar tu libft con un main de prueba

Para depurar una función de tu libft, escribe un `main.c` pequeño que la llame:

```c
#include <stdio.h>
#include <stdlib.h>
#include "libft.h"

int	main(void)
{
	char	*copia;

	copia = ft_strdup("hola mundo");
	printf("%s\n", copia);
	free(copia);
	return (0);
}
```

Y compila **todo** con `-g`, incluida la librería (`-I.` es porque tu Makefile ya lo pone en `CFLAGS`):

```bash
make fclean
make CFLAGS="-Wall -Wextra -Werror -I. -g"
cc -Wall -Wextra -Werror -g main.c -L. -lft -o prueba
gdb ./prueba
```

```text
(gdb) break ft_strdup
(gdb) run
Breakpoint 1, ft_strdup (s=0x555555556004 "hola mundo") at ft_strdup.c:20
20		str_len = ft_strlen(s) + 1;
(gdb) bt
#0  ft_strdup (s=0x555555556004 "hola mundo") at ft_strdup.c:20
#1  0x00005555555551a4 in main () at main.c:9
```

Cuando termines, vuelve a compilar normal con `make re`.

---

## Método general para depurar

1. **Reproduce el fallo** siempre con la misma entrada. Si no lo puedes repetir, no puedes comprobar si lo has arreglado.
2. **Compila con `-g`** (y `-O0`).
3. **¿Crashea?** → `run`, `bt`, `frame N`, `p`. Ver el [[#Caso 1: el programa crashea (segfault)|caso 1]].
4. **¿Resultado incorrecto?** → hipótesis, `break` donde debería pasar, `p`/`display`, y busca el primer valor inesperado. Ver el [[#Caso 2: el programa no crashea, pero da un resultado incorrecto|caso 2]].
5. **¿Una variable cambia y no sabes dónde?** → `watch`.
6. **¿Problemas de memoria** (leaks, leer fuera de un array)? gdb no los detecta bien: usa `valgrind` o `-fsanitize=address` (ver [[Valgrind y sanitizers]] y [[Control de errores en C]]).
7. **Cuando lo arregles, prueba otra vez todos los casos**, no solo el que fallaba.

---

## Problemas típicos y cómo resolverlos

| # | Lo que ves | Por qué pasa | Qué hacer |
|---|---|---|---|
| 1 | `(No debugging symbols found in ./prog)` | Compilaste sin `-g` | Recompila **todo** con `-g` |
| 2 | `No symbol "n" in current context.` | El programa aún no se está ejecutando, o estás en otra función | Haz `run` primero, o cambia de función con `frame N` |
| 3 | `step` no entra en tu función `ft_...`, la ejecuta de golpe | Esa función (o tu `libft.a`) se compiló **sin `-g`**: gdb se salta las funciones sin símbolos | Recompila la librería con `-g` (ver [[#Depurar tu libft con tus tests]]) |
| 4 | `step` te mete dentro de `printf` o `malloc` | Has entrado en una función de la libc | Escribe `finish` para salir, y usa `next` en esas líneas |
| 5 | Un breakpoint nunca para, o ves `<optimized out>` | Compilaste con optimizaciones (`-O2`…), y el compilador ha reordenado o eliminado código | Compila con `-O0` |
| 6 | Las líneas que enseña gdb no coinciden con tu código | Cambiaste el código y no recompilaste | Recompila y vuelve a abrir gdb |
| 7 | `The program is not being run.` | El programa no ha empezado o ya terminó | `run` |
| 8 | gdb parece colgado | Tu programa está esperando que escribas algo (por ejemplo, lee de la entrada estándar) | Escribe la entrada en la consola de gdb, o haz `run < archivo.txt` |
| 9 | El programa no termina nunca (bucle infinito) | — | Pulsa **`Ctrl + C`**: gdb lo para donde esté. Luego `bt` y `p` para ver en qué bucle está y por qué no avanza |
| 10 | Al salir pregunta `Quit anyway? (y or n)` | El programa sigue en marcha dentro de gdb | Responde `y` |

---

## Equivalencias gdb ↔ lldb

En los Mac de 42 se usa `lldb`. Se compila igual (**con `-g`**) y el método es el mismo; solo cambian algunos comandos:

| Acción | gdb | lldb (macOS) |
|---|---|---|
| Abrir con argumentos | `gdb --args ./prog a b` | `lldb -- ./prog a b` |
| Ejecutar | `run` | `run` |
| Breakpoint en función / línea | `b count_char` · `b count.c:11` | `b count_char` · `b count.c:11` |
| Breakpoint condicional | `b 11 if n == 2` | `br set -l 11 -c "n == 2"` |
| Listar breakpoints | `info breakpoints` | `br list` |
| Siguiente / entrar / salir de la función | `n` / `s` / `finish` | `n` / `s` / `finish` |
| Continuar | `c` | `c` |
| Pila de llamadas | `bt` | `bt` |
| Cambiar de marco | `frame 1` / `up` | `frame select 1` / `up` |
| Variables locales | `info locals` | `frame variable` (`v`) |
| Imprimir | `p n` | `p n` |
| Watchpoint | `watch n` | `watchpoint set variable n` |
| Cambiar una variable | `set var n = 0` | `expr n = 0` |
| Modo visual | `gdb -tui` | `gui` |
| Salir | `quit` | `quit` |

## Relacionadas

[[Valgrind y sanitizers]] · Cómo compila C · [[Punteros en C]] · [[Control de errores en C]] · [[Segmentos de memoria en C]] · [[Makefile y librerías estáticas]] · Vim

## Referencias

- [Debugging with GDB](https://sourceware.org/gdb/current/onlinedocs/gdb/) — manual oficial: `run`, `next`, `step`, `print`, `display`, `info locals`.
- [GDB: Breakpoints](https://sourceware.org/gdb/current/onlinedocs/gdb/Breakpoints.html) y [Setting Watchpoints](https://sourceware.org/gdb/current/onlinedocs/gdb/Set-Watchpoints.html) — breakpoints condicionales y `watch`.
- [GDB: Backtraces](https://sourceware.org/gdb/current/onlinedocs/gdb/Backtrace.html) — `bt` y `frame`.
- [GDB: TUI](https://sourceware.org/gdb/current/onlinedocs/gdb/TUI.html) — el modo visual `gdb -tui`.
- [GCC: Options for Debugging Your Program](https://gcc.gnu.org/onlinedocs/gcc/Debugging-Options.html) — qué hace `-g`.
- [GCC: Options That Control Optimization](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html) — `-O0` es el nivel por defecto.
- [GDB to LLDB command map](https://lldb.llvm.org/use/map.html) — tabla de equivalencias gdb ↔ lldb.
- Las salidas de ejemplo se obtuvieron con gdb en Ubuntu 22.04; las direcciones (`0x...`) cambian de una máquina a otra.
