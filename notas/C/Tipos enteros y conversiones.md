---
tags: [c, tipos, enteros, overflow, conversiones, libft]
aliases: ["Tipos enteros", "size_t", "signed y unsigned", "Overflow"]
---
# Tipos enteros y conversiones

← Inicio · C

> C tiene varios tipos enteros que se diferencian en **cuántos bytes ocupan** y en si admiten **negativos** (`signed`) o no (`unsigned`). Cuando mezclas tipos, C convierte los valores automáticamente con reglas que a veces sorprenden. Entenderlas explica por qué [[ft_itoa]] falla con `INT_MIN`, por qué [[ft_calloc]] debe vigilar `SIZE_MAX` y por qué las funciones `is*` reciben un `int`.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Bit / byte** | Un bit es un 0 o un 1. Un byte son 8 bits (en todas las máquinas que usarás) |
| **`signed`** | El tipo admite negativos. Es lo que son `int`, `short`, `long` por defecto |
| **`unsigned`** | Solo valores ≥ 0, pero llega al doble de alto |
| **Complemento a dos** | La forma en que el procesador guarda los negativos. Hace que el rango sea asimétrico: hay un negativo más que positivos |
| **Overflow** (desbordamiento) | El resultado no cabe en el tipo |
| **Promoción** | Conversión automática de tipos pequeños (`char`, `short`) a `int` antes de operar |
| **Cast** | Conversión explícita que escribes tú: `(unsigned char)c` |
| **Comportamiento indefinido** (*UB*) | El estándar no dice qué pasa: puede funcionar, dar basura o crashear |

## Tamaños y límites en tu máquina

El estándar solo garantiza **mínimos**; los tamaños reales dependen de la plataforma. Pregúntaselo al compilador:

```c
#include <stdio.h>
#include <limits.h>
#include <stdint.h>

int	main(void)
{
	printf("char      %zu byte  [%d, %d]\n", sizeof(char), CHAR_MIN, CHAR_MAX);
	printf("short     %zu bytes [%d, %d]\n", sizeof(short), SHRT_MIN, SHRT_MAX);
	printf("int       %zu bytes [%d, %d]\n", sizeof(int), INT_MIN, INT_MAX);
	printf("long      %zu bytes [%ld, %ld]\n", sizeof(long), LONG_MIN, LONG_MAX);
	printf("unsigned  %zu bytes [0, %u]\n", sizeof(unsigned int), UINT_MAX);
	printf("size_t    %zu bytes [0, %zu]\n", sizeof(size_t), SIZE_MAX);
	printf("void *    %zu bytes\n", sizeof(void *));
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror int1.c -o int1 && ./int1
char      1 byte  [-128, 127]
short     2 bytes [-32768, 32767]
int       4 bytes [-2147483648, 2147483647]
long      8 bytes [-9223372036854775808, 9223372036854775807]
unsigned  4 bytes [0, 4294967295]
size_t    8 bytes [0, 18446744073709551615]
void *    8 bytes
```

(Linux x86_64. En Windows, `long` ocupa 4 bytes.)

| Cabecera | Qué trae |
|---|---|
| `<limits.h>` | `CHAR_MIN/MAX`, `INT_MIN/MAX`, `UINT_MAX`, `LONG_MIN/MAX`… |
| `<stdint.h>` | `SIZE_MAX`, y tipos de tamaño fijo: `int8_t`, `uint8_t`, `int32_t`, `uint32_t`, `int64_t`… |
| `<stddef.h>` | `size_t`, `NULL`, `offsetof` |

> [!note] ¿`char` tiene signo?
> Depende de la plataforma. En Linux x86_64 y en macOS `char` es `signed` (de −128 a 127); en Linux ARM es `unsigned`. Si te importa, escribe `signed char` o `unsigned char`.

## `size_t`

`size_t` es el tipo **sin signo** que devuelve `sizeof` y que usan todas las funciones de tamaños: [[ft_strlen]], [[ft_memcpy]], [[ft_strlcpy]], `malloc`… Es lo bastante grande para medir cualquier objeto en memoria (8 bytes en 64 bits).

- Se imprime con `%zu` (ver printf).
- Como no tiene signo, **nunca es negativo**: `while (len >= 0)` con un `size_t` es un bucle infinito.

## Signed y unsigned: lo que sorprende

```c
#include <stdio.h>
#include <limits.h>

int	main(void)
{
	unsigned int	u;
	char			c;
	unsigned char	uc;
	int				i;

	u = 0;
	u = u - 1;
	printf("0u - 1         = %u\n", u);
	c = (char)200;
	uc = 200;
	printf("(char)200      = %d\n", c);
	printf("(uchar)200     = %d\n", uc);
	i = -1;
	if ((size_t)i < sizeof(int))
		printf("-1 < 4: cierto\n");
	else
		printf("-1 < 4: FALSO (-1 se convirtio a %zu)\n", (size_t)i);
	printf("-INT_MIN como long = %ld\n", -(long)INT_MIN);
	printf("'a' + 1 = %d (tipo int, sizeof = %zu)\n", 'a' + 1, sizeof('a' + 1));
	return (0);
}
```

```text
0u - 1         = 4294967295
(char)200      = -56
(uchar)200     = 200
-1 < 4: FALSO (-1 se convirtio a 18446744073709551615)
-INT_MIN como long = 2147483648
'a' + 1 = 98 (tipo int, sizeof = 4)
```

Qué ha pasado:

1. **Los `unsigned` dan la vuelta**: `0 - 1` no es −1, sino el máximo (`UINT_MAX`). Esto está **definido** por el estándar (aritmética módulo 2ⁿ).
2. **200 no cabe en un `char` con signo**: el byte `0xC8` se interpreta como −56.
3. **Comparar `int` con `size_t`**: el `int` se convierte a `size_t` y −1 se vuelve enorme. En el código original (sin el cast), clang no deja compilar:

```text
int2.c:19:8: error: comparison of integers of different signs: 'int' and 'unsigned long' [-Werror,-Wsign-compare]
        if (i < sizeof(int))
            ~ ^ ~~~~~~~~~~~
```

4. **`'a' + 1` es un `int`**: antes de operar, todo lo que sea más pequeño que `int` se **promociona** a `int`.

## Promociones y conversiones automáticas

Reglas simplificadas (las completas están en el estándar, §6.3.1):

1. **Promoción entera**: `char`, `unsigned char`, `short` → `int` en cualquier operación aritmética.
2. **Conversiones aritméticas habituales**: si mezclas dos tipos, el «menor» se convierte al «mayor» (`int` → `long`, `int` → `double`).
3. **Si uno es `unsigned` y del mismo tamaño o mayor**, el con signo se convierte a `unsigned`. Aquí nacen los −1 gigantes.
4. **Asignar a un tipo más pequeño trunca**: `char c = 300;` se queda con los 8 bits bajos.

> [!tip] Lo que activa `-Wall -Wextra`
> `-Wsign-compare` (comparaciones signed/unsigned) viene con `-Wextra`. `-Wconversion` (pérdidas por truncar) **no** viene incluido; puedes añadirlo mientras desarrollas para que te avise, sin dejarlo en el Makefile entregado.

## Casts

Un **cast** `(tipo)valor` le dice al compilador «convierte esto, sé lo que hago». Usos legítimos en libft:

| Cast | Dónde | Para qué |
|---|---|---|
| `(unsigned char *)s` | [[ft_memset]], [[ft_memcmp]], [[ft_memchr]] | Recorrer bytes y compararlos como 0–255 |
| `(unsigned char)c` | [[ft_strchr]], [[ft_memset]] | El `int c` se trata como un byte |
| `(long)n` o `long nb = n;` | [[ft_itoa]], [[ft_putnbr_fd]] | Poder hacer `-n` con `INT_MIN` |
| `(char *)s` | [[ft_strchr]], [[ft_strnstr]] | Devolver un `char *` a partir de un `const char *` |

> [!warning] Un cast no arregla un overflow
> `(long)(a * b)` con `a` y `b` `int` multiplica **primero** en `int` (desborda) y convierte después. Lo correcto es `(long)a * b`.

## Overflow en la libft

### `ft_itoa` y `ft_putnbr_fd` con `INT_MIN`

`INT_MIN` es −2147483648, pero `INT_MAX` es 2147483647: **−INT_MIN no cabe en un `int`**. Desbordar un `int` con signo es comportamiento indefinido. Un `itoa` ingenuo:

```c
static char	*itoa_mal(int n, char *buf)
{
	int	len;
	int	tmp;

	if (n < 0)
		n = -n;
	tmp = n;
	len = 1;
	while (tmp >= 10)
	{
		tmp /= 10;
		len++;
	}
	buf[len] = '\0';
	while (len-- > 0)
	{
		buf[len] = '0' + n % 10;
		n /= 10;
	}
	return (buf);
}
```

```text
$ ./int3
itoa_mal(INT_MIN) = "("
con long: -INT_MIN = 2147483648

$ cc -Wall -Wextra -Werror -fsanitize=undefined int3.c -o int3u && ./int3u
int3.c:10:7: runtime error: negation of -2147483648 cannot be represented in type 'int'; cast to an unsigned type to negate this value to itself
```

En esta máquina `-n` deja `n` en −2147483648, el bucle cree que tiene 1 cifra y `'0' + (-8)` es `'('`. Soluciones habituales:

- Copiar a un `long` antes de cambiar el signo (`long nb = n; nb = -nb;`).
- Tratar `INT_MIN` como caso especial y devolver `ft_strdup("-2147483648")`.
- Trabajar con negativos: `n % 10` da un resto negativo; usar `-(n % 10)`.

> [!tip] `-fsanitize=undefined`
> Compila tus tests con `-fsanitize=undefined` (o `-fsanitize=address,undefined`) y los desbordamientos con signo aparecen como `runtime error`. Ver [[Valgrind y sanitizers]].

### `ft_atoi` con números que no caben

El `atoi` real no comprueba overflow: con `"99999999999"` el resultado no está definido. Tu [[ft_atoi]] puede acumular en un `long` y devolver `(int)` del resultado; lo importante es no crashear. En **push_swap** sí tendrás que detectar argumentos fuera de `[INT_MIN, INT_MAX]` y dar error, y para eso acumular en `long` es lo más sencillo.

### `ft_calloc` y `SIZE_MAX`

`calloc(nmemb, size)` reserva `nmemb * size` bytes. Si esa multiplicación desborda `size_t`, «da la vuelta» y reservarías **menos** de lo pedido:

```c
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

int	main(void)
{
	size_t	nmemb;
	size_t	size;

	nmemb = SIZE_MAX / 2 + 2;
	size = 2;
	printf("nmemb * size = %zu\n", nmemb * size);
	printf("desborda? %s\n", (size != 0 && nmemb > SIZE_MAX / size) ? "si" : "no");
	printf("calloc real: %p\n", calloc(nmemb, size));
	return (0);
}
```

```text
nmemb * size = 2
desborda? si
calloc real: (nil)
```

¡Pedir trillones de bytes se convertiría en pedir 2! El `calloc` de glibc lo detecta y devuelve `NULL`. Tu [[ft_calloc]] debería hacer la misma comprobación **dividiendo**, que no desborda:

```c
if (size != 0 && nmemb > SIZE_MAX / size)
	return (NULL);
```

## Por qué `is*` reciben `int` y se pasa `unsigned char`

Los prototipos son `int ft_isalpha(int c)`, `int ft_toupper(int c)`… ¿Por qué `int` y no `char`?

- Vienen de `<ctype.h>`, que debe aceptar **todos** los valores de `unsigned char` (0–255) **y** `EOF` (−1). Un `char` no puede representar las dos cosas a la vez; un `int` sí.
- Según el estándar, pasar cualquier otro valor negativo es comportamiento indefinido. Si `char` tiene signo, un carácter como `'é'` en Latin-1 (`0xE9`) vale **−23**:

```c
char	c;

c = '\xe9';
printf("c como int: %d\n", c);
printf("isalpha((unsigned char)c) = %d\n", isalpha((unsigned char)c));
```

```text
c como int: -23
isalpha((unsigned char)c) = 0
```

Por eso, al llamar a `isalpha`/`ft_isalpha` con un `char`, lo correcto es convertirlo a `(unsigned char)` primero. Y por eso [[ft_isalpha]] debe devolver 0 (y no crashear) con valores fuera de 0–127.

## Errores frecuentes

| Error | Consecuencia |
|---|---|
| `while (len >= 0)` con `size_t` | Bucle infinito |
| `int i` comparado con `ft_strlen(s)` | `-Wsign-compare` → no compila con `-Werror`. Usa `size_t i` |
| `-n` con `n == INT_MIN` | UB; resultado basura en [[ft_itoa]] |
| `nmemb * size` sin comprobar | Reserva de menos y escrituras fuera del bloque |
| `%d` para un `size_t` o un `long` | Aviso de formato (`-Wformat`); usa `%zu` y `%ld` |
| Comparar bytes como `char` en `ft_memcmp` | `0x80` sale «menor» que `0x01`. Hay que usar `unsigned char` |

> [!question] Pregunta típica de evaluación
> «¿Qué pasa si llamo a tu `ft_itoa` con `INT_MIN`? ¿Por qué no basta con `n = -n`?»
> Porque `INT_MIN` es −2147483648 y el mayor `int` es 2147483647: el opuesto no cabe y desbordar un `int` con signo es comportamiento indefinido. Mi `ft_itoa` copia `n` a un `long` antes de cambiar el signo (o trata `INT_MIN` aparte).

## Relacionadas

[[Operadores de bits]] · [[Punteros en C]] · [[ft_atoi]] · [[ft_itoa]] · [[ft_calloc]] · [[ft_putnbr_fd]] · [[ft_isalpha]] · [[ft_memcmp]] · printf · [[Valgrind y sanitizers]] · Cómo compila C

## Referencias

- [Arithmetic types — cppreference](https://en.cppreference.com/w/c/language/arithmetic_types) — tipos enteros, tamaños mínimos y signo de `char`.
- [Numeric limits — cppreference](https://en.cppreference.com/w/c/types/limits) — macros de `<limits.h>` y `<stdint.h>`.
- [Fixed width integer types — cppreference](https://en.cppreference.com/w/c/types/integer) — `int32_t`, `uint8_t`, `SIZE_MAX`…
- [size_t — cppreference](https://en.cppreference.com/w/c/types/size_t).
- [Implicit conversions — cppreference](https://en.cppreference.com/w/c/language/conversion) — promoción entera y conversiones aritméticas habituales.
- [isalpha — cppreference](https://en.cppreference.com/w/c/string/byte/isalpha) e [isalpha(3) — man7.org](https://man7.org/linux/man-pages/man3/isalpha.3.html) — el argumento debe ser `EOF` o representable como `unsigned char`.
- [calloc(3) — man7.org](https://man7.org/linux/man-pages/man3/calloc.3.html) — `calloc` devuelve error si `nmemb * size` desborda.
- [Beej's Guide to C: Types II](https://beej.us/guide/bgc/html/split/types-ii-way-more-types.html) y [Types III: Conversions](https://beej.us/guide/bgc/html/split/types-iii-conversions.html).
- [N1570 (borrador C11)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) — §5.2.4.2.1 (límites), §6.2.5p9 (los `unsigned` no desbordan: aritmética módulo), §6.3.1.1 y §6.3.1.8 (promociones y conversiones), §6.5p5 (overflow con signo es UB), §7.4p1 (argumento de `<ctype.h>`).
- [Two's complement — Wikipedia](https://en.wikipedia.org/wiki/Two%27s_complement) — por qué el rango es asimétrico.
- Ejemplos compilados con `cc` (Ubuntu clang 12.0.1) en Linux x86_64.
