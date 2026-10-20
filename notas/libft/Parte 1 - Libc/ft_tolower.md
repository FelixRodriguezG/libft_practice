---
tags: [libft, libft/parte1, libft/caracteres]
funcion: ft_tolower
original: "tolower(3)"
cabecera: "<ctype.h>"
estado: hecho
---
# ft_tolower

[[libft - Índice|← Índice]] · Parte 1 · Caracteres

> Mayúscula → minúscula. Si `c` es una letra mayúscula devuelve su minúscula; cualquier otro valor lo devuelve sin tocar.

## Explicación sencilla

| Entrada | Salida |
|---|---|
| `'A'` (65) | `'a'` (97) |
| `'Z'` (90) | `'z'` (122) |
| `'a'` | `'a'` (ya es minúscula) |
| `'5'` | `'5'` |
| `EOF` (−1) | −1 |

Es la inversa de [[ft_toupper]]: en ASCII la minúscula está 32 posiciones por encima de la mayúscula.

```text
 'A' 'B' 'C' ... 'Z'        'a' 'b' 'c' ... 'z'
  65  66  67 ...  90   +32   97  98  99 ... 122
```

## Prototipo

```c
// Original — tolower(3)
#include <ctype.h>
int tolower(int c);

// libft
int ft_tolower(int c);
```

Consultar: `man 3 tolower`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 tolower — DESCRIPTION
> These functions convert lowercase letters to uppercase, and vice versa.

> [!note] Traducción
> Estas funciones convierten letras minúsculas en mayúsculas, y viceversa.

> [!quote] man 3 tolower — DESCRIPTION
> If c is an uppercase letter, tolower() returns its lowercase equivalent, if a lowercase representation exists in the current locale.  Otherwise, it returns c.

> [!note] Traducción
> Si c es una letra mayúscula, tolower() devuelve su equivalente en minúscula, si existe una representación en minúscula en el locale actual. Si no, devuelve c.

> [!quote] man 3 tolower — DESCRIPTION
> If c is neither an unsigned char value nor EOF, the behavior of these functions is undefined.

> [!note] Traducción
> Si c no es ni un valor unsigned char ni EOF, el comportamiento de estas funciones es indefinido.

> [!quote] man 3 tolower — RETURN VALUE
> The value returned is that of the converted letter, or c if the conversion was not possible.

> [!note] Traducción
> El valor devuelto es el de la letra convertida, o c si la conversión no fue posible.

## Cómo implementarla

```text
si c está entre 'A' y 'Z' → devolver c + ('a' - 'A')     (es decir, c + 32)
si no                     → devolver c tal cual
```

## Puntos clave y casos límite

- Cualquier valor que no sea `'A'`–`'Z'` se devuelve sin cambios.

### Errores típicos

- **Sumar 32 sin comprobar el rango**: `ft_tolower('5')` devolvería `'U'` (53 + 32 = 85).
- **Devolver 0 cuando no es mayúscula**: hay que devolver `c` intacto.
- **Cambiar el tipo de retorno a `char`**: el prototipo es `int`.

## Relacionadas

[[ft_toupper]] · [[ft_isalpha]] · [[Tipos enteros y conversiones]]

## Referencias

- `man 3 tolower` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [tolower(3) — man7.org](https://man7.org/linux/man-pages/man3/tolower.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- [ascii(7) — man7.org](https://man7.org/linux/man-pages/man7/ascii.7.html) — tabla ASCII con los códigos de cada carácter.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
