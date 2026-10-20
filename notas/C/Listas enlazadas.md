---
tags: [c, listas, estructuras-de-datos, memoria-dinamica, libft]
aliases: ["Lista enlazada", "Linked list", "t_list"]
---
# Listas enlazadas

← Inicio · C

> Una **lista enlazada** es una cadena de **nodos** reservados con `malloc`, donde cada nodo guarda un dato y la dirección del siguiente. A diferencia de un array, puede crecer y encoger sin copiar nada. Es la base de la Parte 3 de libft (`ft_lst*`) y la estructura más usada en push_swap.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Nodo** | Un struct con el dato (`content`) y un puntero al siguiente (`next`) |
| **Cabeza** (*head*) | El primer nodo. La lista **es** un puntero a la cabeza (`t_list *lst`) |
| **Último nodo** | El que tiene `next == NULL` |
| **Lista vacía** | `lst == NULL`: no hay ningún nodo |
| **Recorrer** | Ir de nodo en nodo siguiendo `next` hasta llegar a `NULL` |

## El nodo: `t_list`

Definido en el subject de libft (ver [[Structs y typedef]]):

```c
typedef struct s_list
{
	void			*content;
	struct s_list	*next;
}	t_list;
```

Una lista con tres cadenas, dibujada:

```text
 lst
┌─────┐    ┌───────────┬──────┐    ┌───────────┬──────┐    ┌───────────┬──────┐
│  ●──┼───►│ content ● │ next●┼───►│ content ● │ next●┼───►│ content ● │ NULL │
└─────┘    └─────┼─────┴──────┘    └─────┼─────┴──────┘    └─────┼─────┴──────┘
                 ▼                       ▼                       ▼
               "A\0"                   "B\0"                   "C\0"
```

Fíjate en que hay **dos niveles de memoria**: los nodos (16 bytes cada uno) y lo que apunta cada `content`. Al liberar habrá que liberar **los dos**.

### Array frente a lista

| | Array | Lista enlazada |
|---|---|---|
| Memoria | Un bloque contiguo | Nodos sueltos por el heap |
| Acceder al elemento `i` | Inmediato: `tab[i]` | Hay que recorrer `i` nodos |
| Añadir al principio | Copiar todo una posición | Cambiar dos punteros |
| Tamaño | Fijo (o `realloc` y copiar) | Crece nodo a nodo |
| Saber el tamaño | Lo guardas tú | Hay que contar ([[ft_lstsize]]) |

## Recorrer una lista

El patrón que usan casi todas las `ft_lst*`:

```c
while (lst)
{
	/* hacer algo con lst->content */
	lst = lst->next;
}
```

`lst` es una **copia local** del puntero, así que moverla no estropea la lista de quien llama. Variantes:

| Función | Qué hace al recorrer |
|---|---|
| [[ft_lstsize]] | Cuenta nodos |
| [[ft_lstlast]] | Para cuando `lst->next == NULL` y devuelve ese nodo |
| [[ft_lstiter]] | Llama a `f(lst->content)` en cada nodo |
| [[ft_lstmap]] | Crea una lista nueva con `f(content)` de cada nodo |

## Crear, añadir delante y detrás

El programa completo (con `strdup` de la libc para abreviar; en tu libft sería [[ft_strdup]]):

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct s_list
{
	void			*content;
	struct s_list	*next;
}	t_list;

t_list	*lst_new(void *content)
{
	t_list	*node;

	node = malloc(sizeof(t_list));
	if (!node)
		return (NULL);
	node->content = content;
	node->next = NULL;
	return (node);
}

void	lst_add_front(t_list **lst, t_list *new)
{
	if (!lst || !new)
		return ;
	new->next = *lst;
	*lst = new;
}

void	lst_add_back(t_list **lst, t_list *new)
{
	t_list	*cur;

	if (!lst || !new)
		return ;
	if (!*lst)
	{
		*lst = new;
		return ;
	}
	cur = *lst;
	while (cur->next)
		cur = cur->next;
	cur->next = new;
}

void	lst_clear(t_list **lst, void (*del)(void *))
{
	t_list	*tmp;

	if (!lst || !del)
		return ;
	while (*lst)
	{
		tmp = (*lst)->next;
		del((*lst)->content);
		free(*lst);
		*lst = tmp;
	}
}

void	print_list(t_list *lst)
{
	while (lst)
	{
		printf("[%s] -> ", (char *)lst->content);
		lst = lst->next;
	}
	printf("NULL\n");
}

int	main(void)
{
	t_list	*lst;

	lst = NULL;
	lst_add_back(&lst, lst_new(strdup("B")));
	lst_add_back(&lst, lst_new(strdup("C")));
	lst_add_front(&lst, lst_new(strdup("A")));
	print_list(lst);
	lst_clear(&lst, free);
	printf("tras clear: lst = %p\n", (void *)lst);
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror -g lst.c -o lst && ./lst
[A] -> [B] -> [C] -> NULL
tras clear: lst = (nil)
```

> [!info] Simplificado para el ejemplo
> El `main` no comprueba si `strdup` o `lst_new` devuelven `NULL`, y el struct está en el `.c` (la [[La Norma|Norma]] lo prohíbe). En tu libft cada función va en su fichero y el struct en `libft.h`.

### Añadir delante: `ft_lstadd_front`

Solo dos asignaciones, **en este orden**:

```text
Antes:            lst ──► [B] ──► [C] ──► NULL        new ──► [A] ──► NULL

1) new->next = *lst;
                  lst ──► [B] ──► [C] ──► NULL
                           ▲
                  new ──► [A]

2) *lst = new;
                  lst ──► [A] ──► [B] ──► [C] ──► NULL
```

Si inviertes el orden (`*lst = new;` primero), `new->next = *lst` haría que `A` apunte a sí mismo y perderías `B` y `C`: **leak** y bucle infinito al recorrer.

¿Por qué `t_list **lst`? Porque la función tiene que **cambiar el puntero `lst` de quien llama** (la cabeza pasa a ser `A`). Con un `t_list *` solo cambiaría su copia. Ver [[Punteros en C#Puntero a puntero|puntero a puntero]].

### Añadir detrás: `ft_lstadd_back`

Recorres hasta el último nodo y enganchas ahí el nuevo. El caso especial es la **lista vacía**: no hay último nodo, así que el nuevo pasa a ser la cabeza (`*lst = new`). Olvidar ese caso es el segfault más típico de [[ft_lstadd_back]].

> [!tip] Reutiliza [[ft_lstlast]]
> `ft_lstlast(*lst)->next = new;` hace el recorrido por ti, siempre que antes hayas tratado el caso `*lst == NULL`.

## Liberar sin leaks

Cada nodo tiene **dos** bloques de memoria que liberar: el `content` (con la función `del` que te pasan) y el nodo (con `free`). Eso es [[ft_lstdelone]]. [[ft_lstclear]] lo repite para toda la lista.

La clave es **guardar el siguiente antes de liberar el actual**:

```c
tmp = (*lst)->next;      // 1. apunto el siguiente
del((*lst)->content);    // 2. libero el contenido
free(*lst);              // 3. libero el nodo
*lst = tmp;              // 4. avanzo
```

```text
$ valgrind --leak-check=full ./lst
==2811975== HEAP SUMMARY:
==2811975==     in use at exit: 0 bytes in 0 blocks
==2811975==   total heap usage: 7 allocs, 7 frees, 4,150 bytes allocated
==2811975==
==2811975== All heap blocks were freed -- no leaks are possible
```

(7 `malloc`: 3 nodos, 3 `strdup` y el buffer interno de `printf`.)

> [!danger] Usar el nodo después de liberarlo
> Si escribes `free(tmp); *lst = tmp->next;`, lees `next` de memoria que ya no es tuya. A menudo «funciona», pero es comportamiento indefinido. Valgrind lo caza:
> ```text
> ==2813070== Invalid read of size 8
> ==2813070==    at 0x4012F3: lst_clear (lstbad.c:59)
> ==2813070==    by 0x40140B: main (lstbad.c:82)
> ==2813070==  Address 0x4a9e1d8 is 8 bytes inside a block of size 16 free'd
> ==2813070==    at 0x484B27F: free (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
> ==2813070==    by 0x4012EE: lst_clear (lstbad.c:58)
> ```
> «8 bytes inside a block of size 16» = el campo `next` (posición 8) de un nodo de 16 bytes ya liberado. Ver [[Valgrind y sanitizers]].

### Por qué `del` es un parámetro

La lista no sabe qué hay en `content`. Si es una cadena de `malloc`, basta `free`. Si es un struct con punteros dentro, hay que liberar también lo de dentro. Si es una cadena literal, **no** hay que liberarla. Por eso quien crea la lista decide pasando su propia función `del` (un [[Punteros en C#Punteros a función|puntero a función]]).

## `ft_lstmap`: la más delicada

[[ft_lstmap]] crea una lista **nueva**, aplicando `f` a cada `content`. La trampa está en los fallos de `malloc` a mitad:

1. `new_content = f(lst->content);`
2. `node = ft_lstnew(new_content);`
3. Si `node == NULL`: hay que liberar `new_content` con `del` (no está en ningún nodo todavía) **y** toda la lista nueva con `ft_lstclear(&new_list, del)`. Luego devolver `NULL`.
4. Si no, `ft_lstadd_back(&new_list, node);`.

Si te olvidas del paso 3, los testers que simulan fallos de `malloc` detectarán leaks.

> [!tip] `ft_lstadd_back` en un bucle es O(n²)
> Cada llamada recorre la lista entera. Para la libft da igual, pero en push_swap con miles de nodos se nota: guarda un puntero al último nodo y engancha directamente. Ver [[Algoritmos de ordenación y complejidad]].

## Listas en los proyectos

- **push_swap**: las pilas `a` y `b` suelen implementarse como listas (a veces doblemente enlazadas, con `prev`). `sa`, `pa`, `ra` y `rra` son manipulaciones de punteros de la cabeza y el último nodo.
- **get_next_line**: algunas soluciones guardan los trozos leídos en una lista.
- **Leer un fichero entero**: guardar en una lista las líneas que devuelve get_next_line cuando aún no sabes cuántas hay.

> [!warning] Comprueba el subject
> Resumen basado en versiones públicas de los subjects; los detalles cambian entre versiones. Lo que manda es el PDF de tu intra.

## Errores frecuentes

| Error | Síntoma |
|---|---|
| No tratar `*lst == NULL` en `add_back` | Segfault al hacer `NULL->next` |
| Invertir el orden en `add_front` | Nodo apuntándose a sí mismo, bucle infinito, leak |
| `free(node)` sin `del(node->content)` | Leak del contenido |
| Leer `node->next` tras `free(node)` | `Invalid read` en valgrind |
| No poner `*lst = NULL` al final de `lst_clear` | El que llama se queda con un puntero colgante |
| Mover la cabeza real (`*lst = (*lst)->next`) para recorrer sin querer borrar | Pierdes los nodos del principio: leak |

> [!question] Pregunta típica de evaluación
> «En `ft_lstclear`, ¿por qué guardas `next` en una variable temporal?»
> Porque después de `free(nodo)` esa memoria ya no es mía: leer `nodo->next` sería un *use-after-free*. Guardo el siguiente antes de liberar y luego avanzo con la copia. Al terminar, `*lst` queda a `NULL` porque el último `next` era `NULL`.

## Relacionadas

[[Structs y typedef]] · [[Punteros en C]] · [[Carácter nulo y puntero NULL]] · [[Segmentos de memoria en C]] · [[Valgrind y sanitizers]] · [[ft_lstnew]] · [[ft_lstadd_front]] · [[ft_lstsize]] · [[ft_lstlast]] · [[ft_lstadd_back]] · [[ft_lstdelone]] · [[ft_lstclear]] · [[ft_lstiter]] · [[ft_lstmap]] · [[libft - Índice]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — definición de `t_list` y descripción de las funciones de la Parte 3 («Al final, el puntero a la lista debe ser NULL»).
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list) — definición, comparación con arrays y coste de las operaciones.
- [Beej's Guide to C: Structs II](https://beej.us/guide/bgc/html/split/structs-ii-more-fun-with-structs.html) — structs autorreferenciados y listas enlazadas.
- [Beej's Guide to C: Manual Memory Allocation](https://beej.us/guide/bgc/html/split/manual-memory-allocation.html) — `malloc` y `free`.
- [malloc(3) — man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html) — usar memoria tras `free` es comportamiento indefinido.
- [Valgrind User Manual](https://valgrind.org/docs/manual/) — mensajes `Invalid read` y resumen de leaks.
- Ejemplos compilados con `cc` (Ubuntu clang 12.0.1) y comprobados con valgrind en Linux x86_64.
