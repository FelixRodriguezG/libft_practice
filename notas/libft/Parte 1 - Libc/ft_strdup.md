---
tags: [libft, libft/parte1, libft/memoria-dinamica]
funcion: ft_strdup
original: "strdup(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_strdup

[[libft - Índice|← Índice]] · Parte 1 · Memoria dinámica

> Duplica una cadena en memoria nueva: reserva con `malloc` el espacio justo, copia `s` dentro y devuelve la copia.

## Explicación sencilla

La copia vive en el **heap** (ver [[Segmentos de memoria en C]]): puedes modificarla y sigue existiendo al salir de la función, pero quien la recibe tiene que liberarla con `free`.

```c
char	*copia;

copia = ft_strdup("hola");
copia[0] = 'H';                  /* ✅ la copia sí se puede modificar */
free(copia);
```

```text
 datos (solo lectura)          heap (malloc de 5 bytes)
 "hola" │ h │ o │ l │ a │ \0 │   │ H │ o │ l │ a │ \0 │ ◄── copia
                                  strlen("hola") + 1 = 5
```

| Entrada | Bytes reservados | Retorno |
|---|---|---|
| `"hola"` | 5 | nueva cadena `"hola"` |
| `""` | 1 | nueva cadena vacía (solo `'\0'`) |
| sin memoria | — | `NULL` |

## Prototipo

```c
// Original — strdup(3)
#include <string.h>
char *strdup(const char *s);

// libft
char *ft_strdup(const char *s);
```

Consultar: `man 3 strdup`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Para implementar estas otras dos funciones, tendrás que utilizar malloc():

## Comportamiento según el manual

> [!quote] man 3 strdup — DESCRIPTION
> The strdup() function returns a pointer to a new string which is a duplicate of the string s.  Memory for the new string is obtained with malloc(3), and can be freed with free(3).

> [!note] Traducción
> La función strdup() devuelve un puntero a una cadena nueva que es un duplicado de la cadena s. La memoria de la cadena nueva se obtiene con malloc(3) y puede liberarse con free(3).

> [!quote] man 3 strdup — RETURN VALUE
> On success, the strdup() function returns a pointer to the duplicated string.  It returns NULL if insufficient memory was available, with errno set to indicate the cause of the error.

> [!note] Traducción
> Si tiene éxito, strdup() devuelve un puntero a la cadena duplicada. Devuelve NULL si no había memoria suficiente, y pone en errno la causa del error.

> [!quote] man 3 strdup — ERRORS
> ENOMEM Insufficient memory available to allocate duplicate string.

> [!note] Traducción
> ENOMEM No hay memoria suficiente para reservar la cadena duplicada.

## Cómo implementarla

```text
len = ft_strlen(s)
copia = malloc(len + 1)
si copia == NULL:
    devolver NULL
copiar los len caracteres de s y el '\0' a copia   (ft_memcpy o ft_strlcpy)
devolver copia
```

## Puntos clave y casos límite

- Reserva `ft_strlen(s) + 1` bytes (el `+ 1` es para el `'\0'`).
- Comprueba siempre el retorno de `malloc`.

### Errores típicos

- **Olvidar el `+ 1`** del `'\0'`: escribes un byte fuera del bloque. Valgrind lo marca como «Invalid write of size 1». Ver [[Valgrind y sanitizers]].
- **Usar `sizeof(s)`** en lugar de `ft_strlen(s)`: `s` es un puntero, así que `sizeof(s)` vale 8 en 64 bits, sea cual sea la cadena.
- **Devolver `s`** en vez de una copia: no es un duplicado y el `free` posterior rompe el programa.
- **No comprobar `NULL` tras `malloc`**. Ver [[Control de errores en C]].
- **No liberar la copia** en tus tests: fuga de memoria (*leak*).

## Relacionadas

[[ft_strlen]] · [[ft_calloc]] · [[ft_substr]] · [[Segmentos de memoria en C]] · [[Control de errores en C]]

## Referencias

- `man 3 strdup` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [strdup(3) — man7.org](https://man7.org/linux/man-pages/man3/strdup.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
