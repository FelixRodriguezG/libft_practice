---
tags: [libft, libft/parte3]
funcion: ft_lstdelone
original: ninguna
externas: "free"
estado: pendiente
---
# ft_lstdelone

[[libft - Índice|← Índice]] · Parte 3 · Listas enlazadas

> Libera **un** nodo: primero su contenido (con la función `del` que te pasan) y después el propio nodo (con `free`). No toca el nodo siguiente.

## Explicación sencilla

Un nodo tiene **dos** bloques de memoria que liberar, y tú solo sabes liberar uno:

```text
 lst ──► ┌───────────────┐       ┌───┬───┬───┬────┐
         │ content ──────┼──────►│ a │ b │ c │ \0 │   ← 1) lo libera del(content)
         ├───────────────┤       └───┴───┴───┴────┘      (tú no sabes qué es)
         │ next ─────────┼──► [ siguiente nodo ]     ← NO se toca
         └───────────────┘
            ▲
            └── 2) lo libera free(lst)  (tú lo reservaste en ft_lstnew)
```

¿Por qué `del` y no un simple `free(content)`? Porque `content` es un `void *`: puede ser una cadena, un `int` en la pila o un `struct` con más punteros dentro. Solo quien creó el contenido sabe cómo destruirlo, así que te pasa la función adecuada (un **puntero a función**, ver [[Punteros en C]]). Lo más común es pasar el propio `free`:

```c
ft_lstdelone(nodo, free);   /* free encaja con void (*del)(void *) */
```

> [!warning] Ojo con el nodo anterior
> Tras liberar el nodo, el anterior (si lo hay) sigue apuntando a él. Quien llama tiene que reenganchar la lista (`anterior->next = siguiente`) **antes** de llamar a `ft_lstdelone`, guardándose `siguiente`.

## Prototipo

```c
void ft_lstdelone(t_list *lst, void (*del)(void *));
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Recibe como parámetro un nodo ‘lst’ y libera la memoria del contenido utilizando la función ‘del’ dada como parámetro. También libera el nodo en sí mismo, pero no libera el siguiente nodo.

| | |
|---|---|
| **Parámetros** | `lst`: el nodo a liberar.<br>`del`: un puntero a la función utilizada para liberar el contenido del nodo. |
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
2. del(lst->content)     (primero el contenido: después ya no podrías leer lst->content)
3. free(lst)
```

## Puntos clave y casos límite

- `del(lst->content); free(lst);` — el siguiente nodo queda intacto.

> [!danger] Errores que provocan crash o leak
> - **Orden al revés** (`free(lst); del(lst->content);`): lees un nodo ya liberado → *use after free* (Valgrind: *Invalid read*). Ver [[Valgrind y sanitizers]].
> - **Olvidar `free(lst)`**: el contenido se libera pero el nodo de 16 bytes queda perdido → leak.
> - **Llamar a `del` siendo NULL**: saltar a la dirección 0 → *segfault*. Compruébalo antes.
> - **Hacer `free(lst->content)` en vez de `del(...)`**: si el contenido no venía de `malloc`, es comportamiento indefinido (lo dice la cita de `man 3 free`); y si era un struct con punteros dentro, dejas leaks.
> - **Liberar también `lst->next`**: el subject dice expresamente que el siguiente no se libera; para eso está [[ft_lstclear]].

> [!note] `lst = NULL` dentro de la función no sirve
> `lst` es una copia del puntero; ponerlo a NULL dentro no cambia la variable de quien llama, que seguirá apuntando a memoria liberada. Es responsabilidad de quien llama no volver a usarla.

## Relacionadas

[[ft_lstclear]] · [[ft_lstnew]] · [[Listas enlazadas]] · [[Punteros en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 free` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [free(3) en man7.org](https://man7.org/linux/man-pages/man3/free.3.html).
