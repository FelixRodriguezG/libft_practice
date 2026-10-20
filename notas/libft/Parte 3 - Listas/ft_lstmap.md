---
tags: [libft, libft/parte3]
funcion: ft_lstmap
original: ninguna
externas: "malloc, free"
estado: pendiente
---
# ft_lstmap

[[libft - Índice|← Índice]] · Parte 3 · Listas enlazadas

> Crea una lista **nueva** del mismo tamaño en la que cada contenido es `f(contenido original)`. La lista original no cambia. Si algo falla a medias, debe liberar todo lo que había creado y devolver `NULL`.

## Explicación sencilla

Es a las listas lo que [[ft_strmapi]] es a las cadenas.

```c
void	*duplicar_mayus(void *content)
{
	char	*copia;

	copia = ft_strdup((char *)content);
	/* ...pasar copia a mayúsculas (si no es NULL)... */
	return (copia);
}

t_list	*nueva = ft_lstmap(lista, duplicar_mayus, free);
```

```text
 lista ──► [ "ab" | ● ]──► [ "cd" | NULL ]        (no se toca)
               │               │
             f(...)          f(...)
               ▼               ▼
 nueva ──► [ "AB" | ● ]──► [ "CD" | NULL ]        (nodos y contenidos nuevos)
```

Dos punteros a función en el mismo prototipo ([[Punteros en C]]):

| Parámetro | Tipo | Qué hace |
|---|---|---|
| `f` | `void *(*f)(void *)` | recibe un contenido y **devuelve** el contenido nuevo |
| `del` | `void (*del)(void *)` | sabe liberar un contenido nuevo si hay que deshacer |

## Prototipo

```c
t_list *ft_lstmap(t_list *lst, void *(*f)(void *), void (*del)(void *));
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Itera la lista ‘lst’ y aplica la función ‘f’ al contenido de cada nodo. Crea una lista resultante de aplicar sucesivamente la función ‘f’ a cada nodo. La función ‘del’ se utiliza para eliminar el contenido de un nodo si es necesario.

| | |
|---|---|
| **Parámetros** | `lst`: un puntero a un nodo.<br>`f`: la dirección de un puntero a una función usada en la iteración de cada elemento de la lista.<br>`del`: un puntero a función utilizado para eliminar el contenido de un nodo, si es necesario. |
| **Valor devuelto** | La nueva lista.<br>NULL si falla la reserva de memoria. |
| **Funciones autorizadas** | malloc, free |

## Funciones externas (man)

> [!quote] man 3 malloc — RETURN VALUE
> The malloc() and calloc() functions return a pointer to the allocated memory, which is suitably aligned for any built-in type.  On error, these functions return NULL.

> [!note] Traducción
> malloc() y calloc() devuelven un puntero a la memoria reservada, alineada adecuadamente para cualquier tipo predefinido. En caso de error, devuelven NULL.

> [!quote] man 3 free — DESCRIPTION
> The free() function frees the memory space pointed to by ptr, which must have been returned by a previous call to malloc(), calloc(), or realloc().  Otherwise, or if free(ptr) has already been called before, undefined behavior occurs.  If ptr is NULL, no operation is performed.

> [!note] Traducción
> La función free() libera el espacio de memoria apuntado por ptr, que debe haber sido devuelto por una llamada previa a malloc(), calloc() o realloc(). Si no, o si ya se llamó antes a free(ptr), el comportamiento es indefinido. Si ptr es NULL, no se hace nada.

## Cómo implementarla

```text
1. Si lst, f o del son NULL → devuelve NULL.
2. nueva = NULL
3. Mientras lst no sea NULL:
       contenido = f(lst->content)
       nodo = ft_lstnew(contenido)
       si nodo es NULL:                     ← falló malloc
           del(contenido)                   (el contenido aún no está en ningún nodo)
           ft_lstclear(&nueva, del)         (libera todo lo creado hasta ahora)
           devuelve NULL
       ft_lstadd_back(&nueva, nodo)
       lst = lst->next
4. Devuelve nueva.
```

> [!tip] Rendimiento
> `ft_lstadd_back` recorre la lista entera en cada llamada (n² pasos en total). Para libft es aceptable; si quieres afinar, guarda un puntero al último nodo añadido y engancha ahí.

## Puntos clave y casos límite

- Si falla un `ft_lstnew`, libera el contenido recién creado con `del` y toda la lista nueva con `ft_lstclear`, y devuelve NULL.
- La lista original no se modifica.

> [!danger] El camino de error es lo que se evalúa
> - **Devolver NULL sin limpiar**: los nodos ya creados y sus contenidos se quedan sin dueño → leak. Los testers simulan fallos de `malloc` para comprobarlo ([[Valgrind y sanitizers]], [[Control de errores en C]]).
> - **Olvidar `del(contenido)`** cuando falla `ft_lstnew`: ese contenido lo creó `f` pero todavía no está en la lista nueva, así que `ft_lstclear` no lo verá.
> - **Usar `del` sobre la lista original**: `del` es para los contenidos **nuevos**; la original pertenece a quien llama.
> - **Reutilizar los nodos originales** (cambiar `lst->content` en el sitio): eso sería [[ft_lstiter]], no `ft_lstmap`, y rompe la lista de quien llama.

> [!note] ¿Y si `f` devuelve NULL?
> El subject no lo trata. Muchas implementaciones lo aceptan como contenido válido (un nodo con `content == NULL`); otras lo consideran fallo y limpian. Elige una y sé capaz de justificarla en la evaluación.

## Relacionadas

[[ft_lstnew]] · [[ft_lstclear]] · [[ft_lstiter]] · [[ft_lstadd_back]] · [[ft_strmapi]] · [[Listas enlazadas]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 malloc` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [malloc(3) en man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html).
- `man 3 free` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [free(3) en man7.org](https://man7.org/linux/man-pages/man3/free.3.html).
