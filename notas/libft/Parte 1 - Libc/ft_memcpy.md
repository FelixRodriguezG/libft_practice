---
tags: [libft, libft/parte1, libft/memoria]
funcion: ft_memcpy
original: "memcpy(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_memcpy

[[libft - Índice|← Índice]] · Parte 1 · Memoria

> Copia n bytes (sin solapamiento): copia exactamente `n` bytes de `src` a `dest`, sin mirar qué contienen.

## Explicación sencilla

Copia **bytes**, no cadenas: no se detiene en `'\0'`. Y `n` es un número de bytes, no de elementos.

```c
int	a[3] = {1, 2, 3};
int	b[3];

ft_memcpy(b, a, sizeof(a));     /* 3 * sizeof(int) = 12 bytes */
```

```text
 src  a: │01 00 00 00│02 00 00 00│03 00 00 00│
           │  copia byte a byte (12 bytes)   │
 dest b: │01 00 00 00│02 00 00 00│03 00 00 00│
```

Las dos zonas **no deben solaparse** (compartir bytes). Si se solapan, usa [[ft_memmove]]. Ver [[Punteros en C]].

## Prototipo

```c
// Original — memcpy(3)
#include <string.h>
void *memcpy(void *dest, const void *src, size_t n);

// libft
void *ft_memcpy(void *dest, const void *src, size_t n);
```

Consultar: `man 3 memcpy`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 memcpy — DESCRIPTION
> The memcpy() function copies n bytes from memory area src to memory area dest.  The memory areas must not overlap.  Use memmove(3) if the memory areas do overlap.

> [!note] Traducción
> La función memcpy() copia n bytes de la zona de memoria src a la zona de memoria dest. Las zonas de memoria no deben solaparse. Usa memmove(3) si se solapan.

> [!quote] man 3 memcpy — RETURN VALUE
> The memcpy() function returns a pointer to dest.

> [!note] Traducción
> La función memcpy() devuelve un puntero a dest.

> [!quote] man 3 memcpy — NOTES
> (POSIX and the C standards are explicit that employing memcpy() with overlapping areas produces undefined behavior.)

> [!note] Traducción
> (POSIX y los estándares de C dicen explícitamente que usar memcpy() con zonas solapadas produce comportamiento indefinido.)

## Cómo implementarla

```text
d = dest visto como puntero a unsigned char
s = src  visto como puntero a const unsigned char
para i desde 0 hasta n - 1:
    d[i] = s[i]
devolver dest
```

## Puntos clave y casos límite

- Con `n == 0` devuelve `dest` sin acceder a memoria.
- `dest` y `src` NULL con `n > 0` es comportamiento indefinido en la original; algunos testers lo prueban, así que decide qué hace tu versión.

### Errores típicos

- **Pasar el número de elementos en vez de bytes**: `ft_memcpy(b, a, 3)` con `int` copia solo 3 bytes, no 3 enteros.
- **Parar en `'\0'`**: eso es copiar cadenas; `memcpy` copia datos binarios con ceros en medio.
- **Devolver el puntero avanzado** en lugar de `dest`.
- **Aritmética con `void *`**: convierte a `unsigned char *` (mira [[ft_memset]]).
- **Usarla con zonas solapadas**: el resultado depende del orden de copia; por eso existe `memmove`.

## Relacionadas

[[ft_memmove]] · [[ft_strlcpy]] · [[Punteros en C]]

## Referencias

- `man 3 memcpy` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [memcpy(3) — man7.org](https://man7.org/linux/man-pages/man3/memcpy.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
