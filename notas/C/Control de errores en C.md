---
tags: [c, errores, malloc, errno, memoria]
---
# Control de errores en C

← Inicio · C

> C no tiene excepciones: **cada función avisa de un error con su valor de retorno**, y es responsabilidad de quien la llama comprobarlo. Si no lo compruebas, el programa sigue como si nada… hasta que crashea más adelante, lejos de la causa.

| Término | Qué significa |
|---|---|
| **Valor de retorno** | Lo que devuelve una función con `return`. En C es el canal normal para avisar de un fallo |
| **Propagar un error** | Devolver tú también un valor de error para que lo gestione quien te llamó |
| **Llamada al sistema** (*syscall*) | Función que pide algo al núcleo del sistema operativo: `open`, `read`, `write`, `close`… |
| **`errno`** | Variable global donde el sistema deja un número que explica el último fallo |
| **Fuga de memoria** (*leak*) | Memoria reservada con `malloc` que ya nadie puede liberar porque se ha perdido su dirección |
| **stderr** | Salida de error, el *file descriptor* 2 (ver [[Descriptores de fichero y read]]) |

## Cómo avisa cada función

| Tipo de función | Valor si falla | Ejemplos |
|---|---|---|
| Devuelve un puntero | `NULL` | `malloc`, [[ft_calloc]], [[ft_strdup]], [[ft_split]], [[ft_lstnew]] |
| Llamada al sistema | `-1` (y pone `errno`) | `open`, `read`, `write`, `close` |
| Devuelve un estado | Lo que diga su `man` (`-1`, `0`, `EOF`…) | `printf` → negativo |
| No puede fallar o no avisa | — | [[ft_strlen]], [[ft_atoi]] (¡`"abc"` devuelve `0`, igual que `"0"`!) |

> [!tip] Regla de oro
> Antes de usar una función, mira en su `man` la sección **RETURN VALUE**: ahí dice qué devuelve cuando falla.

## Comprobar siempre `malloc`

`malloc` puede devolver `NULL` (sin memoria, tamaño absurdo…). Usar ese `NULL` provoca un segfault (el programa intenta tocar una dirección prohibida y el sistema lo mata con la señal `SIGSEGV`; ver [[Carácter nulo y puntero NULL]]).

```c
char	*dup_str(const char *s)
{
	char	*dup;
	size_t	len;

	len = ft_strlen(s) + 1;
	dup = malloc(len);
	if (!dup)
		return (NULL);
	ft_memcpy(dup, s, len);
	return (dup);
}
```

El error **se propaga hacia arriba**: la función no sabe qué hacer con el fallo, así que devuelve `NULL` y quien la llamó decide.

## Liberar lo reservado antes de salir

Si una función hace varios `malloc` y falla el tercero, hay que **liberar los dos anteriores** antes de devolver `NULL`. Si no, hay fuga de memoria. Es el caso de [[ft_split]] o [[ft_lstmap]].

```c
static void	*free_partial(char **arr, size_t filled)
{
	while (filled > 0)
	{
		filled--;
		free(arr[filled]);
	}
	free(arr);
	return (NULL);
}

char	**dup_all(char **src, size_t n)
{
	char	**arr;
	size_t	i;

	arr = malloc(sizeof(char *) * (n + 1));
	if (!arr)
		return (NULL);
	i = 0;
	while (i < n)
	{
		arr[i] = dup_str(src[i]);
		if (!arr[i])
			return (free_partial(arr, i));
		i++;
	}
	arr[n] = NULL;
	return (arr);
}
```

> [!note] Sin `goto`
> En C es habitual limpiar con `goto cleanup;`, pero la [[La Norma|Norma]] de 42 prohíbe `goto`. La alternativa es una **función auxiliar de limpieza** que libere y devuelva `NULL`, para poder escribir `return (free_partial(arr, i));` en una sola línea.

## Llamadas al sistema: `-1` y `errno`

Las llamadas al sistema devuelven `-1` y guardan el motivo en la variable global **`errno`** (`<errno.h>`). Para mostrarlo:

| Función | Qué hace | Ejemplo de salida |
|---|---|---|
| `perror("open")` | Escribe en stderr tu texto + el mensaje de `errno` | `open: No such file or directory` |
| `strerror(errno)` | Devuelve el mensaje como cadena, para formatearlo tú | `"No such file or directory"` |

```c
static int	print_file(const char *path)
{
	char	buf[64];
	int		fd;
	ssize_t	bytes;

	fd = open(path, O_RDONLY);
	if (fd == -1)
	{
		perror(path);
		return (-1);
	}
	bytes = read(fd, buf, sizeof(buf));
	while (bytes > 0)
	{
		if (write(1, buf, bytes) == -1)
		{
			perror("write");
			close(fd);
			return (-1);
		}
		bytes = read(fd, buf, sizeof(buf));
	}
	if (bytes == -1)
		perror("read");
	close(fd);
	return ((int)bytes);
}
```

Al salir del bucle, `bytes` vale `0` (fin de fichero, todo bien) o `-1` (error de `read`), así que la función devuelve `0` o `-1`. Fíjate en que **cada camino de error cierra el `fd`** antes de volver: un fichero abierto que no se cierra también es una fuga. Más sobre `open`/`read` en [[Descriptores de fichero y read]].

```text
$ ./prog /no/existe
/no/existe: No such file or directory
```

> [!warning] Cuidado con `errno`
> - **Solo tiene sentido justo después de que una función falle.** Si la función tuvo éxito, `errno` puede tener un valor viejo de otro error.
> - Cualquier otra llamada (incluso `printf`) puede cambiarlo: léelo o muéstralo **inmediatamente**.
> - `perror` y `strerror` solo se pueden usar si el **subject** los autoriza (libft no; en otros proyectos depende: compruébalo en la lista de funciones permitidas de tu subject).

## Desbordamientos de enteros

Algunos errores no avisan: el número simplemente da la vuelta.

- **Multiplicar tamaños**: `nmemb * size` puede desbordar `size_t` y reservar **menos** de lo pedido. Compruébalo antes, como hace el `calloc` original:
  ```c
  if (size != 0 && nmemb > SIZE_MAX / size)
  	return (NULL);
  ```
  `SIZE_MAX` (el mayor valor posible de un `size_t`) está en `<stdint.h>`. Ver [[ft_calloc]].
- **`size_t` por debajo de 0**: `size_t` es un entero **sin signo** (no puede ser negativo). `ft_strlen(s) - 1` con `s == ""` no da `-1`: «da la vuelta» y vale 18446744073709551615 en 64 bits. Más en [[Tipos enteros y conversiones]].
- **Convertir texto a número**: [[ft_atoi]] no detecta `"99999999999"` ni `"12abc"`. En proyectos como push_swap tendrás que escribir tu propia versión que valide.

## Validar la entrada

- **Argumentos del programa**: comprueba `argc` antes de leer `argv[1]`. Si no hay argumento, `argv[1]` es `NULL` (ver el ejemplo de [[Depurar con gdb]]).
- **Parámetros `NULL`**: las funciones originales de la libc crashean con `NULL` (es comportamiento indefinido). En libft lo correcto es **imitar al original**; en tus propios proyectos, decide y sé coherente.
- **Formato de los datos**: en push_swap (los números de `argv`), en A-Maze-ing (el fichero de configuración), etc., valida todo lo que viene de fuera antes de usarlo.

## Informar del error y salir

- Los mensajes de error van a la **salida de error (fd 2)**, no a la estándar: `ft_putstr_fd("Error\n", 2);` (ver [[ft_putstr_fd]]). Así no se mezclan con la salida normal del programa.
- El código de salida le dice al sistema si todo fue bien: `return (EXIT_SUCCESS);` (0) o `return (EXIT_FAILURE);` (1), definidos en `<stdlib.h>`.
- Muchos subjects piden un mensaje exacto, por ejemplo `"Error\n"`. Respétalo al pie de la letra.
- Antes de salir por un error, **libera lo que tengas reservado**: el sistema recupera la memoria al terminar, pero valgrind lo marcará y en la evaluación cuenta como leak.

```c
if (argc < 2)
{
	ft_putstr_fd("Error: falta el archivo\n", 2);
	return (EXIT_FAILURE);
}
```

```bash
$ ./prog; echo "código de salida: $?"
Error: falta el archivo
código de salida: 1
```

## Herramientas para encontrar los errores que se escapan

| Herramienta | Encuentra | Uso |
|---|---|---|
| `-Wall -Wextra -Werror` | Variables sin inicializar, tipos incorrectos, retornos olvidados | Siempre al compilar |
| `-fsanitize=address -g` | Desbordamientos de buffer (también en el stack), *use-after-free*, leaks en Linux (al ejecutar) | `cc -fsanitize=address -g *.c` |
| `valgrind` | Leaks, accesos inválidos al heap y uso de memoria sin inicializar | `valgrind --leak-check=full ./prog` |
| `gdb` | Dónde y por qué crashea, paso a paso | Ver [[Depurar con gdb]] |

Uso detallado de las dos primeras en [[Valgrind y sanitizers]].

## Errores frecuentes

| ❌ Error | Qué pasa | ✅ Arreglo |
|---|---|---|
| Usar el resultado de `malloc` sin comprobarlo | Segfault cuando no hay memoria | `if (!ptr) return (NULL);` justo después |
| Devolver `NULL` sin liberar lo anterior | Leak en el camino de error | Función auxiliar tipo `free_partial` |
| Leer `errno` tras una llamada que ha ido bien | Mensaje de un error viejo | Mira `errno` solo si la función ha devuelto error |
| Escribir el error con `printf` | Va a stdout (fd 1) y se mezcla con la salida | `ft_putstr_fd("Error\n", 2)` |
| Olvidar `close(fd)` en un `return` de error | Fuga de descriptores | Cierra antes de cada `return` |

## Checklist

- [ ] Cada `malloc` (y cada función que reserva) tiene su `if (!ptr)`.
- [ ] Si falla un `malloc` a mitad, libero todo lo anterior.
- [ ] Cada `open`/`read`/`write` comprueba el `-1`.
- [ ] Compruebo `argc` antes de usar `argv`.
- [ ] Los errores van por el fd 2 con el mensaje que pide el subject.
- [ ] Salgo con `EXIT_FAILURE` cuando algo falla.
- [ ] `valgrind` no muestra leaks, ni siquiera en los caminos de error.

## Relacionadas

[[Valgrind y sanitizers]] · [[Depurar con gdb]] · [[Descriptores de fichero y read]] · [[Tipos enteros y conversiones]] · [[Segmentos de memoria en C]] · [[Arrays en C]] · [[Carácter nulo y puntero NULL]] · [[La Norma]] · [[libft - Anexo comparativo]]

## Referencias

- [malloc(3) — Linux man-pages](https://man7.org/linux/man-pages/man3/malloc.3.html) — `malloc`/`calloc` devuelven `NULL` al fallar; `calloc` comprueba el desbordamiento de `nmemb * size`.
- [errno(3)](https://man7.org/linux/man-pages/man3/errno.3.html) — `errno` solo es significativo cuando la función indica error.
- [perror(3)](https://man7.org/linux/man-pages/man3/perror.3.html) y [strerror(3)](https://man7.org/linux/man-pages/man3/strerror.3.html) — formato de los mensajes.
- [open(2)](https://man7.org/linux/man-pages/man2/open.2.html) y [read(2)](https://man7.org/linux/man-pages/man2/read.2.html) — devuelven `-1` y ponen `errno`.
- [exit(3)](https://man7.org/linux/man-pages/man3/exit.3.html) — `EXIT_SUCCESS` y `EXIT_FAILURE`.
- [Valgrind: Memcheck manual](https://valgrind.org/docs/manual/mc-manual.html) — qué errores detecta memcheck.
- La Norma v4 (`Normativa 42/es.norm-2.pdf`) — prohíbe `goto`, máximo 25 líneas por función.
- Ejemplo de `print_file` comprobado con `cc -Wall -Wextra -Werror` (clang 12, Ubuntu 22.04).
