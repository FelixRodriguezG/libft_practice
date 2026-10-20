---
tags: [libft, libft/parte3]
funcion: ft_lstsize
original: ninguna
externas: "Ninguna"
estado: pendiente
---
# ft_lstsize

[[libft - Índice|← Índice]] · Parte 3 · Listas enlazadas

> Cuenta cuántos nodos tiene una lista, siguiendo los punteros `next` desde el primero hasta llegar a `NULL`.

## Explicación sencilla

```text
 lst ──► [ 1 | ● ]──► [ 2 | ● ]──► [ 3 | NULL ]
          cuenta=1     cuenta=2     cuenta=3     lst = NULL → para

 ft_lstsize(lst) = 3
 ft_lstsize(NULL) = 0
```

Una lista no guarda su tamaño en ningún sitio: no es un array (ver [[Listas enlazadas]]). La única forma de saberlo es recorrerla entera.

## Prototipo

```c
unsigned int ft_lstsize(t_list *lst);
```

> [!note] Tipo de retorno
> El subject v19.3 da `unsigned int` como tipo de retorno. Versiones anteriores del subject usaban `int`; copia el prototipo de **tu** PDF.

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> No usa funciones externas, así que no hay citas de `man`.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Cuenta el número de nodos de una lista.

| | |
|---|---|
| **Parámetros** | `lst`: el principio de la lista. |
| **Valor devuelto** | La longitud de la lista. |
| **Funciones autorizadas** | Ninguna |

## Cómo implementarla

```text
1. cuenta = 0
2. Mientras lst no sea NULL:
       cuenta = cuenta + 1
       lst = lst->next
3. Devuelve cuenta.
```

Modificar `lst` dentro de la función no afecta al que llama: es una copia del puntero.

## Puntos clave y casos límite

- Lista vacía (`NULL`) → 0.

> [!warning] Errores típicos
> - **Condición `while (lst->next)`**: se salta el último nodo (devuelve uno menos) y con lista vacía hace `NULL->next` → *segfault*.
> - **Nodos con `next` sin inicializar**: si tu [[ft_lstnew]] no pone `next = NULL`, el recorrido sigue basura. El fallo no está aquí, pero aparece aquí.

## Relacionadas

[[ft_lstlast]] · [[ft_lstiter]] · [[Listas enlazadas]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — prototipo, descripción, parámetros y valor devuelto, copiados literalmente.
