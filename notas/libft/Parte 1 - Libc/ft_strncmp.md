---
tags: [libft, libft/parte1, libft/cadenas]
funcion: ft_strncmp
original: "strncmp(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_strncmp

[[libft - Índice|← Índice]] · Parte 1 · Cadenas

> Compara hasta n caracteres: devuelve 0 si los `n` primeros caracteres de `s1` y `s2` son iguales, y un número negativo o positivo según cuál sea «menor».

## Explicación sencilla

Compara carácter a carácter y se para en la **primera diferencia**, en el `'\0'` o al llegar a `n`. El resultado es la resta de los dos caracteres distintos (como `unsigned char`).

```text
 s1:  │ h │ o │ l │ a │ \0 │
 s2:  │ h │ o │ L │ a │ \0 │
        =   =   ≠
                └─ 'l' (108) - 'L' (76) = 32  → positivo: s1 > s2
```

| Llamada | Resultado |
|---|---|
| `ft_strncmp("abc", "abd", 2)` | 0 (solo mira `"ab"`) |
| `ft_strncmp("abc", "abd", 3)` | negativo (`'c'` − `'d'`) |
| `ft_strncmp("hola", "hoLa", 5)` | positivo (32 en glibc) |
| `ft_strncmp("a", "b", 0)` | 0 |

La comparación con `unsigned char` importa para los bytes ≥ 128 (ver [[Tipos enteros y conversiones]]).

## Prototipo

```c
// Original — strncmp(3)
#include <string.h>
int strncmp(const char *s1, const char *s2, size_t n);

// libft
int ft_strncmp(const char *s1, const char *s2, size_t n);
```

Consultar: `man 3 strncmp`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 strncmp — DESCRIPTION
> The strcmp() function compares the two strings s1 and s2.  The locale is not taken into account (for a locale-aware comparison, see strcoll(3)).  The comparison is done using unsigned characters.

> [!note] Traducción
> La función strcmp() compara las dos cadenas s1 y s2. No se tiene en cuenta el locale (para una comparación que lo tenga en cuenta, ver strcoll(3)). La comparación se hace con caracteres sin signo.

> [!quote] man 3 strncmp — DESCRIPTION
> The strncmp() function is similar, except it compares only the first (at most) n bytes of s1 and s2.

> [!note] Traducción
> La función strncmp() es similar, salvo que compara solo los primeros n bytes (como máximo) de s1 y s2.

> [!quote] man 3 strncmp — RETURN VALUE
> The strcmp() and strncmp() functions return an integer less than, equal to, or greater than zero if s1 (or the first n bytes thereof) is found, respectively, to be less than, to match, or be greater than s2.

> [!note] Traducción
> strcmp() y strncmp() devuelven un entero menor, igual o mayor que cero si s1 (o sus primeros n bytes) es, respectivamente, menor, igual o mayor que s2.

## Cómo implementarla

```text
i = 0
mientras i < n:
    a = s1[i] como unsigned char
    b = s2[i] como unsigned char
    si a != b  → devolver a - b
    si a == 0  → devolver 0         (las dos cadenas acaban aquí)
    i = i + 1
devolver 0
```

## Puntos clave y casos límite

- Se detiene en el primer byte distinto, en `'\0'` o al llegar a `n`.
- Compara como `unsigned char`: `ft_strncmp("\200", "\0", 1)` debe ser **positivo**.
- Con `n == 0` devuelve 0.

### Errores típicos

- **Comparar como `char`**: en Linux `char` tiene signo, así que `'\200'` vale −128 y `ft_strncmp("\200", "\0", 1)` saldría negativo. Debe ser positivo.
- **Seguir después del `'\0'`**: lees memoria fuera de la cadena más corta.
- **Leer `s1[0]` con `n == 0`**: no se debe tocar la memoria; devuelve 0 directamente.
- **Exigir en los tests el valor exacto**: el man solo garantiza el signo. Compara signos.

## Relacionadas

[[ft_memcmp]] · [[ft_strnstr]] · [[Tipos enteros y conversiones]]

## Referencias

- `man 3 strncmp` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [strncmp(3) — man7.org](https://man7.org/linux/man-pages/man3/strncmp.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
