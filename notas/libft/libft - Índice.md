---
tags: [libft, indice]
---
# libft - Índice

← Inicio · libft

> **libft** es el primer proyecto del Common Core: programar tu propia **librería estática** (`libft.a`) con funciones de la libc rehechas por ti (Parte 1), funciones nuevas de cadenas y salida (Parte 2) y funciones de listas enlazadas (Parte 3). La usarás en muchos proyectos posteriores. Esta nota es el índice de todas sus funciones.

En la Parte 1 cada nota cita literalmente el `man` de la función original (en inglés) con su traducción al español. La Parte 2 y la Parte 3 no tienen función original: se citan literalmente del subject (v19.3).

> [!note] Vocabulario
> - **libc**: la librería estándar de C que ya trae el sistema (`strlen`, `malloc`, `printf`…).
> - **Librería estática** (`.a`): un paquete de ficheros `.o` que se une a tu programa al compilar. Ver [[Makefile y librerías estáticas]].
> - **Funciones externas**: funciones que no has escrito tú y que el subject te deja usar (columna «Externas» de las tablas).
> - **`man`**: el manual del sistema. `man 3 strlen` abre la página de `strlen` (ver [[#Cómo consultar el manual]]).

> [!tip] Anexo
> [[libft - Anexo comparativo]] — funciones agrupadas por uso y comparadas entre sí (pros, contras y cuándo usar cada una).

> [!info] Conceptos clave
> - [[Carácter nulo y puntero NULL]] — `'\0'` termina cadenas; `NULL` termina arrays de punteros (`ft_split`) y listas (Parte 3).
> - [[Punteros en C]] y [[Arrays en C]] — casi todas las funciones reciben punteros a memoria o a cadenas.
> - [[Segmentos de memoria en C]] — dónde vive cada dato (pila, heap, literales de solo lectura).
> - [[Listas enlazadas]] y [[Structs y typedef]] — la base de la Parte 3.
> - [[libft - Edge cases y tests por función]] — un `main` por función, con su happy path y sus edge cases, para la defensa.

## Parte 1 — Funciones de la libc

### Caracteres

| Función | Original | Cabecera | Descripción |
|---|---|---|---|
| [[ft_isalpha]] | `man 3 isalpha` | `<ctype.h>` | ¿Es una letra? |
| [[ft_isdigit]] | `man 3 isdigit` | `<ctype.h>` | ¿Es un dígito decimal? |
| [[ft_isalnum]] | `man 3 isalnum` | `<ctype.h>` | ¿Es letra o dígito? |
| [[ft_isascii]] | `man 3 isascii` | `<ctype.h>` | ¿Está en la tabla ASCII (0–127)? |
| [[ft_isprint]] | `man 3 isprint` | `<ctype.h>` | ¿Es imprimible (espacio incluido)? |
| [[ft_toupper]] | `man 3 toupper` | `<ctype.h>` | Minúscula → mayúscula |
| [[ft_tolower]] | `man 3 tolower` | `<ctype.h>` | Mayúscula → minúscula |

### Memoria

| Función | Original | Cabecera | Descripción |
|---|---|---|---|
| [[ft_memset]] | `man 3 memset` | `<string.h>` | Rellena n bytes con un valor |
| [[ft_bzero]] | `man 3 bzero` | `<strings.h>` | Pone n bytes a cero |
| [[ft_memcpy]] | `man 3 memcpy` | `<string.h>` | Copia n bytes (sin solapamiento) |
| [[ft_memmove]] | `man 3 memmove` | `<string.h>` | Copia n bytes (permite solapamiento) |
| [[ft_memchr]] | `man 3 memchr` | `<string.h>` | Busca un byte en n bytes de memoria |
| [[ft_memcmp]] | `man 3 memcmp` | `<string.h>` | Compara n bytes de memoria |

### Cadenas

| Función | Original | Cabecera | Descripción |
|---|---|---|---|
| [[ft_strlen]] | `man 3 strlen` | `<string.h>` | Longitud de una cadena |
| [[ft_strlcpy]] | `man 3bsd strlcpy` | `<string.h> / <bsd/string.h>` | Copia segura con tamaño de buffer |
| [[ft_strlcat]] | `man 3bsd strlcat` | `<string.h> / <bsd/string.h>` | Concatenación segura con tamaño de buffer |
| [[ft_strchr]] | `man 3 strchr` | `<string.h>` | Primera aparición de un carácter |
| [[ft_strrchr]] | `man 3 strrchr` | `<string.h>` | Última aparición de un carácter |
| [[ft_strncmp]] | `man 3 strncmp` | `<string.h>` | Compara hasta n caracteres |
| [[ft_strnstr]] | `man 3bsd strnstr` | `<string.h> / <bsd/string.h>` | Busca una subcadena en los primeros len caracteres |

### Conversión

| Función | Original | Cabecera | Descripción |
|---|---|---|---|
| [[ft_atoi]] | `man 3 atoi` | `<stdlib.h>` | Cadena → int |

### Memoria dinámica

| Función | Original | Cabecera | Descripción |
|---|---|---|---|
| [[ft_calloc]] | `man 3 calloc` | `<stdlib.h>` | Reserva memoria inicializada a cero |
| [[ft_strdup]] | `man 3 strdup` | `<string.h>` | Duplica una cadena en memoria nueva |

## Parte 2 — Funciones adicionales

| Función | Externas | Descripción |
|---|---|---|
| [[ft_substr]] | malloc | Subcadena desde start de longitud máxima len |
| [[ft_strjoin]] | malloc | Concatena dos cadenas en memoria nueva |
| [[ft_strtrim]] | malloc | Elimina caracteres de set al principio y al final |
| [[ft_split]] | malloc, free | Divide una cadena por un delimitador |
| [[ft_itoa]] | malloc | int → cadena |
| [[ft_strmapi]] | malloc | Nueva cadena aplicando f(índice, carácter) |
| [[ft_striteri]] | Ninguna | Aplica f(índice, &carácter) en el sitio |
| [[ft_putchar_fd]] | write | Escribe un carácter en un fd |
| [[ft_putstr_fd]] | write | Escribe una cadena en un fd |
| [[ft_putendl_fd]] | write | Escribe una cadena + salto de línea en un fd |
| [[ft_putnbr_fd]] | write | Escribe un entero en un fd |

> [!info] Las cuatro `ft_put*_fd` escriben en un **descriptor de fichero** (`1` pantalla, `2` errores o un fichero abierto con `open`). Si no sabes qué es un fd, empieza por [[Descriptores de fichero y read]].

## Parte 3 — Listas enlazadas

```c
typedef struct s_list
{
	void			*content;
	struct s_list	*next;
}					t_list;
```

- `content`: los datos contenidos en el nodo. Usar `void *` permite almacenar cualquier tipo de dato.
- `next`: la dirección del siguiente nodo, o NULL si el nodo actual es el último de la lista (ver [[Carácter nulo y puntero NULL]]).

| Función | Externas | Descripción |
|---|---|---|
| [[ft_lstnew]] | malloc | Crea un nodo nuevo |
| [[ft_lstadd_front]] | Ninguna | Añade un nodo al principio |
| [[ft_lstsize]] | Ninguna | Cuenta los nodos |
| [[ft_lstlast]] | Ninguna | Devuelve el último nodo |
| [[ft_lstadd_back]] | Ninguna | Añade un nodo al final |
| [[ft_lstdelone]] | free | Libera un nodo y su contenido |
| [[ft_lstclear]] | free | Libera toda la lista |
| [[ft_lstiter]] | Ninguna | Aplica f al contenido de cada nodo |
| [[ft_lstmap]] | malloc, free | Nueva lista aplicando f a cada contenido |

## Reglas generales del subject (v19.3)

- Archivos a entregar: `Makefile`, `libft.h` y `ft_*.c`, **todos en la raíz del repositorio** (y `libft.a` se crea también en la raíz). **Prohibido entregar archivos no utilizados.**
- Mismos prototipos y comportamiento que las originales (según su `man`), con el prefijo `ft_`.
- Prohibido usar `restrict` en los prototipos y compilar con `-std=c99`.
- Las funciones de la Parte 1 no pueden depender de funciones externas (salvo `malloc` en `calloc` y `strdup`).
- `isalpha`, `isdigit`, `isalnum`, `isascii`, `isprint` devuelven **1 o 0**.
- `calloc` con `nmemb` o `size` a 0 → puntero único liberable con `free()`.
- Sin variables globales; las funciones auxiliares deben ser `static` (ver [[Variables static y ámbito]]).
- Compilar con `cc -Wall -Werror -Wextra`; generar la librería con `ar` (prohibido `libtool`).
- Makefile con `$(NAME)`, `all`, `clean`, `fclean`, `re` y sin relink.
- Sin leaks, y ninguna función debe crashear (segfault, bus error, double free…) salvo en casos de comportamiento indefinido. Si crashea, el proyecto es «no funcional» y es un 0.
- Todo el código, también las funciones auxiliares, debe pasar la Norma: un solo error es un 0.
- Las listas enlazadas son la **Parte 3, obligatoria**: en esta versión del subject libft no tiene parte bonus.
- Hace falta un `README.md` en la raíz:
  - Primera línea en cursiva: *Este proyecto ha sido creado como parte del currículo de 42 por <login>*.
  - Secciones «Descripción», «Instrucciones» (compilar, usar) y «Recursos» (referencias y **para qué se ha usado IA**, si se ha usado).
  - En libft, además, una descripción detallada de la librería.
- En la evaluación pueden pedirte una **pequeña modificación** del código para comprobar que lo entiendes.

> [!warning] Los tests no se entregan
> Los `main.c` de prueba, los testers y cualquier regla extra del Makefile para ejecutarlos son para ti. Como el subject prohíbe entregar archivos no utilizados y la Norma pide fuentes nombradas explícitamente (nada de `$(wildcard ...)`), quítalos antes de la entrega final. Para la defensa, cada `ft_*.c` lleva al final su `main` de prueba **comentado** (no se compila); cómo usarlo, en [[libft - Edge cases y tests por función]]. Ver también [[Git para 42]].

Más detalle en [[La Norma]] y [[Makefile y librerías estáticas]].

## Progreso

Cada nota tiene la propiedad `estado` (`hecho` / `pendiente`). Cámbiala al terminar una función.

## Cómo consultar el manual

- Sección 3 = funciones de biblioteca: `man 3 strlen`.
- `strlcpy`, `strlcat` y `strnstr` no están en glibc; vienen de **libbsd**: `man 3bsd strlcpy`. Para compilar tests con la original: `#include <bsd/string.h>` y `-lbsd`.
- Las secciones que más importan son **DESCRIPTION**, **RETURN VALUE** y **NOTES**.
- Las citas son de Linux man-pages 5.10 (Ubuntu 22.04). En los Mac de 42 la redacción del man (BSD) puede variar.
- Desde glibc 2.38 (posterior a la de Ubuntu 22.04), `strlcpy` y `strlcat` ya están en `<string.h>` sin `libbsd`; `strnstr` sigue siendo solo de BSD.

## Relacionadas

[[libft - Anexo comparativo]] · [[libft - Edge cases y tests por función]] · [[Makefile y librerías estáticas]] · [[La Norma]] · [[Carácter nulo y puntero NULL]] · [[Punteros en C]] · [[Listas enlazadas]] · [[Valgrind y sanitizers]] · [[Depurar con gdb]] · [[Git para 42]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — lista de funciones, reglas generales, consideraciones técnicas y requisitos del README.
- `man 3 <función>` y `man 3bsd strlcpy` (Linux man-pages 5.10 y libbsd, Ubuntu 22.04) — comportamiento de las funciones originales de la Parte 1.
- [man7.org: strlcpy(3)](https://man7.org/linux/man-pages/man3/strlcpy.3.html) — `strlcpy`/`strlcat` disponibles en glibc desde la 2.38.
- La Norma v4 (`Normativa 42/es.norm-2.pdf`) — reglas de estilo que se aplican a todos los ficheros.
