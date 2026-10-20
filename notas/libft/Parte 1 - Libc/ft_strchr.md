---
tags: [libft, libft/parte1, libft/cadenas]
funcion: ft_strchr
original: "strchr(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_strchr

[[libft - Índice|← Índice]] · Parte 1 · Cadenas

> Primera aparición de un carácter: devuelve un puntero al primer `c` que haya en `s`, o `NULL` si no está.

## Explicación sencilla

No crea ninguna cadena nueva: devuelve la **dirección** de una posición dentro de `s` (ver [[Punteros en C]]). Si imprimes ese puntero con `%s`, ves la cadena desde ahí hasta el final.

```text
 s ──►│ h │ o │ l │ a │ ' '│ t │ u │ \0 │
                                ▲
             ft_strchr(s, 't') ─┘        printf("%s") → "tu"
```

| Llamada | Retorno |
|---|---|
| `ft_strchr("hola tu", 't')` | puntero a `"tu"` |
| `ft_strchr("hola", 'z')` | `NULL` |
| `ft_strchr("hola", '\0')` | puntero al `'\0'` (`s + 4`) |

El `'\0'` cuenta como parte de la cadena; [[Carácter nulo y puntero NULL]] explica la diferencia entre `'\0'` y `NULL`.

## Prototipo

```c
// Original — strchr(3)
#include <string.h>
char *strchr(const char *s, int c);

// libft
char *ft_strchr(const char *s, int c);
```

Consultar: `man 3 strchr`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 strchr — DESCRIPTION
> The strchr() function returns a pointer to the first occurrence of the character c in the string s.

> [!note] Traducción
> La función strchr() devuelve un puntero a la primera aparición del carácter c en la cadena s.

> [!quote] man 3 strchr — DESCRIPTION
> Here "character" means "byte"; these functions do not work with wide or multibyte characters.

> [!note] Traducción
> Aquí "carácter" significa "byte"; estas funciones no funcionan con caracteres anchos ni multibyte.

> [!quote] man 3 strchr — RETURN VALUE
> The strchr() and strrchr() functions return a pointer to the matched character or NULL if the character is not found.  The terminating null byte is considered part of the string, so that if c is specified as '\0', these functions return a pointer to the terminator.

> [!note] Traducción
> strchr() y strrchr() devuelven un puntero al carácter encontrado, o NULL si no se encuentra. El byte nulo final se considera parte de la cadena, así que si c es '\0', estas funciones devuelven un puntero al terminador.

## Cómo implementarla

```text
ch = c convertido a char
i = 0
repetir:
    si s[i] == ch   → devolver la dirección de s[i]
    si s[i] == '\0' → devolver NULL
    i = i + 1
```

El orden de las dos comprobaciones hace que buscar `'\0'` funcione solo.

## Puntos clave y casos límite

- Convierte `c` a `char` antes de comparar: `ft_strchr(s, 't' + 256)` debe encontrar `'t'`.
- `ft_strchr(s, '\0')` devuelve `s + ft_strlen(s)`, no NULL.
- Devuelve `char *` a partir de un `const char *`: hace falta un cast.

### Errores típicos

- **Devolver `NULL` al buscar `'\0'`**: si compruebas el fin de cadena antes que la coincidencia, nunca encuentras el terminador.
- **No convertir `c` a `char`**: `ft_strchr(s, 't' + 256)` debe encontrar `'t'`, igual que la original.
- **Imprimir el resultado con `printf("%s")` sin comprobar `NULL`**: es comportamiento indefinido.
- **Olvidar el cast** de `const char *` a `char *` en el `return`: sin él, `-Werror` lo rechaza.

## Relacionadas

[[ft_strrchr]] · [[ft_memchr]] · [[Punteros en C]] · [[Carácter nulo y puntero NULL]]

## Referencias

- `man 3 strchr` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [strchr(3) — man7.org](https://man7.org/linux/man-pages/man3/strchr.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
