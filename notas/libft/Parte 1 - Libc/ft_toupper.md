---
tags: [libft, libft/parte1, libft/caracteres]
funcion: ft_toupper
original: "toupper(3)"
cabecera: "<ctype.h>"
estado: hecho
---
# ft_toupper

[[libft - Índice|← Índice]] · Parte 1 · Caracteres

> Minúscula → mayúscula. Si `c` es una letra minúscula devuelve su mayúscula; cualquier otro valor lo devuelve sin tocar.

## Explicación sencilla

| Entrada | Salida |
|---|---|
| `'a'` (97) | `'A'` (65) |
| `'z'` (122) | `'Z'` (90) |
| `'A'` | `'A'` (ya es mayúscula) |
| `'5'` | `'5'` |
| `EOF` (−1) | −1 |

En ASCII cada minúscula está exactamente 32 posiciones por encima de su mayúscula. En binario, la diferencia es un solo bit (el de valor 32; ver [[Operadores de bits]]):

```text
 'A' =  65 = 0100 0001
 'a' =  97 = 0110 0001
               ^
               bit de valor 32: la única diferencia
```

## Prototipo

```c
// Original — toupper(3)
#include <ctype.h>
int toupper(int c);

// libft
int ft_toupper(int c);
```

Consultar: `man 3 toupper`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 toupper — DESCRIPTION
> These functions convert lowercase letters to uppercase, and vice versa.

> [!note] Traducción
> Estas funciones convierten letras minúsculas en mayúsculas, y viceversa.

> [!quote] man 3 toupper — DESCRIPTION
> If c is a lowercase letter, toupper() returns its uppercase equivalent, if an uppercase representation exists in the current locale.  Otherwise, it returns c.

> [!note] Traducción
> Si c es una letra minúscula, toupper() devuelve su equivalente en mayúscula, si existe una representación en mayúscula en el locale actual. Si no, devuelve c.

> [!quote] man 3 toupper — DESCRIPTION
> If c is neither an unsigned char value nor EOF, the behavior of these functions is undefined.

> [!note] Traducción
> Si c no es ni un valor unsigned char ni EOF, el comportamiento de estas funciones es indefinido.

> [!quote] man 3 toupper — RETURN VALUE
> The value returned is that of the converted letter, or c if the conversion was not possible.

> [!note] Traducción
> El valor devuelto es el de la letra convertida, o c si la conversión no fue posible.

## Cómo implementarla

```text
si c está entre 'a' y 'z' → devolver c - ('a' - 'A')     (es decir, c - 32)
si no                     → devolver c tal cual
```

## Puntos clave y casos límite

- En ASCII la diferencia entre minúscula y mayúscula es 32 (`'a' - 'A'`).
- Cualquier valor que no sea `'a'`–`'z'` se devuelve sin cambios.

### Errores típicos

- **Restar 32 sin comprobar el rango**: `ft_toupper('A')` devolvería `'!'` (65 − 32 = 33).
- **Devolver 0 cuando no es minúscula**: hay que devolver `c` intacto.
- **Cambiar el tipo de retorno a `char`**: el prototipo es `int` (para poder devolver `EOF`). Ver [[Tipos enteros y conversiones]].

## Relacionadas

[[ft_tolower]] · [[ft_isalpha]] · [[Tipos enteros y conversiones]]

## Referencias

- `man 3 toupper` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [toupper(3) — man7.org](https://man7.org/linux/man-pages/man3/toupper.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- [ascii(7) — man7.org](https://man7.org/linux/man-pages/man7/ascii.7.html) — tabla ASCII con los códigos de cada carácter.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
