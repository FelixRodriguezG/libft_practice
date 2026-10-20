---
tags: [libft, libft/parte1, libft/cadenas]
funcion: ft_strlcpy
original: "strlcpy(3bsd)"
cabecera: "<string.h> / <bsd/string.h>"
estado: hecho
---
# ft_strlcpy

[[libft - Índice|← Índice]] · Parte 1 · Cadenas

> Copia segura con tamaño de buffer: copia `src` en `dst` sin escribir más de `size` bytes (incluido el `'\0'`) y devuelve la longitud de `src`.

## Explicación sencilla

`size` es el tamaño **total** del buffer de destino. Como siempre hay que reservar un byte para el `'\0'` (ver [[Carácter nulo y puntero NULL]]), caben como mucho `size - 1` caracteres.

```c
char	buf[5];
size_t	r;

r = ft_strlcpy(buf, "Barcelona", 5);
```

```text
 src:  │ B │ a │ r │ c │ e │ l │ o │ n │ a │ \0 │     strlen(src) = 9
 buf:  │ B │ a │ r │ c │ \0 │                         size = 5 → 4 letras + '\0'
 r = 9   →   9 >= 5   →   la copia se ha truncado
```

| Llamada | `dst` después | Retorno |
|---|---|---|
| `ft_strlcpy(buf, "Barcelona", 5)` | `"Barc"` | 9 |
| `ft_strlcpy(buf, "hola", 10)` | `"hola"` | 4 |
| `ft_strlcpy(buf, "abc", 0)` | sin cambios | 3 |

## Prototipo

```c
// Original — strlcpy(3bsd)
#include <string.h>
size_t strlcpy(char *dst, const char *src, size_t size);

// libft
size_t ft_strlcpy(char *dst, const char *src, size_t size);
```

Consultar: `man 3bsd strlcpy`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.
> 
> Algunas de las funciones que debes rehacer, como strlcpy, strlcat y bzero, no están incluidas por defecto en la biblioteca GNU C (glibc). Para compararlas con la versión estándar del sistema, puede ser necesario incluir <bsd/string.h> y compilar con la opción -lbsd.

## Comportamiento según el manual

> [!quote] man 3bsd strlcpy — DESCRIPTION
> The strlcpy() and strlcat() functions copy and concatenate strings respectively.  They are designed to be safer, more consistent, and less error prone replacements for strncpy(3) and strncat(3).  Unlike those functions, strlcpy() and strlcat() take the full size of the buffer (not just the length) and guarantee to NUL-terminate the result (as long as size is larger than 0 or, in the case of strlcat(), as long as there is at least one byte free in dst).  Note that a byte for the NUL should be included in size.  Also note that strlcpy() and strlcat() only operate on true "C" strings.  This means that for strlcpy() src must be NUL-terminated and for strlcat() both src and dst must be NUL-terminated.

> [!note] Traducción
> Las funciones strlcpy() y strlcat() copian y concatenan cadenas respectivamente. Están diseñadas como sustitutas más seguras, coherentes y menos propensas a errores de strncpy(3) y strncat(3). A diferencia de esas funciones, strlcpy() y strlcat() reciben el tamaño completo del buffer (no solo la longitud) y garantizan que el resultado termina en NUL (siempre que size sea mayor que 0 o, en el caso de strlcat(), siempre que quede al menos un byte libre en dst). Ten en cuenta que size debe incluir un byte para el NUL. Además, strlcpy() y strlcat() solo operan sobre cadenas "C" auténticas: para strlcpy() src debe terminar en NUL, y para strlcat() tanto src como dst deben terminar en NUL.

> [!quote] man 3bsd strlcpy — DESCRIPTION
> The strlcpy() function copies up to size - 1 characters from the NUL-terminated string src to dst, NUL-terminating the result.

> [!note] Traducción
> La función strlcpy() copia hasta size - 1 caracteres de la cadena src (terminada en NUL) a dst, terminando el resultado en NUL.

> [!quote] man 3bsd strlcpy — RETURN VALUES
> The strlcpy() and strlcat() functions return the total length of the string they tried to create.  For strlcpy() that means the length of src.  For strlcat() that means the initial length of dst plus the length of src.  While this may seem somewhat confusing, it was done to make truncation detection simple.

> [!note] Traducción
> strlcpy() y strlcat() devuelven la longitud total de la cadena que intentaron crear. Para strlcpy() es la longitud de src. Para strlcat() es la longitud inicial de dst más la longitud de src. Aunque pueda parecer confuso, se hizo así para que detectar el truncamiento sea sencillo.

## Cómo implementarla

```text
len = longitud de src
si size == 0:
    devolver len                    (no se escribe nada)
i = 0
mientras src[i] no sea '\0' y i < size - 1:
    dst[i] = src[i]
    i = i + 1
dst[i] = '\0'
devolver len
```

## Puntos clave y casos límite

- Siempre devuelve `ft_strlen(src)`, aunque se trunque.
- Con `size == 0` no escribe nada en `dst` (ni siquiera el `'\0'`).
- Truncamiento: si el valor devuelto `>= size`, la copia se truncó.
- En Linux no está en glibc 2.35: para probar la original usa `#include <bsd/string.h>` y compila con `-lbsd`.

### Errores típicos

- **Devolver los caracteres copiados** en vez de `ft_strlen(src)`: el retorno sirve para detectar truncamiento, así que es siempre la longitud de `src`.
- **Calcular `size - 1` con `size == 0`**: `size_t` no tiene negativos; `0 - 1` da el valor máximo (`SIZE_MAX`) y copiarías sin límite. Por eso el caso `size == 0` va primero. Ver [[Tipos enteros y conversiones]].
- **Olvidar el `'\0'` final** cuando sí hay sitio.
- **Usar `strncpy` como modelo**: `strncpy` rellena con ceros hasta `n` y no garantiza el `'\0'`; `strlcpy` no rellena y sí lo garantiza (si `size > 0`).

## Relacionadas

[[ft_strlcat]] · [[ft_strlen]] · [[ft_memcpy]] · [[Carácter nulo y puntero NULL]]

## Referencias

- `man 3bsd strlcpy` — libbsd (libbsd-dev, Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [strlcpy(3) — man7.org](https://man7.org/linux/man-pages/man3/strlcpy.3.html) — versión añadida a glibc 2.38 (Ubuntu 22.04 trae glibc 2.35, que aún no la incluye).
- [strlcpy(3) — OpenBSD](https://man.openbsd.org/strlcpy) — página original de BSD.
- [strlcpy(3bsd) — libbsd (Debian)](https://manpages.debian.org/bookworm/libbsd-dev/strlcpy.3bsd.en.html) — la misma página que `man 3bsd strlcpy`.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
