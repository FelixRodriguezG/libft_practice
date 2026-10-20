---
tags: [libft, libft/parte2]
funcion: ft_putendl_fd
original: ninguna
externas: "write"
estado: pendiente
---
# ft_putendl_fd

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Escribe una cadena y después un salto de línea (`'\n'`) en el descriptor de fichero indicado. Es [[ft_putstr_fd]] + `'\n'` («end line»).

## Explicación sencilla

```c
ft_putendl_fd("hola", 1);
ft_putendl_fd("mundo", 1);
```

```text
$ ./a.out
hola
mundo
```

Bytes que llegan a la terminal: `h o l a \n m u n d o \n`. El `'\0'` de la cadena **no** se escribe: solo marca dónde acaba ([[Carácter nulo y puntero NULL]]).

## Prototipo

```c
void ft_putendl_fd(char *s, int fd);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Envía la cadena ‘s’ al descriptor de archivo dado, seguido de un salto de línea.

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
1. Si s es NULL → no hagas nada y sal (protección opcional, ver abajo).
2. Escribe la cadena s en fd (reutiliza ft_putstr_fd).
3. Escribe el carácter '\n' en fd (reutiliza ft_putchar_fd).
```

## Puntos clave y casos límite

- `ft_putstr_fd(s, fd); ft_putchar_fd('\n', fd);`

> [!warning] Errores típicos
> - **Escribir el `'\n'` dentro de un bucle** (uno por carácter) en vez de una sola vez al final.
> - **No proteger `s == NULL`**: el subject no dice qué hacer, pero si llamas a `ft_strlen(NULL)` el programa se cae. Muchos testers comprueban que no haya *segfault*; lo habitual es no escribir nada (ni siquiera el `'\n'`). Ver [[Control de errores en C]].
> - **Reescribir el código** de [[ft_putstr_fd]] en vez de llamarla: más líneas, más sitios donde equivocarse.

## Relacionadas

[[ft_putstr_fd]] · [[ft_putchar_fd]] · [[Descriptores de fichero y read]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 2 write` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [write(2) en man7.org](https://man7.org/linux/man-pages/man2/write.2.html).
