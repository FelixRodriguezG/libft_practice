---
tags: [libft, libft/parte1, libft/cadenas]
funcion: ft_strnstr
original: "strnstr(3bsd)"
cabecera: "<string.h> / <bsd/string.h>"
estado: hecho
---
# ft_strnstr

[[libft - Índice|← Índice]] · Parte 1 · Cadenas

> Busca una subcadena en los primeros len caracteres: devuelve un puntero al inicio de `little` dentro de `big`, siempre que aparezca **entera** antes de la posición `len`.

## Explicación sencilla

`len` es una «ventana»: solo se mira esa cantidad de caracteres de `big`, y la coincidencia tiene que caber completa dentro.

```text
 índice:  0   1   2   3   4   5   6   7   8   9   10
 big:   │ F │ o │ o │ ' '│ B │ a │ r │ ' '│ B │ a │ z │
                          └── "Bar" ─┘
 len = 4:  └──── ventana ───┘            → NULL ("Bar" no cabe)
 len = 7:  └──────── ventana ────────┘   → &big[4]  ("Bar Baz")
```

| Llamada | Retorno |
|---|---|
| `ft_strnstr("Foo Bar Baz", "Bar", 7)` | puntero a `"Bar Baz"` |
| `ft_strnstr("Foo Bar Baz", "Bar", 4)` | `NULL` |
| `ft_strnstr("abc", "", 0)` | `big` (`little` vacía) |

Devuelve una dirección dentro de `big` (ver [[Punteros en C]]).

## Prototipo

```c
// Original — strnstr(3bsd)
#include <string.h>
char *strnstr(const char *big, const char *little, size_t len);

// libft
char *ft_strnstr(const char *big, const char *little, size_t len);
```

Consultar: `man 3bsd strnstr`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3bsd strnstr — DESCRIPTION
> The strnstr() function locates the first occurrence of the null-terminated string little in the string big, where not more than len characters are searched.  Characters that appear after a '\0' character are not searched.  Since the strnstr() function is a FreeBSD specific API, it should only be used when portability is not a concern.

> [!note] Traducción
> La función strnstr() localiza la primera aparición de la cadena little (terminada en nulo) en la cadena big, buscando en no más de len caracteres. Los caracteres que aparecen después de un '\0' no se examinan. Como strnstr() es una API específica de FreeBSD, solo debe usarse cuando la portabilidad no importe.

> [!quote] man 3bsd strnstr — RETURN VALUES
> If little is an empty string, big is returned; if little occurs nowhere in big, NULL is returned; otherwise a pointer to the first character of the first occurrence of little is returned.

> [!note] Traducción
> Si little es una cadena vacía, se devuelve big; si little no aparece en big, se devuelve NULL; en otro caso se devuelve un puntero al primer carácter de la primera aparición de little.

## Cómo implementarla

```text
si little está vacía → devolver big
i = 0
mientras big[i] no sea '\0' y i < len:
    j = 0
    mientras little[j] no sea '\0'
          y big[i + j] == little[j]
          y i + j < len:
        j = j + 1
    si little[j] == '\0' → devolver la dirección de big[i]
    i = i + 1
devolver NULL
```

## Puntos clave y casos límite

- La coincidencia completa debe caber dentro de los `len` primeros caracteres.
- Ejemplo del man: `strnstr("Foo Bar Baz", "Bar", 4)` → NULL.
- Para probar la original en Linux: `#include <bsd/string.h>` y `-lbsd`.

### Errores típicos

- **Aceptar una coincidencia que se sale de la ventana**: falta la condición `i + j < len`.
- **No tratar `little` vacía**: debe devolver `big`, incluso con `len == 0`.
- **Ignorar el `'\0'` de `big`**: con `len` mayor que la cadena leerías fuera.
- **Usar `ft_strncmp(big + i, little, ft_strlen(little))` sin comprobar que `i + ft_strlen(little) <= len`**: vuelves a salirte de la ventana.

## Relacionadas

[[ft_strncmp]] · [[ft_strchr]] · [[Punteros en C]]

## Referencias

- `man 3bsd strnstr` — libbsd (libbsd-dev, Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [strnstr(3bsd) — libbsd (Debian)](https://manpages.debian.org/bookworm/libbsd-dev/strnstr.3bsd.en.html) — la misma página que `man 3bsd strnstr` (no existe en man7.org porque glibc no la incluye).
- [strnstr(3) — FreeBSD](https://man.freebsd.org/cgi/man.cgi?query=strnstr) — página original de FreeBSD.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
