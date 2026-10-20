---
tags: [libft, libft/parte2]
funcion: ft_putchar_fd
original: ninguna
externas: "write"
estado: pendiente
---
# ft_putchar_fd

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Escribe un único carácter en el descriptor de fichero que le digas (pantalla, salida de error o un fichero abierto). Es la pieza básica de las demás `ft_put*_fd`.

## Explicación sencilla

Un **descriptor de fichero** (*fd*) es un número entero que el sistema te da para identificar «a dónde escribes». Hay tres abiertos siempre al arrancar un programa (más en [[Descriptores de fichero y read]]):

| fd | Nombre | Normalmente es |
|---|---|---|
| 0 | stdin | el teclado (entrada) |
| 1 | stdout | la terminal (salida normal) |
| 2 | stderr | la terminal (mensajes de error) |

```c
ft_putchar_fd('A', 1);   /* imprime A en la terminal */
ft_putchar_fd('!', 2);   /* imprime ! por la salida de error */
```

```text
$ ./a.out 2>/dev/null
A
```

(La `!` no aparece porque `2>/dev/null` tira la salida de error.)

`write` necesita la **dirección** de los bytes a escribir, no el carácter en sí:

```text
  variable c (en la pila)      write(fd, &c, 1)
  ┌─────┐                        │      │   └── cuántos bytes
  │ 'A' │ ◄──────────────────────┘      │
  └─────┘   &c = dirección de c         └────── a dónde
```

## Prototipo

```c
void ft_putchar_fd(char c, int fd);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Envía el carácter ‘c’ al descriptor de archivo (file descriptor) especificado.

| | |
|---|---|
| **Parámetros** | `c`: El carácter a enviar.<br>`fd`: El descriptor de archivo sobre el que escribir. |
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
1. Llama a write con: el fd recibido, la dirección de c, y 1 byte.
2. Nada más: la función no devuelve nada.
```

Es literalmente una línea; está en el bloque de abajo.

## Puntos clave y casos límite

- `write(fd, &c, 1);`
- fd estándar: 0 = stdin, 1 = stdout, 2 = stderr.
- `'\0'` **también se escribe**: fuera de una cadena es un byte más (`0x00`), no un final. `ft_putchar_fd('\0', 1)` escribe 1 byte, igual que `putchar('\0')` ([[Carácter nulo y puntero NULL]]).
- Con un fd inválido (`-1`, uno sin abrir o uno ya cerrado) `write` no escribe nada y devuelve `-1`; la función no se cuelga ni peta.
- Los tests de esta función y su salida esperada están en [[libft - Edge cases y tests por función#ft_putchar_fd]].

> [!warning] Errores típicos
> - **Pasar `c` en vez de `&c`**: `write(fd, c, 1)` convierte el carácter en una dirección de memoria absurda. El compilador avisa (`makes pointer from integer without a cast`); con `-Werror` no compila.
> - **Escribir siempre en 1**: si ignoras `fd`, la función «funciona» en tus pruebas por pantalla pero falla al escribir en stderr o en un fichero.
> - **Saltarse el `'\0'`** con `if (!c) return ;`: el subject no hace ninguna excepción, así que `ft_putchar_fd('\0', fd)` debe escribir 1 byte. Ese `if` hace que tu función no se comporte igual que `write` o `putchar` y no te avisa de nada.
> - **Comprobar `if (fd < 0)`**: no hace falta. Con un fd inválido `write` ya falla sin hacer nada, y `fd >= 0` no garantiza que el fd esté abierto (`42` es positivo y también falla).
> - **Preocuparte por el valor de retorno de `write`**: el subject dice que la función no devuelve nada; con un fd inválido `write` devuelve -1 y no pasa nada más (no hay crash).

## Relacionadas

[[ft_putstr_fd]] · [[ft_putendl_fd]] · [[ft_putnbr_fd]] · [[Descriptores de fichero y read]] · [[Carácter nulo y puntero NULL]] · [[libft - Edge cases y tests por función]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 2 write` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [write(2) en man7.org](https://man7.org/linux/man-pages/man2/write.2.html).
