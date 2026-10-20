---
tags: [c, static, ambito, variables, norma]
aliases: ["static en C", "Ámbito de variables"]
---
# Variables static y ámbito

← Inicio · C

> Toda variable de C tiene dos propiedades: su **ámbito** (desde qué parte del código se la puede nombrar) y su **duración** (cuánto tiempo existe en memoria). La palabra `static` cambia una de las dos según dónde la pongas: dentro de una función hace que la variable **sobreviva entre llamadas**; fuera de una función hace que la variable o la función **solo se vea en su fichero**.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Ámbito** (*scope*) | Zona del código donde un nombre es visible. Fuera de ella, el compilador no sabe qué es ese nombre |
| **Duración** (*storage duration*) | Cuánto vive la variable: mientras dura su bloque (automática) o todo el programa (estática) |
| **Bloque** | Todo lo que va entre `{` y `}` |
| **Unidad de traducción** | Un `.c` después de pegarle sus `#include`. Es lo que compila el compilador de una vez (ver Preprocesador y headers) |
| **Enlazado** (*linkage*) | Si un nombre se puede usar desde **otros** `.c` (externo) o solo desde el suyo (interno) |

## Los tres ámbitos que vas a usar

```c
#include <stdio.h>

int			g_contador;     /* ámbito de fichero + visible desde otros .c */
static int	g_privada;      /* ámbito de fichero, SOLO este .c            */

void	f(int param)        /* param: ámbito de bloque (la función)       */
{
	int	local;              /* ámbito de bloque: solo dentro de f         */

	local = param;
	{
		int	x;              /* solo dentro de estas llaves               */

		x = local;
	}
	/* aquí x ya no existe: error de compilación si la usas */
}
```

| Dónde se declara | Ámbito | Duración | ¿Se inicializa sola? |
|---|---|---|---|
| Dentro de una función (local) | El bloque | Automática: nace al entrar, muere al salir | ❌ Contiene basura |
| Dentro de una función con `static` | El bloque | **Todo el programa** | ✅ A `0` (o al valor que pongas), **una sola vez** |
| Fuera de toda función (global) | Todo el fichero, y otros `.c` con `extern` | Todo el programa | ✅ A `0` |
| Fuera de toda función con `static` | **Solo su fichero** | Todo el programa | ✅ A `0` |

Las locales normales viven en la **pila**; las `static` y las globales viven en los segmentos `.data`/`.bss`, que existen desde que arranca el programa hasta que termina (ver [[Segmentos de memoria en C]]).

### Una variable tapa a otra con el mismo nombre

Si declaras una variable con el mismo nombre en un bloque interior, la de dentro **tapa** (*shadowing*) a la de fuera mientras dura el bloque:

```c
#include <stdio.h>

int	main(void)
{
	int	x;

	x = 1;
	{
		int	x;

		x = 2;
		printf("dentro: %d\n", x);
	}
	printf("fuera: %d\n", x);
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror sombra.c -o sombra && ./sombra
dentro: 2
fuera: 1
```

Compila sin avisos, pero es una fuente de bugs. `-Wshadow` lo detecta:

```text
$ cc -Wall -Wextra -Werror -Wshadow sombra.c -o sombra
sombra.c:9:7: error: declaration shadows a local variable [-Werror,-Wshadow]
```

## `static` dentro de una función: memoria entre llamadas

Una variable local normal se crea de nuevo en cada llamada. Una local `static` se crea **una vez** y conserva su valor:

```c
#include <stdio.h>

int	contar(void)
{
	static int	llamadas = 0;
	int			normal;

	normal = 0;
	llamadas++;
	normal++;
	printf("llamadas = %d, normal = %d\n", llamadas, normal);
	return (llamadas);
}

int	main(void)
{
	contar();
	contar();
	contar();
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror contador.c -o contador && ./contador
llamadas = 1, normal = 1
llamadas = 2, normal = 1
llamadas = 3, normal = 1
```

```text
             llamada 1        llamada 2        llamada 3
pila:      [normal = 1]     [normal = 1]     [normal = 1]    ← se crea y destruye cada vez
.data:     [llamadas = 1] → [llamadas = 2] → [llamadas = 3]  ← siempre la misma casilla
```

> [!note] `= 0` en una `static` no se ejecuta en cada llamada
> `static int llamadas = 0;` no es una asignación que se repita: es el valor inicial, que se pone **antes de que arranque el programa**. Por eso solo puede ser una constante (no puedes escribir `static int n = strlen(s);`).

> [!info] La Norma y las `static` con valor inicial
> La Norma pide separar declaración y asignación en las variables locales, pero una `static` necesita el valor en la declaración. La norminette lo acepta: en el ejemplo de abajo solo marca `char frase[] = "..."` del `main` (`DECL_ASSIGN_LINE`), no `static char *resto = NULL;`. Si no pones valor, la `static` empieza en `0` igualmente.

### El caso de get_next_line

Este es el uso estrella de `static` en el cursus. `read` lee bloques de tamaño fijo, y casi nunca un bloque acaba justo en un `'\n'`. Lo que sobra tras la línea hay que **guardarlo para la siguiente llamada**. Una variable local se perdería al salir; una `static` no.

El mismo patrón en pequeño, con una función que devuelve palabra a palabra (como hace `strtok`):

```c
#include <stdio.h>

char	*siguiente_palabra(char *str)
{
	static char	*resto = NULL;
	char		*inicio;

	if (str)
		resto = str;
	if (!resto || !*resto)
		return (NULL);
	inicio = resto;
	while (*resto && *resto != ' ')
		resto++;
	if (*resto)
		*resto++ = '\0';
	return (inicio);
}

int	main(void)
{
	char	frase[] = "hola que tal";
	char	*p;

	p = siguiente_palabra(frase);
	while (p)
	{
		printf("[%s]\n", p);
		p = siguiente_palabra(NULL);
	}
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror lineas.c -o lineas && ./lineas
[hola]
[que]
[tal]
```

En get_next_line la idea es la misma: `static char *stash;` guarda lo leído de más. En el bonus, para varios descriptores a la vez, se usa un array: `static char *stash[MAX_FD];`, una casilla por cada fd (ver [[Descriptores de fichero y read]]).

> [!danger] La `static` también guarda lo que no quieres
> Si la `static` apunta a memoria de `malloc` y el programa deja de llamar a la función antes de llegar al final, esa memoria sigue reservada. Cuando `read` devuelve `0` o `-1`, **libera la `static` y ponla a `NULL`**: si no, Valgrind te marcará *still reachable* o un leak, y la siguiente llamada usará datos viejos.

### Devolver la dirección de una local: el error que `static` «arregla»

```c
char	*saludo(void)
{
	char	buf[] = "hola";

	return (buf);
}
```

```text
$ cc -Wall -Wextra -Werror dangling.c -o d
dangling.c:7:10: error: address of stack memory associated with local variable 'buf' returned [-Werror,-Wreturn-stack-address]
```

`buf` muere al salir de la función, así que el puntero devuelto apunta a basura. Con `static char buf[] = "hola";` funcionaría, pero **la solución correcta casi siempre es `malloc`** (como en [[ft_strdup]]): una `static` es una única casilla compartida por todas las llamadas, así que la siguiente llamada sobrescribe el resultado anterior.

## `static` fuera de una función: privado al fichero

Delante de una **función** o de una **variable global**, `static` no cambia la duración (ya era todo el programa): cambia el **enlazado**. El nombre deja de exportarse y solo existe para ese `.c`.

```c
/* modulo.c */
#include <stdio.h>

static int	g_total = 0;

static int	es_par(int n)
{
	return (n % 2 == 0);
}

void	sumar_si_par(int n)
{
	if (es_par(n))
		g_total += n;
}

int	total(void)
{
	return (g_total);
}
```

```c
/* main_modulo.c */
#include <stdio.h>

void	sumar_si_par(int n);
int		total(void);

int	main(void)
{
	int	i;

	i = 0;
	while (i <= 10)
		sumar_si_par(i++);
	printf("total = %d\n", total());
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror modulo.c main_modulo.c -o modulo && ./modulo
total = 30
```

Si otro `.c` intenta llamar a `es_par`, el compilador lo acepta (hay prototipo), pero el **enlazador** no la encuentra:

```text
$ cc -Wall -Wextra -Werror modulo.c main_mal.c -o mal
/usr/bin/ld: /tmp/main_mal-8bb131.o: in function `main':
main_mal.c:(.text+0x15): undefined reference to `es_par'
```

Con `nm` (lista los símbolos de un `.o`) se ve la diferencia: mayúscula = exportado, minúscula = privado.

```text
$ cc -c modulo.c -o modulo.o && nm modulo.o
0000000000000040 t es_par          ← static: t minúscula
0000000000000000 b g_total         ← static: b minúscula (.bss)
0000000000000000 T sumar_si_par    ← pública
0000000000000060 T total           ← pública
```

### Por qué libft exige helpers `static`

> [!quote] Subject de libft v19.3, «Consideraciones técnicas»
> «Declarar variables globales está prohibido.»
> «Si necesitas crear funciones auxiliares para descomponer una función más compleja, debes definirlas como static para restringir su alcance al archivo correspondiente.»

El motivo es práctico: [[ft_split]] y el `ft_printf` de un compañero pueden tener ambos un helper llamado `count_words`. Si los dos son públicos y acaban en el mismo ejecutable, el enlazador da `multiple definition of 'count_words'`. Con `static`, cada uno vive en su fichero y no chocan. Las funciones que **sí** van en `libft.h` (las `ft_*` del subject) no llevan `static`, porque otros `.c` tienen que poder llamarlas.

> [!summary] Regla de oro
> - ¿La función aparece en tu `.h`? → **sin** `static`.
> - ¿Es un helper que solo usa su propio `.c`? → **con** `static`.

## Variables globales y la Norma

> [!quote] La Norma v4, «Formato»
> «El nombre de una variable global debe comenzar con g_.»
> «El uso de variables globales que no están marcadas como const y static está prohibido y se considera un error de norma, a menos que el proyecto las permita explícitamente.»

Además, muchos subjects (libft, get_next_line…) prohíben **cualquier** global. Por qué no gustan:

- Cualquier función puede modificarlas: cuando falla algo, no sabes quién la cambió.
- Esconden dependencias: `total()` depende de `g_total` y no se ve en su prototipo.
- Hacen las funciones no **reentrantes** (no puedes usar dos a la vez de forma independiente).

Incluso una global `static` como la de `modulo.c` hace que la norminette avise:

```text
$ norminette modulo.c
Notice: GLOBAL_VAR_DETECTED  (line:   3, col:   1):	Global variable present in file. Make sure it is a reasonable choice.
```

> [!warning] Comprueba el subject
> Resumen basado en versiones públicas del subject; los detalles cambian entre versiones. Lo que manda es el PDF de tu intra.

## Errores frecuentes

> [!warning] Confundir los dos significados de `static`
> Dentro de una función: «dura todo el programa». Fuera: «solo se ve en este fichero». Es la misma palabra para dos cosas distintas.

> [!warning] Usar una local sin inicializar
> `int count; count++;` suma a basura. Solo las `static` y las globales empiezan a `0`. `-Wall` avisa en muchos casos (`variable 'count' is uninitialized`), pero no en todos.

> [!warning] Declarar una `static` en un `.h`
> `static int g_x;` en un header crea **una copia distinta en cada `.c`** que lo incluye. Cambiarla en uno no la cambia en los otros. Los `.h` llevan prototipos, no variables.

> [!warning] Olvidar `static` en un helper de libft
> No falla al compilar tu libft, pero es error de corrección según el subject, y puede chocar con funciones de otro proyecto al enlazar.

> [!question] Pregunta típica de evaluación
> **«¿Por qué tu get_next_line usa `static`? ¿Qué pasaría sin ella?»**
> Porque `read` lee más de lo que cabe en una línea y lo sobrante tiene que llegar a la siguiente llamada. Una local se destruye al volver de la función, así que se perdería ese trozo de texto. La `static` vive en `.data`/`.bss` todo el programa y conserva el puntero entre llamadas. Ojo: hay que liberarla y ponerla a `NULL` al llegar al final del fichero o en caso de error.

## Relacionadas

[[Segmentos de memoria en C]] · Preprocesador y headers · [[Descriptores de fichero y read]] · [[La Norma]] · [[Makefile y librerías estáticas]] · get_next_line · [[libft - Índice]]

## Referencias

- [cppreference: Storage duration and linkage](https://en.cppreference.com/w/c/language/storage_duration) — duración automática/estática, enlazado interno y externo, inicialización a cero.
- [cppreference: Scope](https://en.cppreference.com/w/c/language/scope) — ámbito de bloque y de fichero, ocultación de nombres.
- [nm(1), man7.org](https://man7.org/linux/man-pages/man1/nm.1.html) — significado de `T`/`t`, `B`/`b` (mayúscula global, minúscula local).
- [Beej's Guide to C Programming](https://beej.us/guide/bgc/) — capítulo sobre *storage-class specifiers* (`static`, `extern`).
- La Norma v4 (`Normativa 42/es.norm-2.pdf`) — prefijo `g_` y restricción de variables globales.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — prohibición de globales y helpers `static`.
- Salidas obtenidas con Ubuntu clang 12.0.1 en Ubuntu 22.04.
