---
tags: [libft, libft/parte3]
funcion: ft_lstadd_front
original: ninguna
externas: "Ninguna"
estado: pendiente
---
# ft_lstadd_front

[[libft - Índice|← Índice]] · Parte 3 · Listas enlazadas

> Pone el nodo `new` delante de todos, de modo que pasa a ser la nueva cabeza de la lista. Recibe la **dirección** del puntero a la cabeza para poder cambiarlo.

## Explicación sencilla

Antes:

```text
 lista ──► [ "B" | ● ]──► [ "C" | NULL ]

 new   ──► [ "A" | NULL ]
```

Después de `ft_lstadd_front(&lista, new);`:

```text
 lista ──► [ "A" | ● ]──► [ "B" | ● ]──► [ "C" | NULL ]
              ▲
             new
```

¿Por qué `t_list **lst` y no `t_list *lst`? Porque hay que cambiar la variable `lista` del que llama. En C los argumentos se pasan **por copia**: si recibieras `t_list *`, cambiarías solo tu copia (ver [[Punteros en C]]).

```text
 en main:           lista  (variable, guarda la dirección del 1er nodo)
                      ▲
 en la función:     lst = &lista       →  *lst es «la variable lista de main»
                                          *lst = new  la cambia de verdad
```

## Prototipo

```c
void ft_lstadd_front(t_list **lst, t_list *new);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> No usa funciones externas, así que no hay citas de `man`.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Añade el nodo ‘new’ al principio de la lista ‘lst’.

| | |
|---|---|
| **Parámetros** | `lst`: la dirección de memoria de un puntero al primer nodo de una lista.<br>`new`: un puntero al nodo que se añade al principio de la lista. |
| **Valor devuelto** | Nada |
| **Funciones autorizadas** | Ninguna |

## Cómo implementarla

```text
1. Si lst o new son NULL → sal.
2. new->next = *lst        (new apunta a la antigua cabeza; si la lista estaba vacía, a NULL)
3. *lst = new              (la cabeza pasa a ser new)
```

El orden importa: si haces el paso 3 antes que el 2, pierdes la dirección de la lista antigua.

## Puntos clave y casos límite

- `new->next = *lst; *lst = new;`
- Recibe `t_list **` porque cambia la cabeza de la lista.

> [!warning] Errores típicos
> - **Invertir los dos pasos**: `*lst = new; new->next = *lst;` hace que `new` apunte a sí mismo → bucle infinito en cualquier recorrido.
> - **No proteger `lst == NULL` o `new == NULL`**: desreferenciar NULL → *segfault* ([[Carácter nulo y puntero NULL]]).
> - **Lista vacía** (`*lst == NULL`): no es un caso especial; el código de arriba ya funciona y deja `new->next = NULL`.
> - **Llamarla con `lista` en vez de `&lista`**: el compilador avisa de tipo incompatible (`t_list *` frente a `t_list **`).

## Relacionadas

[[ft_lstnew]] · [[ft_lstadd_back]] · [[Listas enlazadas]] · [[Punteros en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
