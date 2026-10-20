---
tags: [c, unix, fd, read, write, open, llamadas-al-sistema]
aliases: ["File descriptors", "File descriptor", "fd", "Descriptores de archivo", "open read write close"]
---
# Descriptores de fichero y read

← Inicio · C

> Un **descriptor de fichero** (*file descriptor*, **fd**) es un número entero pequeño que el sistema operativo te da para referirte a algo de lo que se puede leer o en lo que se puede escribir: un fichero, la terminal, una tubería… Con `open` consigues uno, con `read` y `write` lo usas y con `close` lo devuelves. Es la base de get_next_line, de `ft_putchar_fd` y familia y de ft_printf.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Llamada al sistema** (*syscall*) | Función que pide algo directamente al núcleo (kernel) del sistema: `open`, `read`, `write`, `close`, `fork`… Se documentan en la sección 2 del manual: `man 2 read` |
| **fd** | Índice en la tabla de ficheros abiertos de tu proceso. Para ti es solo un `int` |
| **EOF** (*end of file*) | Fin del fichero: ya no queda nada que leer |
| **`errno`** | Variable global de `<errno.h>` donde las syscalls dejan el **código** del último error |
| **`ssize_t`** | Entero *con signo* del tamaño de `size_t`. Lo devuelve `read`/`write` porque necesita poder valer `-1` |

## Qué es un fd

> [!example] La analogía del guardarropa
> En el guardarropa de un teatro no entras al almacén a buscar tu abrigo: te dan un ticket con un número, por ejemplo el 3. Cada vez que quieres algo, enseñas el 3 y el encargado se ocupa del resto. El fd es ese ticket: tú le dices al sistema «escribe en el 3» y el núcleo sabe a qué fichero corresponde y por dónde ibas.

Cada proceso tiene una tabla. El fd es la **posición** en esa tabla; el núcleo guarda detrás qué fichero es y por dónde vas leyendo:

```text
  tu programa                 núcleo (kernel)
 ┌──────────────┐     ┌──────────────────────────────────────┐
 │ int fd = 3; ─┼──►  │ 0 → terminal (teclado)        stdin  │
 └──────────────┘     │ 1 → terminal (pantalla)       stdout │
                      │ 2 → terminal (pantalla)       stderr │
                      │ 3 → texto.txt, posición = 8          │
                      │ 4 → (libre)                          │
                      └──────────────────────────────────────┘
```

Todo proceso arranca con tres fds ya abiertos:

| fd | Nombre | Constante (`<unistd.h>`) | Para qué |
|---|---|---|---|
| `0` | Entrada estándar | `STDIN_FILENO` | Lo que se teclea o llega por `<` o por una tubería |
| `1` | Salida estándar | `STDOUT_FILENO` | La salida normal del programa |
| `2` | Salida de error | `STDERR_FILENO` | Mensajes de error. Va a la pantalla aunque redirijas la salida con `>` |

`open` devuelve siempre **el número libre más bajo**. Por eso el primer fichero que abres suele ser el 3, y si cierras uno su número se reutiliza:

```c
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int	main(void)
{
	int	a;
	int	b;
	int	c;

	a = open("texto.txt", O_RDONLY);
	b = open("texto.txt", O_RDONLY);
	close(a);
	c = open("texto.txt", O_RDONLY);
	printf("a = %d, b = %d, c = %d\n", a, b, c);
	close(b);
	close(c);
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror varios.c -o var && ./var
a = 3, b = 4, c = 3
```

## El ciclo de vida: abrir, usar, cerrar

Trabajar con un fichero siempre sigue los mismos tres pasos:

```text
  1. open  ──►  te da un fd (o -1 si falla: compruébalo SIEMPRE)
       │
  2. read / write (fd, ...)  ──►  tantas veces como haga falta
       │
  3. close (fd)  ──►  devuelves el ticket; el número queda libre
```

Un ejemplo completo con [[ft_putchar_fd]]: crea `salida.txt` y escribe una `A`:

```c
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

void	ft_putchar_fd(char c, int fd)
{
	write(fd, &c, 1);
}

int	main(void)
{
	int	fd;

	fd = open("salida.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (fd == -1)
	{
		perror("salida.txt");
		return (1);
	}
	printf("fd = %d\n", fd);
	ft_putchar_fd('A', fd);
	ft_putchar_fd('\n', fd);
	close(fd);
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror ciclo.c -o ciclo && ./ciclo
fd = 3
$ cat salida.txt
A
$ ls -l salida.txt
-rw-r--r-- 1 ...  salida.txt
```

- **Paso 1**: `O_WRONLY | O_CREAT | O_TRUNC` significa «para escribir, créalo si no existe y vacíalo si ya existía». Las flags y el `0644` se explican abajo.
- **Paso 2**: `ft_putchar_fd` no sabe ni le importa que sea un fichero; solo recibe un número.
- **Paso 3**: sin `close`, el fd sigue ocupado hasta que el programa termina (ver [[#Errores frecuentes]]).

## Las cuatro llamadas

| Llamada | Prototipo | Devuelve si va bien | Si falla |
|---|---|---|---|
| `open` | `int open(const char *path, int flags, ...);` | El nuevo fd (≥ 0) | `-1` y `errno` |
| `read` | `ssize_t read(int fd, void *buf, size_t count);` | Bytes leídos (puede ser **menos** de `count`); `0` = EOF | `-1` y `errno` |
| `write` | `ssize_t write(int fd, const void *buf, size_t count);` | Bytes escritos | `-1` y `errno` |
| `close` | `int close(int fd);` | `0` | `-1` y `errno` |

`open` está en `<fcntl.h>`; `read`, `write` y `close` en `<unistd.h>`.

### Flags de `open`

Se combinan con `|` (OR de bits, ver [[Operadores de bits]]):

| Flag | Significado |
|---|---|
| `O_RDONLY` | Solo lectura |
| `O_WRONLY` | Solo escritura |
| `O_RDWR` | Lectura y escritura |
| `O_CREAT` | Créalo si no existe. **Obliga a pasar el tercer argumento**: los permisos, p. ej. `0644` |
| `O_TRUNC` | Si existe, vacíalo |
| `O_APPEND` | Escribe siempre al final |

### Permisos: qué significa `0644`

`0644` es un número en **octal** (el `0` inicial lo indica). Cada una de las tres últimas cifras son los permisos de un grupo de usuarios, y se obtiene sumando:

| Permiso | Letra | Vale |
|---|---|---|
| Lectura (*read*) | `r` | 4 |
| Escritura (*write*) | `w` | 2 |
| Ejecución (*execute*) | `x` | 1 |

```text
   0   6       4       4
       │       │       └── resto de usuarios: 4         = r--
       │       └────────── grupo:             4         = r--
       └────────────────── propietario (tú):  4 + 2     = rw-
                                                → ls -l muestra  -rw-r--r--
```

Es decir: tú puedes leer y escribir, los demás solo leer. Es lo habitual para crear un fichero de salida: `open(outfile, O_WRONLY | O_CREAT | O_TRUNC, 0644)`. Si el fichero ya existe, `open` **no** cambia sus permisos; el `0644` solo se usa al crearlo.

> [!info] Por qué a veces sale distinto
> El permiso final es `0644` menos lo que quite la **umask** del sistema (normalmente `0022`, que no quita nada aquí). Por eso con `0666` suele salir también `rw-r--r--`. Míralo con el comando `umask`.

## Leer por bloques

`read` no sabe de líneas: lee **como mucho** `count` bytes, y avanza la posición del fd. Hay que llamarla en bucle hasta que devuelva `0` (fin) o `-1` (error).

```c
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

#ifndef BUFFER_SIZE
# define BUFFER_SIZE 8
#endif

int	main(int argc, char **argv)
{
	int		fd;
	ssize_t	n;
	char	buf[BUFFER_SIZE + 1];

	if (argc != 2)
		return (1);
	fd = open(argv[1], O_RDONLY);
	if (fd == -1)
	{
		perror(argv[1]);
		return (1);
	}
	printf("fd = %d\n", fd);
	n = read(fd, buf, BUFFER_SIZE);
	while (n > 0)
	{
		buf[n] = '\0';
		printf("read devolvio %zd: \"%s\"\n", n, buf);
		n = read(fd, buf, BUFFER_SIZE);
	}
	printf("read devolvio %zd (fin de fichero)\n", n);
	close(fd);
	return (0);
}
```

Con un fichero de 3 líneas y bloques de 8 bytes:

```text
$ printf 'Hola, 42!\nSegunda linea\nFin\n' > texto.txt
$ cc -Wall -Wextra -Werror leer.c -o leer && ./leer texto.txt
fd = 3
read devolvio 8: "Hola, 42"
read devolvio 8: "!
Segund"
read devolvio 8: "a linea
"
read devolvio 4: "Fin
"
read devolvio 0 (fin de fichero)
```

Fíjate en lo que pasa:

```text
texto.txt:  H o l a ,   4 2 ! \n S e g u n d a   l i n e a \n F i n \n
            └─ read 1 (8) ──┘└─ read 2 (8) ──┘└─ read 3 (8) ──┘└ read 4 (4) ┘ → read 5: 0
                              ▲ el '\n' queda en medio del bloque
```

- Los bloques **no respetan las líneas**: el segundo `read` trae el final de la línea 1 y el principio de la 2.
- El último `read` útil devuelve **menos** de lo pedido (4).
- `read` **no pone `'\0'`**: lo añadimos nosotros en `buf[n]`, por eso el buffer mide `BUFFER_SIZE + 1`.

Con `-D BUFFER_SIZE=1000` lo lee todo de una vez (`read devolvio 28`). Esto es exactamente el problema de get_next_line: juntar bloques hasta encontrar un `'\n'`, devolver la línea y **guardar el sobrante** en una variable `static` para la siguiente llamada (ver [[Variables static y ámbito]] y -D BUFFER_SIZE).

> [!tip] Leer de la entrada estándar
> El fd `0` ya está abierto: `read(0, buf, BUFFER_SIZE)` lee lo que llega por teclado o por una tubería. Con el teclado, `read` vuelve en cuanto pulsas Enter (aunque no haya llenado el buffer), y devuelve `0` cuando pulsas Ctrl+D al principio de una línea.

## Escribir: `write` y la familia `ft_put*_fd`

```c
#include <fcntl.h>
#include <unistd.h>

static void	put_str_fd(char *s, int fd)
{
	int	len;

	len = 0;
	while (s[len])
		len++;
	write(fd, s, len);
}

int	main(void)
{
	int	fd;

	put_str_fd("esto va a la salida estandar (fd 1)\n", 1);
	put_str_fd("esto va a la salida de error (fd 2)\n", 2);
	fd = open("salida.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (fd == -1)
		return (1);
	put_str_fd("esto va al fichero\n", fd);
	close(fd);
	return (0);
}
```

```text
$ ./esc 2>/dev/null          ← tiro la salida de error
esto va a la salida estandar (fd 1)
$ ./esc >/dev/null           ← tiro la salida estándar
esto va a la salida de error (fd 2)
$ cat salida.txt
esto va al fichero
```

La **misma función** escribe en pantalla, en error o en un fichero: solo cambia el número. Por eso [[ft_putchar_fd]], [[ft_putstr_fd]], [[ft_putendl_fd]] y [[ft_putnbr_fd]] reciben un `fd`: el corrector puede pasarles `1`, `2` o un fichero abierto.

> [!info] `write` frente a `printf`
> `printf` guarda el texto en un buffer de la biblioteca y llama a `write` cuando le conviene (al ver `'\n'` en una terminal, al llenarse, al salir). `write` escribe **ya**. Mezclar ambos puede desordenar la salida.

## Errores: `-1` y `errno`

Cuando una syscall falla devuelve `-1` y deja en `errno` el motivo. `perror` y `strerror` lo traducen a texto:

```c
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int	main(void)
{
	int		fd;
	ssize_t	n;
	char	c;

	fd = open("no_existe.txt", O_RDONLY);
	printf("open: %d, errno = %d (%s)\n", fd, errno, strerror(errno));
	n = read(42, &c, 1);
	printf("read(42): %zd, errno = %d (%s)\n", n, errno, strerror(errno));
	fd = open("texto.txt", O_RDONLY);
	close(fd);
	n = read(fd, &c, 1);
	printf("read tras close: %zd, errno = %d (%s)\n", n, errno,
		strerror(errno));
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror errores.c -o err && ./err
open: -1, errno = 2 (No such file or directory)
read(42): -1, errno = 9 (Bad file descriptor)
read tras close: -1, errno = 9 (Bad file descriptor)
```

`errno = 2` es `ENOENT` y `9` es `EBADF`. Un fd inválido (negativo, nunca abierto o ya cerrado) da `EBADF`: así es como el corrector comprueba que get_next_line devuelve `NULL` con `fd = -1` o `fd = 42`.

> [!warning] `errno` solo vale justo después del fallo
> Las funciones que van bien **no** ponen `errno` a 0, y `printf` puede cambiarlo. Léelo o guárdalo inmediatamente después de recibir `-1`. Más en [[Control de errores en C]].

## Errores frecuentes

> [!danger] No cerrar los fds
> Cada proceso tiene un límite de fds abiertos (míralo con `ulimit -n`; en muchas instalaciones es 1024, aunque varía según el sistema). Si abres en un bucle sin `close`, a partir de ahí `open` devuelve `-1` con `EMFILE` (*Too many open files*).

> [!warning] Tratar `read` como si llenara siempre el buffer
> `read` puede devolver menos de lo pedido sin que sea el final. El final es **solo** cuando devuelve `0`.

> [!warning] Guardar el resultado de `read` en `size_t`
> `size_t` no tiene signo: el `-1` se convierte en un número enorme y tu `while (n > 0)` sigue. Usa `ssize_t` (ver [[Tipos enteros y conversiones]]).

> [!warning] `O_CREAT` sin permisos
> `open("out", O_WRONLY | O_CREAT)` sin el tercer argumento crea el fichero con permisos basura. Pon siempre `0644`.

> [!warning] Olvidar el `'\0'` tras `read`
> El buffer no es una cadena hasta que tú le pones el terminador en `buf[n]` (ver [[Carácter nulo y puntero NULL]]).

> [!question] Pregunta típica de evaluación
> **«¿Qué devuelve `read` y cómo distingues el final del fichero de un error?»**
> Devuelve el número de bytes leídos, que puede ser menor que el pedido. Devuelve `0` cuando no queda nada (EOF) y `-1` si hay un error (fd inválido, por ejemplo), dejando el motivo en `errno`. Por eso el bucle es `while (n > 0)` y después se mira si `n == -1` para liberar y devolver `NULL`.

## Relacionadas

[[Control de errores en C]] · [[Variables static y ámbito]] · Preprocesador y headers · [[Carácter nulo y puntero NULL]] · [[Operadores de bits]] · [[Tipos enteros y conversiones]] · [[ft_putchar_fd]] · [[ft_putstr_fd]] · [[ft_putendl_fd]] · [[ft_putnbr_fd]] · get_next_line · ft_printf

## Referencias

- [open(2), man7.org](https://man7.org/linux/man-pages/man2/open.2.html) — flags, permisos con `O_CREAT`, «the lowest-numbered file descriptor not currently open».
- [read(2), man7.org](https://man7.org/linux/man-pages/man2/read.2.html) — valor de retorno, `0` en fin de fichero, lecturas parciales.
- [write(2), man7.org](https://man7.org/linux/man-pages/man2/write.2.html) — valor de retorno y errores.
- [umask(2), man7.org](https://man7.org/linux/man-pages/man2/umask.2.html) — cómo la umask recorta los permisos que pasas a `open`.
- [chmod(1), man7.org](https://man7.org/linux/man-pages/man1/chmod.1.html) — permisos en octal: lectura 4, escritura 2, ejecución 1.
- [close(2), man7.org](https://man7.org/linux/man-pages/man2/close.2.html) — reutilización de fds.
- [errno(3), man7.org](https://man7.org/linux/man-pages/man3/errno.3.html) — `ENOENT`, `EBADF`, `EMFILE`; cuándo es válido leer `errno`.
- [stdin(3), man7.org](https://man7.org/linux/man-pages/man3/stdin.3.html) — fds 0, 1 y 2 y `STDIN_FILENO`…
- [Beej's Guide to Unix IPC](https://beej.us/guide/bgipc/) — introducción a fds en el contexto de tuberías.
- Salidas obtenidas con Ubuntu clang 12.0.1 en Ubuntu 22.04.
