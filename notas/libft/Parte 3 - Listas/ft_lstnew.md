---
tags: [libft, libft/parte3]
funcion: ft_lstnew
original: ninguna
externas: "malloc"
estado: pendiente
---
# ft_lstnew

[[libft - Índice|← Índice]] · Parte 3 · Listas enlazadas

> Reserva un nodo nuevo de tipo `t_list`, guarda en él el puntero `content` y deja `next` a `NULL`. Es la única función de la Parte 3 que crea nodos.

## Explicación sencilla

Una [[Listas enlazadas|lista enlazada]] es una cadena de **nodos**: cada nodo guarda un dato y la dirección del siguiente. En libft el nodo es este `struct` (ver [[Structs y typedef]]):

```c
typedef struct s_list
{
	void			*content;   /* puntero a cualquier dato */
	struct s_list	*next;      /* siguiente nodo, o NULL si es el último */
}	t_list;
```

```c
char	*txt = ft_strdup("hola");
t_list	*nodo = ft_lstnew(txt);
```

```text
 txt ──────────────────────────┐
                               ▼
 nodo ──► ┌───────────────┐   ┌───┬───┬───┬───┬────┐
          │ content ──────┼──►│ h │ o │ l │ a │ \0 │
          ├───────────────┤   └───┴───┴───┴───┴────┘
          │ next = NULL   │
          └───────────────┘
          (malloc de sizeof(t_list) = 16 bytes en 64 bits)
```

El nodo **no copia** `"hola"`: guarda la misma dirección que `txt`. Por eso, al liberar, la cadena se libera una sola vez (con `del`, ver [[ft_lstdelone]]).

## Prototipo

```c
t_list *ft_lstnew(void *content);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Reserva memoria (usando malloc(3)) y devuelve un nuevo nodo. La variable ‘content’ se inicializa con el contenido del parámetro ‘content’. Mientras que la variable ‘next’ se inicializa con NULL.

| | |
|---|---|
| **Parámetros** | `content`: el contenido con el que se crea el nodo. |
| **Valor devuelto** | Un puntero al nuevo nodo |
| **Funciones autorizadas** | malloc |

## Funciones externas (man)

> [!quote] man 3 malloc — RETURN VALUE
> The malloc() and calloc() functions return a pointer to the allocated memory, which is suitably aligned for any built-in type.  On error, these functions return NULL.

> [!note] Traducción
> malloc() y calloc() devuelven un puntero a la memoria reservada, alineada adecuadamente para cualquier tipo predefinido. En caso de error, devuelven NULL.

## Cómo implementarla

```text
1. nodo = malloc(sizeof(t_list)). Si falla → devuelve NULL.
2. nodo->content = content
3. nodo->next = NULL
4. Devuelve nodo.
```

## Puntos clave y casos límite

- No copia el contenido: guarda el puntero tal cual.
- Devuelve NULL si `malloc` falla.

> [!warning] Errores típicos
> - **`malloc(sizeof(t_list *))`**: reservas el tamaño de un **puntero** (8 bytes), no del nodo (16). Al escribir `next` te sales del bloque. Valgrind: *Invalid write of size 8* ([[Valgrind y sanitizers]]).
> - **Olvidar `next = NULL`**: `malloc` no pone ceros; `next` tendría basura y [[ft_lstsize]] o [[ft_lstlast]] seguirían ese puntero hasta un *segfault*.
> - **Copiar el contenido** (con `ft_strdup` o similar): el subject dice que se inicializa con el parámetro; además no sabes de qué tipo es (`void *`).
> - **`content == NULL`** es válido: crea el nodo igual.
> - **Declarar el nodo como variable local** (`t_list n;` y devolver `&n`): esa memoria desaparece al salir de la función ([[Segmentos de memoria en C]]).

## Relacionadas

[[ft_lstadd_front]] · [[ft_lstadd_back]] · [[ft_lstdelone]] · [[Listas enlazadas]] · [[Structs y typedef]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — definición de `t_list`, descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 malloc` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [malloc(3) en man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html).
