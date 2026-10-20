---
tags: [libft, libft/parte2]
funcion: ft_strmapi
original: ninguna
externas: "malloc"
estado: pendiente
---
# ft_strmapi

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Crea una cadena **nueva** en la que cada carácter es el resultado de `f(índice, carácter original)`. La cadena de entrada no se modifica.

## Explicación sencilla

La función `f` la escribe quien llama; tú solo la aplicas (es un **puntero a función**, ver [[Punteros en C]]).

```c
char	sumar_indice(unsigned int i, char c)
{
	return (c + i);
}

char	*r = ft_strmapi("aaaa", sumar_indice);
/* r = "abcd"  ('a'+0, 'a'+1, 'a'+2, 'a'+3) */
```

```text
 s (no cambia)                 r (memoria nueva, malloc de 5 bytes)
┌───┬───┬───┬───┬────┐        ┌───┬───┬───┬───┬────┐
│ a │ a │ a │ a │ \0 │  ──►   │ a │ b │ c │ d │ \0 │
└───┴───┴───┴───┴────┘        └───┴───┴───┴───┴────┘
  f(0,'a') f(1,'a') ...         r[i] = f(i, s[i])
```

Cómo leer el tipo del parámetro `f`: `char (*f)(unsigned int, char)` = «puntero a una función que recibe un índice y un carácter y **devuelve** un carácter».

## Prototipo

```c
char *ft_strmapi(char const *s, char (*f)(unsigned int, char));
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Aplica la función ‘f’ a cada carácter de la cadena ‘s’, pasando su índice como primer argumento y el propio carácter como segundo argumento. Se crea una nueva cadena (utilizando malloc(3)) para almacenar los resultados de las sucesivas aplicaciones de ‘f’.

| | |
|---|---|
| **Parámetros** | `s`: La cadena sobre la que iterar.<br>`f`: La función a aplicar sobre cada carácter. |
| **Valor devuelto** | La cadena creada tras el correcto uso de ‘f’ sobre cada carácter.<br>NULL si falla la reserva de memoria. |
| **Funciones autorizadas** | malloc |

## Funciones externas (man)

> [!quote] man 3 malloc — RETURN VALUE
> The malloc() and calloc() functions return a pointer to the allocated memory, which is suitably aligned for any built-in type.  On error, these functions return NULL.

> [!note] Traducción
> malloc() y calloc() devuelven un puntero a la memoria reservada, alineada adecuadamente para cualquier tipo predefinido. En caso de error, devuelven NULL.

## Cómo implementarla

```text
1. Si s o f son NULL → devuelve NULL.
2. len = ft_strlen(s)
3. r = malloc(len + 1). Si falla → devuelve NULL.
4. Para i de 0 a len - 1:  r[i] = f(i, s[i])
5. r[len] = '\0'
6. Devuelve r.
```

## Puntos clave y casos límite

- `s` no se modifica: el resultado va en memoria nueva.
- No olvides el `'\0'` final.

> [!warning] Errores típicos
> - **Confundirla con [[ft_striteri]]**: aquí `f` recibe el carácter **por valor** y lo **devuelve**; en `ft_striteri` recibe su dirección y no devuelve nada.
> - **Reservar `len` en vez de `len + 1`**: no cabe el `'\0'` y escribes un byte fuera (Valgrind: *Invalid write of size 1*).
> - **No comprobar el `malloc`**: escribir en NULL → *segfault* ([[Control de errores en C]]).
> - **Cadena vacía**: `ft_strmapi("", f)` debe devolver `""` reservada (1 byte), no NULL.
> - **Quien llama debe hacer `free`** del resultado; si no, leak.

## Relacionadas

[[ft_striteri]] · [[ft_lstmap]] · [[Punteros en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 malloc` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [malloc(3) en man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html).
