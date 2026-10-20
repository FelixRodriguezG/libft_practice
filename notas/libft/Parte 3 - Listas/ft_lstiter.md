---
tags: [libft, libft/parte3]
funcion: ft_lstiter
original: ninguna
externas: "Ninguna"
estado: pendiente
---
# ft_lstiter

[[libft - Índice|← Índice]] · Parte 3 · Listas enlazadas

> Recorre la lista y llama a `f` con el **contenido** de cada nodo. No crea nodos ni devuelve nada: es el equivalente para listas de [[ft_striteri]].

## Explicación sencilla

```c
void	imprimir(void *content)
{
	ft_putendl_fd((char *)content, 1);
}

ft_lstiter(lista, imprimir);
```

```text
 lista ──► [ "uno" | ● ]──► [ "dos" | ● ]──► [ "tres" | NULL ]
               │                 │                 │
         f("uno")          f("dos")          f("tres")

$ ./a.out
uno
dos
tres
```

`f` recibe `void *` porque la lista puede guardar cualquier tipo; dentro de `f` se convierte (*cast*) al tipo real. Tipo del parámetro: `void (*f)(void *)` = «puntero a función que recibe un `void *` y no devuelve nada» ([[Punteros en C]]).

## Prototipo

```c
void ft_lstiter(t_list *lst, void (*f)(void *));
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> No usa funciones externas, así que no hay citas de `man`.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Itera la lista ‘lst’ y aplica la función ‘f’ en el contenido de cada nodo.

| | |
|---|---|
| **Parámetros** | `lst`: un puntero al primer nodo.<br>`f`: un puntero a la función que utilizará cada nodo. |
| **Valor devuelto** | Nada |
| **Funciones autorizadas** | Ninguna |

## Cómo implementarla

```text
1. Si f es NULL → sal.
2. Mientras lst no sea NULL:
       f(lst->content)
       lst = lst->next
```

## Puntos clave y casos límite

- Se pasa `lst->content`, no el nodo.

> [!warning] Errores típicos
> - **Pasar `lst` en vez de `lst->content`**: compila sin aviso (todo puntero se convierte a `void *`), pero `f` interpreta el nodo como si fuera el dato → resultados absurdos o crash.
> - **No comprobar `f`**: llamar a un puntero a función NULL → *segfault*.
> - **Lista vacía**: con `lst == NULL` no se hace nada; no es un error.
> - **`f` que libera el contenido**: `ft_lstiter` no está pensada para eso; los nodos quedarían apuntando a memoria liberada. Para liberar usa [[ft_lstclear]].

## Relacionadas

[[ft_lstmap]] · [[ft_striteri]] · [[ft_lstsize]] · [[Listas enlazadas]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
