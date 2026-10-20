---
tags: [libft, libft/parte3]
funcion: ft_lstlast
original: ninguna
externas: "Ninguna"
estado: pendiente
---
# ft_lstlast

[[libft - Índice|← Índice]] · Parte 3 · Listas enlazadas

> Devuelve un puntero al último nodo de la lista: el único cuyo `next` es `NULL`. Si la lista está vacía, devuelve `NULL`.

## Explicación sencilla

```text
 lst ──► [ "a" | ● ]──► [ "b" | ● ]──► [ "c" | NULL ]
                                          ▲
                              ft_lstlast(lst) devuelve este nodo
```

Ojo: devuelve el **nodo**, no su contenido. Para el contenido: `ft_lstlast(lst)->content` (solo si la lista no está vacía).

## Prototipo

```c
t_list *ft_lstlast(t_list *lst);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> No usa funciones externas, así que no hay citas de `man`.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Devuelve el último nodo de la lista.

| | |
|---|---|
| **Parámetros** | `lst`: el principio de la lista. |
| **Valor devuelto** | Último nodo de la lista. |
| **Funciones autorizadas** | Ninguna |

## Cómo implementarla

```text
1. Si lst es NULL → devuelve NULL.
2. Mientras lst->next no sea NULL:
       lst = lst->next
3. Devuelve lst.
```

Compárala con [[ft_lstsize]]: allí la condición es `lst != NULL` (contar todos); aquí es `lst->next != NULL` (pararse **en** el último).

## Puntos clave y casos límite

- Lista vacía → NULL.
- Avanza mientras `lst->next != NULL`.

> [!warning] Errores típicos
> - **No comprobar `lst == NULL` antes**: el bucle evalúa `NULL->next` → *segfault* ([[Carácter nulo y puntero NULL]]).
> - **Usar `while (lst)`**: sales del bucle con `lst == NULL` y devuelves NULL siempre.
> - **Usar el resultado sin comprobarlo**: `ft_lstlast(lista)->next = x;` explota si `lista` está vacía. Por eso [[ft_lstadd_back]] trata ese caso aparte.

## Relacionadas

[[ft_lstadd_back]] · [[ft_lstsize]] · [[Listas enlazadas]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
