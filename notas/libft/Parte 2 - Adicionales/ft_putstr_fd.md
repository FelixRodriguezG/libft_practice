---
tags: [libft, libft/parte2]
funcion: ft_putstr_fd
original: ninguna
externas: "write"
estado: pendiente
---
# ft_putstr_fd

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Escribe una cadena completa (sin su `'\0'`) en el descriptor de fichero indicado.

## Explicación sencilla

```c
ft_putstr_fd("Hola 42", 1);
```

```text
$ ./a.out
Hola 42$
```

(El `$` es el prompt: no se ha escrito salto de línea. Si lo quieres, usa [[ft_putendl_fd]].)

`write` recibe la dirección del primer carácter y **cuántos** bytes escribir. Ese número es justo `ft_strlen(s)`:

```text
 s ─►┌───┬───┬───┬───┬───┬───┬───┬────┐
     │ H │ o │ l │ a │   │ 4 │ 2 │ \0 │
     └───┴───┴───┴───┴───┴───┴───┴────┘
      └───────── 7 bytes ─────────┘     ← write(fd, s, 7)
```

## Prototipo

```c
void ft_putstr_fd(char *s, int fd);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Envía la cadena ‘s’ al descriptor de archivo especificado.

| | |
|---|---|
| **Parámetros** | `s`: La cadena a enviar.<br>`fd`: El descriptor de archivo sobre el que escribir. |
| **Valor devuelto** | Nada |
| **Funciones autorizadas** | write |

## Funciones externas (man)

> [!quote] man 2 write — DESCRIPTION / RETURN VALUE
> write() writes up to count bytes from the buffer starting at buf to the file referred to by the file descriptor fd.
>
> On success, the number of bytes written is returned.  On error, -1 is returned, and errno is set to indicate the cause of the error.

> [!note] Traducción
> write() escribe hasta count bytes del buffer que empieza en buf en el fichero al que hace referencia el descriptor de fichero fd.
>
> Si tiene éxito, devuelve el número de bytes escritos. En caso de error, devuelve -1 y pone en errno la causa del error.

## Cómo implementarla

```text
1. Si s es NULL → sal sin hacer nada.
2. Calcula la longitud con ft_strlen(s).
3. Una sola llamada a write: fd, s, longitud.
```

(Alternativa válida pero más lenta: recorrer la cadena y llamar a [[ft_putchar_fd]] por carácter, una llamada al sistema por byte.)

## Puntos clave y casos límite

- Una sola llamada: `write(fd, s, ft_strlen(s));`.

> [!warning] Errores típicos
> - **No proteger `s == NULL`**: `ft_strlen(NULL)` desreferencia NULL → *segfault*. El subject no lo exige, pero los testers suelen probarlo ([[Carácter nulo y puntero NULL]]).
> - **Escribir también el `'\0'`** (`ft_strlen(s) + 1`): mandas un byte nulo invisible que estropea comparaciones de salida en los testers.
> - **Usar `sizeof(s)`** en vez de `ft_strlen(s)`: `s` es un puntero, así que `sizeof` da 8 (el tamaño del puntero), no la longitud del texto. Ver [[Punteros en C]].

## Relacionadas

[[ft_putchar_fd]] · [[ft_putendl_fd]] · [[ft_strlen]] · [[Descriptores de fichero y read]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 2 write` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [write(2) en man7.org](https://man7.org/linux/man-pages/man2/write.2.html).
