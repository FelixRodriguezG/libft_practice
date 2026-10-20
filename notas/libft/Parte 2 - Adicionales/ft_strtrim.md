---
tags: [libft, libft/parte2]
funcion: ft_strtrim
original: ninguna
externas: "malloc"
estado: hecho
---
# ft_strtrim

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Devuelve una copia nueva de `s1` sin los caracteres de `set` que haya **al principio y al final**. Lo de en medio se queda igual. Sirve, por ejemplo, para quitar espacios sobrantes.

## Explicación sencilla

`set` no es una palabra: es una **lista de caracteres** sueltos que se pueden quitar, en cualquier orden.

| Llamada | Resultado |
|---|---|
| `ft_strtrim("   hola  ", " ")` | `"hola"` |
| `ft_strtrim("xyxhola mundoyx", "xy")` | `"hola mundo"` |
| `ft_strtrim("xxhoxlaxx", "x")` | `"hoxla"` (la `x` de en medio se queda) |
| `ft_strtrim("xxxx", "x")` | `""` |
| `ft_strtrim("hola", "")` | `"hola"` |

```text
 s1:    x   y   x   h   o   l   a   y   x  \0
        0   1   2   3   4   5   6   7   8
                    ▲           ▲
                  inicio       fin
        avanza mientras        retrocede mientras
        s1[i] está en set      s1[j] está en set

 resultado = ft_substr(s1, inicio, fin - inicio + 1) = "hola"
```

## Prototipo

```c
char *ft_strtrim(char const *s1, char const *set);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Reserva memoria (con malloc(3)) y devuelve una copia de ‘s1’ con los caracteres de ‘set’ eliminados al principio y al final.

| | |
|---|---|
| **Parámetros** | `s1`: La cadena de caracteres que debe ser recortada.<br>`set`: Los caracteres a eliminar de la cadena en cuestión. |
| **Valor devuelto** | La cadena recortada resultante.<br>NULL si falla la reserva de memoria. |
| **Funciones autorizadas** | malloc |

## Funciones externas (man)

> [!quote] man 3 malloc — RETURN VALUE
> The malloc() and calloc() functions return a pointer to the allocated memory, which is suitably aligned for any built-in type.  On error, these functions return NULL.

> [!note] Traducción
> malloc() y calloc() devuelven un puntero a la memoria reservada, alineada adecuadamente para cualquier tipo predefinido. En caso de error, devuelven NULL.

## Cómo implementarla

```text
1. Si s1 o set son NULL → devuelve NULL.
2. inicio = 0
   mientras s1[inicio] != '\0' y s1[inicio] está en set: inicio + 1
3. fin = ft_strlen(s1)            (una posición después del último carácter)
   mientras fin > inicio y s1[fin - 1] está en set: fin - 1
4. Devuelve ft_substr(s1, inicio, fin - inicio)
   (ft_substr ya reserva, copia y pone el '\0'; si malloc falla, devuelve NULL)
```

«Está en set» = `ft_strchr(set, caracter) != NULL`, pero cuidado con el `'\0'` (ver abajo).

## Puntos clave y casos límite

- Los caracteres del medio **no** se tocan: `ft_strtrim("xxhoxlaxx", "x")` → `"hoxla"`.
- Si todo son caracteres de `set`, devuelve una cadena vacía reservada.
- `ft_strchr(set, c)` sirve para saber si `c` está en `set`.

> [!warning] Errores típicos
> - **`ft_strchr(set, '\0')` no devuelve NULL**: devuelve un puntero al `'\0'` de `set`, porque el terminador cuenta como parte de la cadena. Si tu bucle no para antes en el `'\0'` de `s1`, se sale de la cadena. Comprueba siempre `s1[i] != '\0'` primero.
> - **Índice `fin` que baja de 0**: con `size_t`, `0 - 1` no da -1 sino un número enorme ([[Tipos enteros y conversiones]]). Por eso el pseudocódigo usa `fin > inicio` y mira `s1[fin - 1]`.
> - **Devolver NULL** cuando todo se recorta: lo correcto es `""` reservada; NULL significa «falló `malloc`».
> - **Devolver `s1` tal cual** si no hay nada que recortar: el subject pide una copia nueva; quien llama hará `free` y liberaría memoria que no es suya.

## Relacionadas

[[ft_strchr]] · [[ft_substr]] · [[ft_strlen]] · [[Control de errores en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 malloc` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [malloc(3) en man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html).
