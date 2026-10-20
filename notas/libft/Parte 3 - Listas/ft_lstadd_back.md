---
tags: [libft, libft/parte3]
funcion: ft_lstadd_back
original: ninguna
externas: "Ninguna"
estado: pendiente
---
# ft_lstadd_back

[[libft - Índice|← Índice]] · Parte 3 · Listas enlazadas

> Engancha el nodo `new` al final de la lista. Si la lista está vacía, `new` pasa a ser la cabeza; por eso recibe `t_list **`.

## Explicación sencilla

Lista con nodos:

```text
 antes:    lista ──► [ 1 | ● ]──► [ 2 | NULL ]        new ──► [ 3 | NULL ]

 después:  lista ──► [ 1 | ● ]──► [ 2 | ● ]──► [ 3 | NULL ]
                                    ▲
                     ft_lstlast(lista)->next = new
```

Lista vacía (el caso que obliga a usar `**`):

```text
 antes:    lista = NULL                          new ──► [ 3 | NULL ]
 después:  lista ──► [ 3 | NULL ]                (*lst = new cambia la variable de main)
```

## Prototipo

```c
void ft_lstadd_back(t_list **lst, t_list *new);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> No usa funciones externas, así que no hay citas de `man`.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Añade el nodo ‘new’ al final de la lista ‘lst’.

| | |
|---|---|
| **Parámetros** | `lst`: el puntero al primer nodo de una lista.<br>`new`: el puntero a un nodo que se añade a la lista. |
| **Valor devuelto** | Nada |
| **Funciones autorizadas** | Ninguna |

> [!note] Matiz del parámetro
> El subject describe `lst` como «el puntero al primer nodo», pero el tipo es `t_list **`: en realidad es la **dirección** de ese puntero, igual que en [[ft_lstadd_front]].

## Cómo implementarla

```text
1. Si lst o new son NULL → sal.
2. Si *lst es NULL (lista vacía):
       *lst = new
       sal.
3. Si no:
       ultimo = ft_lstlast(*lst)
       ultimo->next = new
```

## Puntos clave y casos límite

- Si `*lst == NULL`, `new` pasa a ser la cabeza.
- Si no, `ft_lstlast(*lst)->next = new;`.

> [!warning] Errores típicos
> - **Recorrer con `*lst` directamente** (`while ((*lst)->next) *lst = (*lst)->next;`): mueves la cabeza de la lista del que llama y pierdes todos los nodos anteriores → leak. Usa una variable local o [[ft_lstlast]].
> - **Olvidar el caso lista vacía**: `ft_lstlast(NULL)` devuelve NULL y `NULL->next = new` → *segfault*.
> - **Añadir el mismo nodo dos veces**: crea un ciclo (el último apunta a uno anterior) y cualquier recorrido se vuelve infinito.

## Relacionadas

[[ft_lstlast]] · [[ft_lstadd_front]] · [[ft_lstnew]] · [[Listas enlazadas]] · [[Punteros en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
