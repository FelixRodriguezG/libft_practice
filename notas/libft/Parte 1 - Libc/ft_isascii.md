---
tags: [libft, libft/parte1, libft/caracteres]
funcion: ft_isascii
original: "isascii(3)"
cabecera: "<ctype.h>"
estado: hecho
---
# ft_isascii

[[libft - Índice|← Índice]] · Parte 1 · Caracteres

> ¿Está en la tabla ASCII (0–127)? Devuelve 1 si `c` es uno de los 128 códigos ASCII y 0 si no.

## Explicación sencilla

ASCII es una tabla de 128 caracteres numerados del 0 al 127 (caben en 7 bits). Incluye los caracteres de control (como `'\0'` o `'\n'`), los imprimibles y el 127 (DEL).

| Entrada | Salida |
|---|---|
| `'A'` (65) | 1 |
| `'\0'` (0) | 1 |
| `127` (DEL) | 1 |
| `128` | 0 |
| `-1` | 0 |

```text
 0 ....... 31   32 ......... 126   127  |  128 ...... 255   y negativos
  control         imprimibles      DEL  |   fuera de ASCII
 └───────────────── 1 ─────────────────┘  └──────────── 0 ───────────┘
```

## Prototipo

```c
// Original — isascii(3)
#include <ctype.h>
int isascii(int c);

// libft
int ft_isascii(int c);
```

Consultar: `man 3 isascii`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.
> 
> Para las funciones de clasificación de caracteres (isalpha, isdigit, isalnum, isascii, isprint), el valor de retorno debe ser:
> • 1 si el carácter cumple la condición comprobada.
> • 0 si el carácter no la cumple.

## Comportamiento según el manual

> [!quote] man 3 isascii — DESCRIPTION
> These functions check whether c, which must have the value of an unsigned char or EOF, falls into a certain character class according to the specified locale.  The functions without the "_l" suffix perform the check based on the current locale.

> [!note] Traducción
> Estas funciones comprueban si c, que debe tener el valor de un unsigned char o EOF, pertenece a una determinada clase de caracteres según el locale especificado. Las funciones sin el sufijo "_l" hacen la comprobación según el locale actual.

> [!quote] man 3 isascii — DESCRIPTION
> isascii()
>        checks whether c is a 7-bit unsigned char value that fits into the ASCII character set.

> [!note] Traducción
> isascii()
>        comprueba si c es un valor unsigned char de 7 bits que cabe en el juego de caracteres ASCII.

> [!quote] man 3 isascii — RETURN VALUE
> The values returned are nonzero if the character c falls into the tested class, and zero if not.

> [!note] Traducción
> Los valores devueltos son distintos de cero si el carácter c pertenece a la clase comprobada, y cero si no.

> [!quote] man 3 isascii — CONFORMING TO
> POSIX.1-2008 marks isascii() as obsolete, noting that it cannot be used portably in a localized application.

> [!note] Traducción
> POSIX.1-2008 marca isascii() como obsoleta, porque no puede usarse de forma portable en una aplicación localizada.

## Cómo implementarla

```text
si c está entre 0 y 127 (ambos incluidos) → devolver 1
si no                                     → devolver 0
```

## Puntos clave y casos límite

- Rango: 0–127 (incluye `'\0'` y los caracteres de control).
- A diferencia de las otras `is*`, la original acepta cualquier `int`: es solo una comprobación de rango.

### Errores típicos

- **Olvidar el 0**: `c > 0` deja fuera `'\0'`, que sí es ASCII.
- **Usar `c < 127`**: deja fuera DEL (127), que también es ASCII.
- **Confundirla con [[ft_isprint]]**: los caracteres de control son ASCII pero no imprimibles.

## Relacionadas

[[ft_isprint]] · [[Carácter nulo y puntero NULL]]

## Referencias

- `man 3 isascii` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [isascii(3) — man7.org](https://man7.org/linux/man-pages/man3/isascii.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- [ascii(7) — man7.org](https://man7.org/linux/man-pages/man7/ascii.7.html) — tabla ASCII con los códigos de cada carácter.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
