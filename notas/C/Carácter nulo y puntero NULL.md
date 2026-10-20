---
tags: [c, libft, punteros, memoria, cadenas]
aliases: ["'\\0' vs NULL", "NULL vs '\\0'", "Carácter nulo"]
---
# Carácter nulo y puntero NULL

← Inicio · C

> Los dos valen **0**, pero no son lo mismo: `'\0'` es un **carácter** que marca el final de una **cadena**; `NULL` es un **puntero** que no apunta a nada. Usar uno en lugar del otro compila de milagro o no compila, y en 42 (`-Werror`) normalmente **no compila**.

> [!summary] Regla de oro
> - Si la casilla guarda un **carácter** (`char`) → `'\0'`.
> - Si la casilla guarda una **dirección** (`char *`, `t_list *`, `void *`…) → `NULL`.

---

## Carácter nulo `'\0'`

| | |
|---|---|
| **Qué es** | El carácter con código ASCII 0 (el byte `0x00`) |
| **Tipo** | Se guarda en un `char`. *Ojo:* la constante `'\0'` en sí es de tipo `int` en C (`sizeof('\0') == 4`), como todas las constantes de carácter |
| **Para qué** | Marcar el **final de una cadena**. Una «cadena» en C es solo un array de `char` que termina en `'\0'` |
| **Quién lo usa** | Todas las funciones de cadenas: [[ft_strlen]], [[ft_strlcpy]], [[ft_strchr]], [[ft_strdup]]… recorren hasta encontrarlo |

```c
char	str[5];

str[0] = 'h';
str[1] = 'o';
str[2] = 'l';
str[3] = 'a';
str[4] = '\0';   // fin de la cadena "hola"
```

```text
str:  [ 'h' ][ 'o' ][ 'l' ][ 'a' ][ '\0' ]
         0      1      2      3      4
```

> [!warning] Siempre hay que reservar un byte más
> `"hola"` tiene 4 letras pero ocupa **5** bytes. Olvidar ese `+ 1` en un `malloc` es el `Invalid write` más típico de valgrind (ver [[Valgrind y sanitizers]]).
> ```c
> word = malloc(sizeof(char) * (len + 1));
> ```

> [!note] No confundir con `'0'`
> `'0'` es el **dígito cero** (ASCII 48). `'\0'` es el carácter nulo (ASCII 0). Es justo lo que usa [[ft_atoi]]: `c - '0'`.

---

## Puntero nulo `NULL`

| | |
|---|---|
| **Qué es** | Un valor de puntero que garantiza **no apuntar a ninguna dirección válida** (repaso de punteros en [[Punteros en C]]) |
| **Tipo** | Una macro de `<stddef.h>` (también la traen `<stdlib.h>`, `<stdio.h>`, `<string.h>`…). En Linux con glibc vale `((void *)0)` |
| **Para qué** | 1. Decir que un puntero **no apunta a nada todavía** o que algo **falló** (`malloc` devuelve `NULL`). <br>2. Marcar el **final de un array de punteros** (el `char **` de [[ft_split]]). <br>3. Marcar el **final de una lista enlazada** (`next == NULL`, Parte 3; ver [[Listas enlazadas]]) |

```c
char	**tab;

tab = malloc(sizeof(char *) * 3);   // 2 palabras + 1 para el NULL final
if (!tab)
	return (NULL);                  // malloc falló → se avisa con NULL
tab[0] = ft_strdup("hola");
tab[1] = ft_strdup("mundo");
tab[2] = NULL;                      // fin del array de punteros
```

```text
tab:  [ ptr ]──► "hola\0"
      [ ptr ]──► "mundo\0"
      [ NULL ]   ← aquí se para quien recorra tab
```

> [!danger] Desreferenciar `NULL` = segfault
> `*ptr` o `ptr[0]` con `ptr == NULL` mata el programa (`SIGSEGV`). Por eso **siempre** se comprueba después de `malloc`: ver [[Control de errores en C]]. Para encontrar dónde ocurre: [[Depurar con gdb]].

---

## Los dos niveles a la vez: `ft_split`

En un `char **` aparecen **los dos**, cada uno en su nivel:

```c
tab[i][len] = '\0';   // dentro de una palabra: char  → fin de cadena
tab[i] = NULL;        // en el array:            char * → fin del array
```

| Expresión | Tipo | Terminador |
|---|---|---|
| `tab` | `char **` | — |
| `tab[i]` | `char *` | `NULL` |
| `tab[i][j]` | `char` | `'\0'` |

> [!tip] Truco para no fallar
> Cuenta los `*` del tipo de la **casilla** que estás rellenando: si tiene alguno, es un puntero → `NULL`. Si no tiene ninguno y es `char` → `'\0'`.

---

## Resumen

| | `'\0'` | `NULL` |
|---|---|---|
| **Es** | Un carácter | Un puntero |
| **Se guarda en** | `char` | `char *`, `void *`, `t_list *`… |
| **Marca** | Fin de una cadena | Fin de un array de punteros / de una lista, o «sin memoria» |
| **Ejemplo** | `word[len] = '\0';` | `tab[i] = NULL;` |
| **Comprobar** | `while (s[i] != '\0')` o `while (s[i])` | `if (ptr == NULL)` o `if (!ptr)` |

---

## Qué dice el compilador si los mezclas

Con `-Wall -Wextra -Werror` (comprobado en Ubuntu 22.04 con clang 12 y gcc 10):

| Código | gcc | clang (`cc` en 42) |
|---|---|---|
| `word[i] = NULL;` (puntero en un `char`) | ❌ error `-Wint-conversion` | ❌ error `-Wint-conversion` |
| `tab[i] = '\0';` (carácter en un `char *`) | ✅ compila sin aviso | ❌ error `-Wnon-literal-null-conversion` |

```text
# clang: word[i] = NULL;
error: incompatible pointer to integer conversion assigning to 'char'
       from 'void *' [-Werror,-Wint-conversion]

# clang: tab[i] = '\0';
error: expression which evaluates to zero treated as a null pointer constant
       of type 'char *' [-Werror,-Wnon-literal-null-conversion]

# gcc: word[i] = NULL;
error: assignment to 'char' from 'void *' makes integer from pointer
       without a cast [-Werror=int-conversion]
```

> [!info] ¿Por qué gcc acepta `tab[i] = '\0'`?
> Para el estándar C, **cualquier expresión constante entera que valga 0** es una «constante de puntero nulo», y `'\0'` lo es. Así que es C válido: `tab[i]` acaba valiendo `NULL`. Pero clang avisa porque casi siempre es un despiste, y en 42 se compila con `cc` (clang) y `-Werror`. Además, la [[La Norma|Norma]] y tu corrector esperan que se lea bien: **usa siempre el que corresponde**.

---

## Relacionadas

[[Arrays en C]] · [[Punteros en C]] · [[Segmentos de memoria en C]] · [[Control de errores en C]] · [[Depurar con gdb]] · [[ft_split]]

## Referencias

- [NULL — cppreference](https://en.cppreference.com/w/c/types/NULL) — definición de la macro y cabeceras que la traen.
- [Character constant — cppreference](https://en.cppreference.com/w/c/language/character_constant) — una constante de carácter es de tipo `int` en C.
- [Borrador del estándar C11 (N1570)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) — §6.3.2.3p3 (constante de puntero nulo), §7.1.1 (cadena terminada en carácter nulo).
- [ascii(7) — Linux man-pages](https://man7.org/linux/man-pages/man7/ascii.7.html) — códigos de `'\0'` (0) y `'0'` (48).
- [Clang Diagnostics Reference](https://clang.llvm.org/docs/DiagnosticsReference.html) — avisos `-Wint-conversion` y `-Wnon-literal-null-conversion`.
- Mensajes de error comprobados compilando en Ubuntu 22.04 (clang 12.0.1, gcc 10.5).
