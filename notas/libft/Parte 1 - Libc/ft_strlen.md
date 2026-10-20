---
tags: [libft, libft/parte1, libft/cadenas]
funcion: ft_strlen
original: "strlen(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_strlen

[[libft - Índice|← Índice]] · Parte 1 · Cadenas

> Longitud de una cadena: cuenta los caracteres que hay antes del `'\0'` final.

## Explicación sencilla

Una cadena en C es un array de `char` que termina en el byte nulo `'\0'` (ver [[Carácter nulo y puntero NULL]]). La función recibe un puntero al primer carácter (ver [[Punteros en C]]) y avanza hasta encontrar el `'\0'`.

```text
 s ──►┌───┬───┬───┬───┬────┐
      │ h │ o │ l │ a │ \0 │
      └───┴───┴───┴───┴────┘
 índice 0   1   2   3   4

 ft_strlen("hola") → 4      (el '\0' no se cuenta)
 ft_strlen("")     → 0      (solo hay '\0')
```

Devuelve `size_t`: un entero **sin signo** pensado para tamaños (ver [[Tipos enteros y conversiones]]).

## Prototipo

```c
// Original — strlen(3)
#include <string.h>
size_t strlen(const char *s);

// libft
size_t ft_strlen(const char *s);
```

Consultar: `man 3 strlen`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 strlen — DESCRIPTION
> The strlen() function calculates the length of the string pointed to by s, excluding the terminating null byte ('\0').

> [!note] Traducción
> La función strlen() calcula la longitud de la cadena apuntada por s, sin contar el byte nulo final ('\0').

> [!quote] man 3 strlen — RETURN VALUE
> The strlen() function returns the number of bytes in the string pointed to by s.

> [!note] Traducción
> La función strlen() devuelve el número de bytes de la cadena apuntada por s.

## Cómo implementarla

```text
i = 0
mientras s[i] no sea '\0':
    i = i + 1
devolver i
```

## Puntos clave y casos límite

- Devuelve `size_t` (sin signo), no `int`.
- `strlen(NULL)` es comportamiento indefinido (segfault).

### Errores típicos

- **Contar el `'\0'`**: devolver 5 para `"hola"`. Luego reservarías mal con `malloc(ft_strlen(s) + 1)`.
- **Usar `int` como contador**: el tipo de retorno es `size_t`; mezclar con/sin signo da avisos y errores sutiles en otras funciones.
- **Proteger `NULL` devolviendo 0**: la original no lo hace; ocultar el error hace más difícil encontrar el bug de quien la llama. Si decides hacerlo, sé coherente y sabe defenderlo en la evaluación.

## Relacionadas

[[ft_strlcpy]] · [[ft_strlcat]] · [[ft_strdup]] · [[Carácter nulo y puntero NULL]] · [[Punteros en C]]

## Referencias

- `man 3 strlen` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [strlen(3) — man7.org](https://man7.org/linux/man-pages/man3/strlen.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
