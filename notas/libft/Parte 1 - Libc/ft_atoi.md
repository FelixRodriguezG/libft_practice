---
tags: [libft, libft/parte1, libft/conversion]
funcion: ft_atoi
original: "atoi(3)"
cabecera: "<stdlib.h>"
estado: hecho
---
# ft_atoi

[[libft - Índice|← Índice]] · Parte 1 · Conversión

> Cadena → int: convierte el número escrito al principio de una cadena (`"  -42abc"`) en el entero que representa (−42).

## Explicación sencilla

La cadena se lee en tres fases y lo que sobra se ignora:

```text
 "   -42abc"

 ' '  ' '  ' '  '-'  '4'  '2'  'a'  'b'  'c'
 └── espacios ──┘ signo └─dígitos─┘ └─ se ignora ─┘

 resultado: -42
```

Cada dígito nuevo desplaza los anteriores una posición: `resultado = resultado * 10 + (c - '0')`.

```text
 "123":   0 → 0*10 + 1 = 1 → 1*10 + 2 = 12 → 12*10 + 3 = 123
```

| Entrada | Salida |
|---|---|
| `"42"` | 42 |
| `"   -42abc"` | −42 |
| `"+-42"` | 0 |
| `"- 42"` | 0 (el espacio corta tras el signo) |
| `"abc42"` | 0 |
| `"-2147483648"` | −2147483648 (`INT_MIN`) |

## Prototipo

```c
// Original — atoi(3)
#include <stdlib.h>
int atoi(const char *nptr);

// libft
int ft_atoi(const char *nptr);
```

Consultar: `man 3 atoi`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 atoi — DESCRIPTION
> The atoi() function converts the initial portion of the string pointed to by nptr to int.  The behavior is the same as
>
>     strtol(nptr, NULL, 10);
>
> except that atoi() does not detect errors.

> [!note] Traducción
> La función atoi() convierte la parte inicial de la cadena apuntada por nptr a int. El comportamiento es el mismo que
>
>     strtol(nptr, NULL, 10);
>
> salvo que atoi() no detecta errores.

> [!quote] man 3 atoi — RETURN VALUE
> The converted value or 0 on error.

> [!note] Traducción
> El valor convertido, o 0 en caso de error.

> [!quote] DESCRIPTION — man 3 strtol
> The string may begin with an arbitrary amount of white space (as determined by isspace(3)) followed by a single optional '+' or '-' sign.
>
> The remainder of the string is converted to a long value in the obvious manner, stopping at the first character which is not a valid digit in the given base.

> [!note] Traducción
> La cadena puede empezar con cualquier cantidad de espacios en blanco (según isspace(3)) seguida de un único signo opcional '+' o '-'.
>
> El resto de la cadena se convierte a long de la forma obvia, deteniéndose en el primer carácter que no sea un dígito válido en la base indicada.

## Cómo implementarla

```text
i = 0
saltar mientras nptr[i] sea ' ', '\t', '\n', '\v', '\f' o '\r'
signo = 1
si nptr[i] es '-' o '+':
    si es '-' → signo = -1
    i = i + 1
resultado = 0                       (en un tipo más grande que int, p. ej. long)
mientras nptr[i] sea un dígito:
    resultado = resultado * 10 + (nptr[i] - '0')
    i = i + 1
devolver resultado * signo convertido a int
```

## Puntos clave y casos límite

- Espacios válidos (isspace en locale "C"): `' '`, `'\t'`, `'\n'`, `'\v'`, `'\f'`, `'\r'` (9–13 y 32).
- Un **único** signo: `"+-42"` y `"--42"` → 0.
- Se detiene en el primer no-dígito: `"42abc"` → 42, `"abc42"` → 0.
- El desbordamiento es comportamiento indefinido en la original; `INT_MIN` (`"-2147483648"`) debe funcionar.

### Errores típicos

- **Aceptar varios signos** (`"--42"`, `"+-42"`): solo se permite uno; si hay dos, el resultado es 0.
- **Saltar espacios también después del signo**: `"- 42"` → 0.
- **Olvidar `'\v'` y `'\f'`** en la lista de espacios: `isspace` acepta del 9 al 13 y el 32.
- **Acumular en `int` y luego multiplicar por el signo**: `2147483648` no cabe en `int` (desbordamiento de entero con signo = comportamiento indefinido), así que `INT_MIN` funciona «de casualidad». Acumula en `long` o resta en negativo. Ver [[Tipos enteros y conversiones]].
- **Usar tu `ft_isdigit`** está bien; **usar `isspace` de la libc**, no (es externa).

## Relacionadas

[[ft_itoa]] · [[ft_isdigit]] · [[Tipos enteros y conversiones]]

## Referencias

- `man 3 atoi` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [atoi(3) — man7.org](https://man7.org/linux/man-pages/man3/atoi.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- [strtol(3) — man7.org](https://man7.org/linux/man-pages/man3/strtol.3.html) — reglas de espacios, signo y dígitos que hereda `atoi`.
- [isspace(3) — man7.org](https://man7.org/linux/man-pages/man3/isspace.3.html) — qué caracteres cuentan como espacio en blanco.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
