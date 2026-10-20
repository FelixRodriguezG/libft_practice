---
tags: [libft, libft/parte1, libft/memoria]
funcion: ft_memcmp
original: "memcmp(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_memcmp

[[libft - Índice|← Índice]] · Parte 1 · Memoria

> Compara n bytes de memoria: devuelve 0 si los `n` primeros bytes de `s1` y `s2` son iguales, y un número negativo o positivo según el primer byte distinto.

## Explicación sencilla

Como [[ft_strncmp]], pero sin tratar el `'\0'` como final: compara **todos** los `n` bytes.

```text
 s1:  │ a │ b │ \0 │ c │
 s2:  │ a │ b │ \0 │ d │
        =   =    =   ≠
                     └─ 'c' - 'd' = -1  → negativo
```

| Llamada | Resultado |
|---|---|
| `ft_memcmp("ab\0c", "ab\0d", 4)` | negativo |
| `ft_strncmp("ab\0c", "ab\0d", 4)` | 0 (se para en el `'\0'`) |
| `ft_memcmp("\200", "\0", 1)` | positivo (128 − 0) |
| `ft_memcmp(a, b, 0)` | 0 |

Sirve para comparar cualquier cosa: structs, arrays de `int`… (ver [[Punteros en C]]).

## Prototipo

```c
// Original — memcmp(3)
#include <string.h>
int memcmp(const void *s1, const void *s2, size_t n);

// libft
int ft_memcmp(const void *s1, const void *s2, size_t n);
```

Consultar: `man 3 memcmp`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 memcmp — DESCRIPTION
> The memcmp() function compares the first n bytes (each interpreted as unsigned char) of the memory areas s1 and s2.

> [!note] Traducción
> La función memcmp() compara los primeros n bytes (cada uno interpretado como unsigned char) de las zonas de memoria s1 y s2.

> [!quote] man 3 memcmp — RETURN VALUE
> The memcmp() function returns an integer less than, equal to, or greater than zero if the first n bytes of s1 is found, respectively, to be less than, to match, or be greater than the first n bytes of s2.
>
> For a nonzero return value, the sign is determined by the sign of the difference between the first pair of bytes (interpreted as unsigned char) that differ in s1 and s2.
>
> If n is zero, the return value is zero.

> [!note] Traducción
> La función memcmp() devuelve un entero menor, igual o mayor que cero si los primeros n bytes de s1 son, respectivamente, menores, iguales o mayores que los primeros n bytes de s2.
>
> Si el valor devuelto no es cero, su signo lo determina el signo de la diferencia entre el primer par de bytes (interpretados como unsigned char) que difieren en s1 y s2.
>
> Si n es cero, el valor devuelto es cero.

## Cómo implementarla

```text
p1 = s1 como puntero a const unsigned char
p2 = s2 como puntero a const unsigned char
para i desde 0 hasta n - 1:
    si p1[i] != p2[i] → devolver p1[i] - p2[i]
devolver 0
```

## Puntos clave y casos límite

- No se detiene en `'\0'`.
- Devuelve `(unsigned char)a - (unsigned char)b` del primer byte distinto.
- El man solo garantiza el **signo**, no el valor exacto: en los tests compara signos.

### Errores típicos

- **Comparar como `char` con signo**: `"\200"` frente a `"\0"` daría negativo. Ver [[Tipos enteros y conversiones]].
- **Parar en `'\0'`**: eso es `strncmp`.
- **Acceder a memoria con `n == 0`**: hay que devolver 0 sin leer.

## Relacionadas

[[ft_strncmp]] · [[ft_memchr]] · [[Tipos enteros y conversiones]]

## Referencias

- `man 3 memcmp` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [memcmp(3) — man7.org](https://man7.org/linux/man-pages/man3/memcmp.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
