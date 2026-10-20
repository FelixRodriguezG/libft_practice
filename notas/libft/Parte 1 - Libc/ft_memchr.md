---
tags: [libft, libft/parte1, libft/memoria]
funcion: ft_memchr
original: "memchr(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_memchr

[[libft - Índice|← Índice]] · Parte 1 · Memoria

> Busca un byte en n bytes de memoria: devuelve un puntero al primer byte igual a `c` dentro de los `n` primeros, o `NULL`.

## Explicación sencilla

Es la versión «de memoria» de [[ft_strchr]]: no sabe qué es una cadena, así que **no se para en `'\0'`**; recorre exactamente `n` bytes.

```c
char	data[5] = {'a', 'b', '\0', 'c', 'd'};
```

```text
 índice:  0   1    2    3   4
 data:  │ a │ b │ \0 │ c │ d │
                      ▲
   ft_memchr(data, 'c', 5) → &data[3]
   ft_strchr(data, 'c')    → NULL   (se para en el '\0')
   ft_memchr(data, 'c', 3) → NULL   (solo mira 3 bytes)
```

Ver [[Punteros en C]].

## Prototipo

```c
// Original — memchr(3)
#include <string.h>
void *memchr(const void *s, int c, size_t n);

// libft
void *ft_memchr(const void *s, int c, size_t n);
```

Consultar: `man 3 memchr`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 memchr — DESCRIPTION
> The memchr() function scans the initial n bytes of the memory area pointed to by s for the first instance of c.  Both c and the bytes of the memory area pointed to by s are interpreted as unsigned char.

> [!note] Traducción
> La función memchr() examina los n primeros bytes de la zona de memoria apuntada por s buscando la primera aparición de c. Tanto c como los bytes de la zona apuntada por s se interpretan como unsigned char.

> [!quote] man 3 memchr — RETURN VALUE
> The memchr() and memrchr() functions return a pointer to the matching byte or NULL if the character does not occur in the given memory area.

> [!note] Traducción
> memchr() y memrchr() devuelven un puntero al byte coincidente, o NULL si el carácter no aparece en la zona de memoria indicada.

## Cómo implementarla

```text
p  = s visto como puntero a const unsigned char
ch = c convertido a unsigned char
para i desde 0 hasta n - 1:
    si p[i] == ch → devolver la dirección de p[i]
devolver NULL
```

## Puntos clave y casos límite

- A diferencia de `strchr`, **no** se detiene en `'\0'`: recorre exactamente `n` bytes.
- Compara usando `unsigned char` tanto para `c` como para los bytes.

### Errores típicos

- **Parar en `'\0'`**: es justo lo que la diferencia de `strchr`.
- **Comparar un `char` con el `int` sin convertir**: `(char)200` vale −56 en Linux y nunca será igual a 200. Convierte ambos a `unsigned char`. Ver [[Tipos enteros y conversiones]].
- **Leer más allá de `n`** (por ejemplo, condición `i <= n`).
- **Olvidar el cast** a `void *` al devolver un puntero que venía de `const void *`.

## Relacionadas

[[ft_strchr]] · [[ft_memcmp]] · [[Punteros en C]] · [[Tipos enteros y conversiones]]

## Referencias

- `man 3 memchr` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [memchr(3) — man7.org](https://man7.org/linux/man-pages/man3/memchr.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
