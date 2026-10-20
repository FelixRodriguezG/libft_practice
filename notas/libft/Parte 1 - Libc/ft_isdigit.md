---
tags: [libft, libft/parte1, libft/caracteres]
funcion: ft_isdigit
original: "isdigit(3)"
cabecera: "<ctype.h>"
estado: hecho
---
# ft_isdigit

[[libft - Índice|← Índice]] · Parte 1 · Caracteres

> ¿Es un dígito decimal? Devuelve 1 si `c` es uno de los caracteres `'0'`…`'9'` y 0 si no.

## Explicación sencilla

El **carácter** `'7'` no es el **número** 7. El carácter `'7'` tiene el código ASCII 55; el número 7 es un carácter de control invisible (BEL).

| Entrada | Código | Salida |
|---|---|---|
| `'0'` | 48 | 1 |
| `'7'` | 55 | 1 |
| `7` | 7 | 0 |
| `'a'` | 97 | 0 |

```text
 carácter:  '/'  '0' '1' '2' ... '9'  ':'
 código:     47   48  49  50 ...  57   58
 salida:      0   └──────── 1 ──────┘   0
```

Como los dígitos son consecutivos, el valor numérico de un dígito es `c - '0'` (`'7' - '0'` = 55 − 48 = 7). Lo usarás en [[ft_atoi]].

## Prototipo

```c
// Original — isdigit(3)
#include <ctype.h>
int isdigit(int c);

// libft
int ft_isdigit(int c);
```

Consultar: `man 3 isdigit`

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

> [!quote] man 3 isdigit — DESCRIPTION
> These functions check whether c, which must have the value of an unsigned char or EOF, falls into a certain character class according to the specified locale.  The functions without the "_l" suffix perform the check based on the current locale.

> [!note] Traducción
> Estas funciones comprueban si c, que debe tener el valor de un unsigned char o EOF, pertenece a una determinada clase de caracteres según el locale especificado. Las funciones sin el sufijo "_l" hacen la comprobación según el locale actual.

> [!quote] man 3 isdigit — DESCRIPTION
> isdigit()
>        checks for a digit (0 through 9).

> [!note] Traducción
> isdigit()
>        comprueba si es un dígito (del 0 al 9).

> [!quote] man 3 isdigit — RETURN VALUE
> The values returned are nonzero if the character c falls into the tested class, and zero if not.

> [!note] Traducción
> Los valores devueltos son distintos de cero si el carácter c pertenece a la clase comprobada, y cero si no.

> [!quote] man 3 isdigit — NOTES
> The standards require that the argument c for these functions is either EOF or a value that is representable in the type unsigned char.  If the argument c is of type char, it must be cast to unsigned char

> [!note] Traducción
> Los estándares exigen que el argumento c de estas funciones sea EOF o un valor representable en el tipo unsigned char. Si el argumento c es de tipo char, debe convertirse (cast) a unsigned char

## Cómo implementarla

```text
si c está entre '0' y '9' (ambos incluidos) → devolver 1
si no                                       → devolver 0
```

## Puntos clave y casos límite

- Rango: `'0'`–`'9'` (48–57). No depende del locale.
- Compara con los caracteres `'0'` y `'9'`, no con los enteros 0 y 9.

### Errores típicos

- **Comparar con `0` y `9`** (enteros) en vez de `'0'` y `'9'` (caracteres): aceptarías caracteres de control y rechazarías los dígitos de verdad.
- **Usar `>` en lugar de `>=`**: `c > '0'` deja fuera el propio `'0'`. Prueba siempre los extremos del rango.
- **Devolver el valor de glibc** (2048 en Ubuntu): el subject pide 1.

## Relacionadas

[[ft_isalpha]] · [[ft_isalnum]] · [[ft_atoi]] · [[Tipos enteros y conversiones]]

## Referencias

- `man 3 isdigit` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [isdigit(3) — man7.org](https://man7.org/linux/man-pages/man3/isdigit.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- [ascii(7) — man7.org](https://man7.org/linux/man-pages/man7/ascii.7.html) — tabla ASCII con los códigos de cada carácter.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
