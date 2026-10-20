---
tags: [libft, libft/parte1, libft/memoria]
funcion: ft_memset
original: "memset(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_memset

[[libft - Índice|← Índice]] · Parte 1 · Memoria

> Rellena n bytes con un valor: escribe el byte `c` en las `n` primeras posiciones de la memoria apuntada por `s`.

## Explicación sencilla

`void *` es un «puntero genérico»: apunta a memoria de cualquier tipo (ver [[Punteros en C]]). `memset` no sabe ni le importa qué hay ahí: trabaja **byte a byte**.

```c
char	buf[6] = "hola!";

ft_memset(buf, '-', 3);
```

```text
 antes:   │ h │ o │ l │ a │ ! │ \0 │
 después: │ - │ - │ - │ a │ ! │ \0 │
           └─ n = 3 ─┘
```

Por trabajar con bytes, con un array de `int` el resultado sorprende: `memset(arr, 1, sizeof(arr))` deja cada `int` (4 bytes) a `0x01010101` = 16843009, no a 1.

## Prototipo

```c
// Original — memset(3)
#include <string.h>
void *memset(void *s, int c, size_t n);

// libft
void *ft_memset(void *s, int c, size_t n);
```

Consultar: `man 3 memset`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 memset — DESCRIPTION
> The memset() function fills the first n bytes of the memory area pointed to by s with the constant byte c.

> [!note] Traducción
> La función memset() rellena los primeros n bytes de la zona de memoria apuntada por s con el byte constante c.

> [!quote] man 3 memset — RETURN VALUE
> The memset() function returns a pointer to the memory area s.

> [!note] Traducción
> La función memset() devuelve un puntero a la zona de memoria s.

## Cómo implementarla

```text
p = s visto como puntero a unsigned char
i = 0
mientras i < n:
    p[i] = c convertido a unsigned char
    i = i + 1
devolver s            (el puntero original, no p avanzado)
```

## Puntos clave y casos límite

- `c` se convierte a `unsigned char`: solo se usa el byte bajo (`memset(p, 256 + 'A', 3)` escribe `AAA`).
- Trabaja byte a byte: `memset(int_array, 1, ...)` **no** pone cada `int` a 1.
- Con `n == 0` no toca nada y devuelve `s`.

### Errores típicos

- **Hacer aritmética con `void *`** (`s + i`, `*s = c`): no es C estándar. `cc` en Linux lo acepta como extensión, pero `gcc -pedantic` da error y no puedes desreferenciar un `void *`. Convierte primero a `unsigned char *`.
- **Devolver el puntero avanzado**: si mueves `s` dentro del bucle, ya no apunta al inicio. Usa un índice o una copia.
- **Esperar que inicialice `int` a valores distintos de 0 o −1**: solo funciona byte a byte (ver ejemplo).

## Relacionadas

[[ft_bzero]] · [[ft_calloc]] · [[Punteros en C]]

## Referencias

- `man 3 memset` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [memset(3) — man7.org](https://man7.org/linux/man-pages/man3/memset.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
