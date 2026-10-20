---
tags: [libft, libft/parte3]
funcion: ft_lstclear
original: ninguna
externas: "free"
estado: pendiente
---
# ft_lstclear

[[libft - Índice|← Índice]] · Parte 3 · Listas enlazadas

> Libera **toda** la lista a partir del nodo dado: cada contenido con `del` y cada nodo con `free`. Al terminar deja el puntero de quien llama a `NULL`.

## Explicación sencilla

El problema: en cuanto liberas un nodo, ya no puedes leer su `next`. Así que primero te guardas el siguiente y luego liberas el actual.

```text
 paso 0:  *lst ──► [A| ● ]──► [B| ● ]──► [C|NULL]

 paso 1:  sig = A->next (B)       ; ft_lstdelone(A, del)
          *lst = B
                     ✗ A          [B| ● ]──► [C|NULL]

 paso 2:  sig = B->next (C)       ; ft_lstdelone(B, del)
          *lst = C
                                  ✗ B        [C|NULL]

 paso 3:  sig = C->next (NULL)    ; ft_lstdelone(C, del)
          *lst = NULL             → fin: la variable de main vale NULL
```

Recibe `t_list **` precisamente para poder dejar la variable de quien llama a `NULL` (si recibiera `t_list *`, solo cambiaría su copia; ver [[Punteros en C]]).

## Prototipo

```c
void ft_lstclear(t_list **lst, void (*del)(void *));
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Elimina y libera el nodo ‘lst’ dado y todos los consecutivos del mismo, utilizando la función ‘del’ y free(3).
> Al final, el puntero a la lista debe ser NULL.

| | |
|---|---|
| **Parámetros** | `lst`: la dirección de un puntero a un nodo.<br>`del`: un puntero a la función utilizado para eliminar el contenido de un nodo. |
| **Valor devuelto** | Nada |
| **Funciones autorizadas** | free |

## Funciones externas (man)

> [!quote] man 3 free — DESCRIPTION
> The free() function frees the memory space pointed to by ptr, which must have been returned by a previous call to malloc(), calloc(), or realloc().  Otherwise, or if free(ptr) has already been called before, undefined behavior occurs.  If ptr is NULL, no operation is performed.

> [!note] Traducción
> La función free() libera el espacio de memoria apuntado por ptr, que debe haber sido devuelto por una llamada previa a malloc(), calloc() o realloc(). Si no, o si ya se llamó antes a free(ptr), el comportamiento es indefinido. Si ptr es NULL, no se hace nada.

## Cómo implementarla

```text
1. Si lst o del son NULL → sal.
2. Mientras *lst no sea NULL:
       sig = (*lst)->next          ← guárdalo ANTES de liberar
       ft_lstdelone(*lst, del)
       *lst = sig
3. (Al salir del bucle *lst ya vale NULL.)
```

## Puntos clave y casos límite

- Guarda `next` **antes** de liberar el nodo actual.
- Termina con `*lst = NULL;`.

> [!danger] Errores que provocan crash o leak
> - **Leer `next` después de liberar**: `ft_lstdelone(*lst, del); *lst = (*lst)->next;` es *use after free*. A veces «funciona» por casualidad; Valgrind lo marca como *Invalid read of size 8* ([[Valgrind y sanitizers]]).
> - **No dejar `*lst` a NULL**: quien llama conserva un puntero colgante (*dangling pointer*) y, si vuelve a liberar la lista, hay *double free*.
> - **Liberar solo los nodos y no el contenido** (o al revés): leak de lo que te saltas. Reutilizar [[ft_lstdelone]] evita olvidos.
> - **`*lst` ya NULL** (lista vacía): no es un error; el bucle no entra y la función termina.

## Relacionadas

[[ft_lstdelone]] · [[ft_lstmap]] · [[Listas enlazadas]] · [[Control de errores en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 free` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [free(3) en man7.org](https://man7.org/linux/man-pages/man3/free.3.html).
