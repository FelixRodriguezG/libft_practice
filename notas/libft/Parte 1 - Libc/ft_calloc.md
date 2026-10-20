---
tags: [libft, libft/parte1, libft/memoria-dinamica]
funcion: ft_calloc
original: "calloc(3)"
cabecera: "<stdlib.h>"
estado: hecho
---
# ft_calloc

[[libft - Índice|← Índice]] · Parte 1 · Memoria dinámica

> Reserva memoria inicializada a cero: pide al sistema espacio para `nmemb` elementos de `size` bytes y lo devuelve con todos los bytes a 0.

## Explicación sencilla

Es `malloc` + `bzero` con una comprobación extra. La memoria sale del **heap** (montículo) y sigue existiendo hasta que llames a `free` (ver [[Segmentos de memoria en C]]).

```c
int	*arr;

arr = ft_calloc(4, sizeof(int));      /* 4 * 4 = 16 bytes */
```

```text
 stack                     heap
 arr ─────────────────►  │ 0 │ 0 │ 0 │ 0 │     16 bytes a 0
                           int int int int
```

| Llamada | Resultado |
|---|---|
| `ft_calloc(4, sizeof(int))` | 16 bytes a cero |
| `ft_calloc(0, 0)` | puntero único que se puede liberar (lo exige el subject) |
| `ft_calloc(SIZE_MAX, 2)` | `NULL` (la multiplicación desborda) |

## Prototipo

```c
// Original — calloc(3)
#include <stdlib.h>
void *calloc(size_t nmemb, size_t size);

// libft
void *ft_calloc(size_t nmemb, size_t size);
```

Consultar: `man 3 calloc`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Para implementar estas otras dos funciones, tendrás que utilizar malloc():
> 
> Dependiendo de tu sistema operativo actual, el comportamiento de la función calloc puede diferir de lo descrito en su página del manual. Debes seguir la siguiente regla: Si nmemb o size es 0, entonces calloc() debe devolver un puntero único que pueda pasarse con éxito a free().

## Comportamiento según el manual

> [!quote] man 3 calloc — DESCRIPTION
> The calloc() function allocates memory for an array of nmemb elements of size bytes each and returns a pointer to the allocated memory.  The memory is set to zero.  If nmemb or size is 0, then calloc() returns either NULL, or a unique pointer value that can later be successfully passed to free().  If the multiplication of nmemb and size would result in integer overflow, then calloc() returns an error.

> [!note] Traducción
> La función calloc() reserva memoria para un array de nmemb elementos de size bytes cada uno y devuelve un puntero a la memoria reservada. La memoria se pone a cero. Si nmemb o size es 0, calloc() devuelve NULL o un puntero único que más tarde se puede pasar a free() sin problemas. Si la multiplicación de nmemb por size produjera un desbordamiento de enteros, calloc() devuelve un error.

> [!quote] man 3 calloc — RETURN VALUE
> The malloc() and calloc() functions return a pointer to the allocated memory, which is suitably aligned for any built-in type.  On error, these functions return NULL.

> [!note] Traducción
> malloc() y calloc() devuelven un puntero a la memoria reservada, alineada adecuadamente para cualquier tipo predefinido. En caso de error, devuelven NULL.

> [!quote] man 3 calloc — ERRORS
> ENOMEM Out of memory.

> [!note] Traducción
> ENOMEM Sin memoria.

## Cómo implementarla

```text
si size != 0 y nmemb > SIZE_MAX / size:
    devolver NULL                   (nmemb * size no cabe en size_t)
total = nmemb * size
p = malloc(total)
si p == NULL:
    devolver NULL
poner a 0 los total bytes de p     (ft_bzero)
devolver p
```

`SIZE_MAX` está en `<stdint.h>`. Con `nmemb` o `size` a 0, `total` vale 0: en glibc `malloc(0)` ya devuelve un puntero único y liberable; si no quieres depender del sistema, reserva 1 byte en ese caso.

## Puntos clave y casos límite

- Comprueba el desbordamiento antes de multiplicar: `if (size && nmemb > SIZE_MAX / size) return (NULL);`.
- Implementación típica: `malloc(nmemb * size)` + `ft_bzero`.
- Con `nmemb` o `size` a 0, **el subject exige** devolver un puntero único liberable con `free()` (no NULL).

### Errores típicos

- **No comprobar el desbordamiento**: `nmemb * size` en `size_t` «da la vuelta» y reservas mucho menos de lo pedido; luego escribes fuera del bloque. Ver [[Tipos enteros y conversiones]].
- **No comprobar si `malloc` devolvió `NULL`** antes de llamar a `ft_bzero`: segfault. Ver [[Control de errores en C]].
- **Devolver `NULL` cuando `nmemb` o `size` es 0**: el subject exige un puntero único liberable.
- **Olvidar poner a cero**: entonces es solo `malloc`. Valgrind lo detecta como «uninitialised value» al usarla. Ver [[Valgrind y sanitizers]].

## Relacionadas

[[ft_bzero]] · [[ft_strdup]] · [[Segmentos de memoria en C]] · [[Control de errores en C]]

## Referencias

- `man 3 calloc` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [calloc(3) — man7.org](https://man7.org/linux/man-pages/man3/calloc.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- [malloc(3) — man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html) — `malloc`, `free` y el comportamiento con tamaño 0.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
