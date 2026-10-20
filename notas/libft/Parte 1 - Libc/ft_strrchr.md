---
tags: [libft, libft/parte1, libft/cadenas]
funcion: ft_strrchr
original: "strrchr(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_strrchr

[[libft - Índice|← Índice]] · Parte 1 · Cadenas

> Última aparición de un carácter: devuelve un puntero al último `c` que haya en `s`, o `NULL` si no está.

## Explicación sencilla

Igual que [[ft_strchr]], pero se queda con la **última** coincidencia.

```text
 índice:  0   1   2   3   4   5   6
 s ──►  │ b │ a │ n │ a │ n │ a │ \0 │
              ▲                   ▲
  ft_strchr(s,'a')     ft_strrchr(s,'a')
   → "anana"            → "a"
```

| Llamada | Retorno |
|---|---|
| `ft_strrchr("banana", 'a')` | puntero a `s + 5` (`"a"`) |
| `ft_strrchr("banana", 'x')` | `NULL` |
| `ft_strrchr("banana", '\0')` | puntero al `'\0'` (`s + 6`) |

Devuelve una dirección dentro de `s` (ver [[Punteros en C]]).

## Prototipo

```c
// Original — strrchr(3)
#include <string.h>
char *strrchr(const char *s, int c);

// libft
char *ft_strrchr(const char *s, int c);
```

Consultar: `man 3 strrchr`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 strrchr — DESCRIPTION
> The strrchr() function returns a pointer to the last occurrence of the character c in the string s.

> [!note] Traducción
> La función strrchr() devuelve un puntero a la última aparición del carácter c en la cadena s.

> [!quote] man 3 strrchr — DESCRIPTION
> Here "character" means "byte"; these functions do not work with wide or multibyte characters.

> [!note] Traducción
> Aquí "carácter" significa "byte"; estas funciones no funcionan con caracteres anchos ni multibyte.

> [!quote] man 3 strrchr — RETURN VALUE
> The strchr() and strrchr() functions return a pointer to the matched character or NULL if the character is not found.  The terminating null byte is considered part of the string, so that if c is specified as '\0', these functions return a pointer to the terminator.

> [!note] Traducción
> strchr() y strrchr() devuelven un puntero al carácter encontrado, o NULL si no se encuentra. El byte nulo final se considera parte de la cadena, así que si c es '\0', estas funciones devuelven un puntero al terminador.

## Cómo implementarla

Opción A, recorriendo hacia delante:
```text
ch = c convertido a char
ultima = NULL
para cada posición i de s, incluido el '\0' final:
    si s[i] == ch → ultima = dirección de s[i]
devolver ultima
```
Opción B, desde el final:
```text
i = longitud de s                  (posición del '\0')
repetir:
    si s[i] == ch → devolver la dirección de s[i]
    si i == 0     → devolver NULL
    i = i - 1
```

## Puntos clave y casos límite

- Igual que `ft_strchr` pero se queda con la **última** coincidencia (o busca desde el final).
- `ft_strrchr(s, '\0')` devuelve el puntero al terminador.

### Errores típicos

- **`while (i >= 0)` con `size_t i`** en la opción B: nunca es falso y acabas leyendo fuera. Comprueba `i == 0` antes de decrementar. Ver [[Tipos enteros y conversiones]].
- **Saltarse la posición 0**: `ft_strrchr("abc", 'a')` debe devolver `s`.
- **No comparar el `'\0'`**: buscar `'\0'` debe devolver el terminador, no `NULL`.
- **No convertir `c` a `char`** (mismo test `'a' + 256` que en `ft_strchr`).

## Relacionadas

[[ft_strchr]] · [[Punteros en C]]

## Referencias

- `man 3 strrchr` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [strrchr(3) — man7.org](https://man7.org/linux/man-pages/man3/strrchr.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
