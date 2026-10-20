---
tags: [libft, libft/parte2]
funcion: ft_strjoin
original: ninguna
externas: "malloc"
estado: hecho
---
# ft_strjoin

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Une dos cadenas en una **nueva**, reservada con `malloc`: primero `s1` y a continuación `s2`. Ninguna de las dos originales cambia.

## Explicación sencilla

```c
char	*r = ft_strjoin("Hola, ", "42");
/* r = "Hola, 42"  — 8 caracteres + '\0' = 9 bytes */
free(r);
```

```text
 s1 ─► "Hola, \0"   (6 + 1)        s2 ─► "42\0"   (2 + 1)
        │                                  │
        └──────────── copia ───────┐ ┌─────┘
                                   ▼ ▼
 r  ─► ┌─┬─┬─┬─┬─┬─┬─┬─┬──┐
       │H│o│l│a│,│ │4│2│\0│   malloc(6 + 2 + 1)
       └─┴─┴─┴─┴─┴─┴─┴─┴──┘
```

Solo hay **un** `'\0'` en el resultado: el de `s1` se sobrescribe con el primer carácter de `s2`.

## Prototipo

```c
char *ft_strjoin(char const *s1, char const *s2);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Reserva memoria (con malloc(3)) y devuelve una nueva cadena de caracteres, formada por la concatenación de ‘s1’ y ‘s2’.

| | |
|---|---|
| **Parámetros** | `s1`: La primera cadena.<br>`s2`: La cadena a añadir a ‘s1’. |
| **Valor devuelto** | La nueva cadena de caracteres.<br>NULL si falla la reserva de memoria. |
| **Funciones autorizadas** | malloc |

## Funciones externas (man)

> [!quote] man 3 malloc — RETURN VALUE
> The malloc() and calloc() functions return a pointer to the allocated memory, which is suitably aligned for any built-in type.  On error, these functions return NULL.

> [!note] Traducción
> malloc() y calloc() devuelven un puntero a la memoria reservada, alineada adecuadamente para cualquier tipo predefinido. En caso de error, devuelven NULL.

## Cómo implementarla

```text
1. Si s1 o s2 son NULL → devuelve NULL (protección habitual).
2. len1 = ft_strlen(s1); len2 = ft_strlen(s2)
3. r = malloc(len1 + len2 + 1). Si falla → devuelve NULL.
4. Copia s1 al principio de r (ft_strlcpy con tamaño len1 + 1 lo deja terminado en '\0').
5. Añade s2 detrás (ft_strlcat con tamaño len1 + len2 + 1).
6. Devuelve r.
```

## Puntos clave y casos límite

- Reserva `ft_strlen(s1) + ft_strlen(s2) + 1`.
- Útil combinar `ft_strlcpy` + `ft_strlcat`.

> [!warning] Errores típicos
> - **Olvidar el `+ 1`** del `'\0'`: escribes un byte fuera del bloque (Valgrind: *Invalid write of size 1*).
> - **Usar `ft_strlcat` sobre memoria sin inicializar**: `strlcat` busca primero el `'\0'` del destino; si `malloc` te dio basura, no lo encontrará donde esperas. Por eso se copia `s1` antes con `ft_strlcpy`.
> - **Leak en bucles**: `s = ft_strjoin(s, otra);` pierde la cadena antigua si `s` venía de `malloc`. Guarda la vieja en una variable temporal y libérala después. Lo verás en get_next_line.
> - **Cadenas vacías**: `ft_strjoin("", "")` debe devolver `""` reservada (1 byte), no NULL.
> - **`s1`/`s2` NULL**: el subject no dice nada; devolver NULL evita el *segfault* de `ft_strlen(NULL)` ([[Carácter nulo y puntero NULL]]).

## Relacionadas

[[ft_strlcat]] · [[ft_strlcpy]] · [[ft_strdup]] · [[ft_substr]] · [[Control de errores en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 malloc` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [malloc(3) en man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html).
