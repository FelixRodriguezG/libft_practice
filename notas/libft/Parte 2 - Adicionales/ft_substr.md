---
tags:
  - libft
  - libft/parte2
funcion: ft_substr
original: ninguna
externas: malloc
estado: hecho
---
# ft_substr

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Copia un trozo de una cadena en memoria nueva: empieza en el índice `start` y coge como mucho `len` caracteres. Es la herramienta que usan por dentro [[ft_strtrim]] y [[ft_split]].

## Explicación sencilla

| Llamada | Resultado | Por qué |
|---|---|---|
| `ft_substr("Barcelona", 3, 4)` | `"celo"` | índices 3, 4, 5, 6 |
| `ft_substr("Barcelona", 6, 100)` | `"ona"` | `len` es un **máximo**: solo quedan 3 |
| `ft_substr("Barcelona", 0, 0)` | `""` | longitud 0 |
| `ft_substr("Barcelona", 20, 5)` | `""` | `start` está fuera de la cadena |

```text
 índice:  0   1   2   3   4   5   6   7   8   9
 s:     │ B │ a │ r │ c │ e │ l │ o │ n │ a │\0 │
                    └──── len = 4 ────┘
                    ▲
                  start = 3

 nuevo (malloc de 4 + 1):  │ c │ e │ l │ o │\0 │
```

## Prototipo

```c
char *ft_substr(char const *s, unsigned int start, size_t len);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Reserva memoria (con malloc(3)) y devuelve una subcadena de caracteres de la cadena ‘s’.
> La subcadena comienza en el índice ‘start’ y tiene una longitud máxima ‘len’.

|                           |                                                                                                                                                                                       |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Parámetros**            | `s`: La cadena original desde la que se crea la subcadena.<br>`start`: El índice del carácter en ‘s’ desde el que empieza la subcadena.<br>`len`: La longitud máxima de la subcadena. |
| **Valor devuelto**        | La subcadena de caracteres resultante.<br>NULL si falla la reserva de memoria.                                                                                                        |
| **Funciones autorizadas** | malloc                                                                                                                                                                                |

## Funciones externas (man)

> [!quote] man 3 malloc — RETURN VALUE
> The malloc() and calloc() functions return a pointer to the allocated memory, which is suitably aligned for any built-in type.  On error, these functions return NULL.

> [!note] Traducción
> malloc() y calloc() devuelven un puntero a la memoria reservada, alineada adecuadamente para cualquier tipo predefinido. En caso de error, devuelven NULL.

## Cómo implementarla

```text
1. Si s es NULL → devuelve NULL.
2. slen = ft_strlen(s)
3. Si start >= slen → devuelve ft_strdup("")      (cadena vacía, pero reservada)
4. Si len > slen - start → len = slen - start      (recorta al trozo que existe)
5. r = malloc(len + 1). Si falla → devuelve NULL.
6. Copia len caracteres desde s + start y pon '\0' al final
   (ft_strlcpy(r, s + start, len + 1) hace las dos cosas).
7. Devuelve r.
```

## Puntos clave y casos límite

- Si `start >= ft_strlen(s)`: devuelve una cadena vacía reservada (`ft_strdup("")`), no NULL.
- Reserva solo lo necesario: `min(len, ft_strlen(s) - start) + 1`.

> [!note] Lo que dice y lo que no dice el subject
> El subject solo define el NULL para fallo de `malloc`. Devolver `""` cuando `start` está fuera de la cadena es la convención que comprueban los testers habituales: así quien llama siempre puede hacer `free` del resultado.

> [!warning] Errores típicos
> - **Reservar `len + 1` sin recortar**: `ft_substr("hola", 0, SIZE_MAX)` → `len + 1` desborda a 0, `malloc(0)` puede devolver un bloque de 0 bytes y, si copias `len` caracteres, escribes fuera de él. Recorta `len` antes de reservar.
> - **Leer fuera de `s` cuando `start` es grande**: `s + start` apunta más allá del `'\0'`; comprueba `start >= slen` **antes** de tocar nada.
> - **Restar con `size_t`** al revés: `slen - start` con `start > slen` no da negativo sino un número enorme ([[Tipos enteros y conversiones]]). Por eso el orden de los pasos 3 y 4 importa.
> - **Olvidar el `'\0'`**: la copia «se ve bien» en `printf` hasta que la memoria siguiente no es cero.

## Relacionadas

[[ft_strdup]] · [[ft_strlcpy]] · [[ft_strtrim]] · [[ft_split]] · [[Control de errores en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 malloc` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [malloc(3) en man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html).
