---
tags: [c, structs, typedef, norma, libft]
aliases: ["Struct", "Estructuras en C", "typedef"]
---
# Structs y typedef

← Inicio · C

> Un **struct** agrupa varias variables relacionadas (de tipos distintos) bajo un mismo nombre: un punto con `x` e `y`, un jugador con nombre y vidas, un nodo de lista con contenido y siguiente. Un **`typedef`** le da un nombre corto a un tipo. En 42 los usarás desde la Parte 3 de libft (`t_list`) y en proyectos como push_swap.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Struct** (estructura) | Tipo compuesto formado por varios **campos** (*members*) |
| **Campo** | Cada variable de dentro del struct: `x`, `y`, `content`, `next` |
| **Etiqueta** (*tag*) | El nombre que va tras `struct`: en `struct s_point`, la etiqueta es `s_point` |
| **`typedef`** | Crea un **alias** para un tipo existente. No crea un tipo nuevo |
| **`.`** | Accede a un campo desde **la variable struct** |
| **`->`** | Accede a un campo desde **un puntero** al struct |
| **Padding** (relleno) | Bytes vacíos que el compilador mete entre campos para alinearlos |

## Declarar un struct

```c
struct s_point
{
	int	x;
	int	y;
};

struct s_point	a;     // hay que escribir "struct s_point" cada vez
```

Sin `typedef`, el tipo se llama `struct s_point` (dos palabras). Es largo, y por eso casi siempre se combina con un `typedef`:

```c
typedef struct s_point
{
	int	x;
	int	y;
}	t_point;

t_point	a;              // equivalente a: struct s_point a;
```

`typedef X Y;` significa «a partir de ahora, `Y` es otro nombre para `X`». Aquí `X` es todo el bloque `struct s_point { … }` e `Y` es `t_point`.

## La convención `s_` y `t_` de la Norma

La [[La Norma|Norma]] fija los nombres:

> [!quote] La Norma (versión 4), «Denominación»
> • El nombre de una estructura debe comenzar con s_.
> • El nombre de un typedef debe comenzar con t_.

Y en el apartado «Typedef, struct, enum y union»:

> [!quote] La Norma (versión 4)
> • Agrega una tabulación al declarar un struct, enum o union.
> • El nombre del typedef debe ir precedido por una tabulación.
> • Debes indentar todos los nombres de las estructuras en la misma columna dentro de su scope.
> • No puedes declarar una estructura en un archivo .c.

Consecuencias prácticas:

- Los structs se declaran en el **`.h`** (`libft.h`, `push_swap.h`…), no en los `.c`. Ver Preprocesador y headers.
- Entre `}` y `t_nombre` va **un tabulador**, y los nombres de los campos se alinean en la misma columna con tabuladores.
- Los ejemplos de esta nota declaran el struct en el `.c` para que quepan en un solo fichero; **norminette lo marcaría**.

## `.` frente a `->`

```c
#include <stdio.h>

typedef struct s_point
{
	int	x;
	int	y;
}	t_point;

static void	move_copy(t_point p)
{
	p.x = 100;
}

static void	move_ptr(t_point *p)
{
	p->x = 100;
}

int	main(void)
{
	t_point	a;
	t_point	*pa;

	a.x = 1;
	a.y = 2;
	pa = &a;
	printf("a.x = %d, pa->y = %d, (*pa).y = %d\n", a.x, pa->y, (*pa).y);
	move_copy(a);
	printf("tras move_copy: a.x = %d\n", a.x);
	move_ptr(&a);
	printf("tras move_ptr:  a.x = %d\n", a.x);
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror st1.c -o st1 && ./st1
a.x = 1, pa->y = 2, (*pa).y = 2
tras move_copy: a.x = 1
tras move_ptr:  a.x = 100
```

| Tienes… | Escribes | Equivale a |
|---|---|---|
| Una variable `t_point a` | `a.x` | — |
| Un puntero `t_point *pa` | `pa->x` | `(*pa).x` |

`->` es solo un atajo de `(*pa).x`. Los paréntesis hacen falta porque `.` tiene más prioridad que `*`: `*pa.x` se leería como `*(pa.x)`.

Y lo más importante de la salida: **un struct se pasa por valor**. `move_copy` recibe una copia entera y cambiarla no afecta a `a`. Para modificar el original hay que pasar un puntero, como con cualquier otra variable (ver [[Punteros en C]]).

> [!tip] Si te equivocas, clang te lo dice
> ```text
> err4.c:13:4: error: member reference type 't_point *' (aka 'struct s_point *') is a pointer; did you mean to use '->'?
>         pa.x = 1;
> err4.c:14:3: error: member reference type 't_point' (aka 'struct s_point') is not a pointer; did you mean to use '.'?
>         a->y = 2;
> ```

## Structs en memoria: tamaño y padding

Los campos se guardan **en el orden en que los declaras**, pero el compilador puede añadir huecos para que cada campo empiece en una dirección múltiplo de su tamaño (alineación). Así el procesador lo lee más rápido.

```c
#include <stdio.h>
#include <stddef.h>

typedef struct s_mix
{
	char	c;
	int		n;
	char	d;
}	t_mix;

typedef struct s_mix2
{
	int		n;
	char	c;
	char	d;
}	t_mix2;

typedef struct s_list
{
	void			*content;
	struct s_list	*next;
}	t_list;

int	main(void)
{
	printf("sizeof(t_mix)  = %zu\n", sizeof(t_mix));
	printf("  offsetof c=%zu n=%zu d=%zu\n", offsetof(t_mix, c),
		offsetof(t_mix, n), offsetof(t_mix, d));
	printf("sizeof(t_mix2) = %zu\n", sizeof(t_mix2));
	printf("sizeof(t_list) = %zu\n", sizeof(t_list));
	return (0);
}
```

```text
sizeof(t_mix)  = 12
  offsetof c=0 n=4 d=8
sizeof(t_mix2) = 8
sizeof(t_list) = 16
```

```text
t_mix (12 bytes):
 0    1    2    3    4    5    6    7    8    9    10   11
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ c  │ pad│ pad│ pad│         n         │ d  │ pad│ pad│ pad│
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘

t_mix2 (8 bytes):
┌────┬────┬────┬────┬────┬────┬────┬────┐
│         n         │ c  │ d  │ pad│ pad│
└────┴────┴────┴────┴────┴────┴────┴────┘
```

Mismos campos, distinto orden, 4 bytes de diferencia. Conclusiones:

- **Nunca calcules a mano** el tamaño de un struct: usa siempre `sizeof(t_mix)` en `malloc`.
- `offsetof` (de `<stddef.h>`) da la posición de un campo dentro del struct.
- Los valores concretos dependen de la máquina; estos son de Linux x86_64.

## El struct de la libft: `t_list`

El subject de libft (Parte 3) te obliga a añadir esto a `libft.h`:

```c
typedef struct s_list
{
	void			*content;
	struct s_list	*next;
}	t_list;
```

Dos detalles que se preguntan en evaluación:

1. **`content` es `void *`** para que la lista pueda guardar cualquier cosa: cadenas, `int *`, otros structs… Al usarlo hay que convertirlo: `(char *)node->content`.
2. **Dentro se escribe `struct s_list *next`, no `t_list *next`**. El alias `t_list` aún no existe mientras se está leyendo el bloque: el `typedef` termina en el `;` final. Por eso el struct necesita etiqueta (`s_list`) y no puede ser anónimo.

> [!info] Un struct que se apunta a sí mismo
> Un struct no puede contener **otro struct de su mismo tipo** (sería infinito), pero sí **un puntero** a uno: un puntero ocupa siempre 8 bytes. Esa es la base de las [[Listas enlazadas]].

## Reservar structs con `malloc`

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct s_player
{
	char	*name;
	int		hp;
}	t_player;

static t_player	*player_new(char *name, int hp)
{
	t_player	*p;

	p = malloc(sizeof(t_player));
	if (!p)
		return (NULL);
	p->name = name;
	p->hp = hp;
	return (p);
}

int	main(void)
{
	t_player	*pl;
	t_player	copy;

	pl = player_new("felix", 3);
	if (!pl)
		return (1);
	copy = *pl;
	copy.hp = 0;
	printf("%s: hp original %d, hp copia %d\n", pl->name, pl->hp, copy.hp);
	free(pl);
	return (0);
}
```

```text
felix: hp original 3, hp copia 0
```

- Es el mismo patrón que [[ft_lstnew]]: `malloc(sizeof(t_list))`, comprobar `NULL`, rellenar campos con `->`, devolver el puntero.
- `copy = *pl;` copia el struct **campo a campo**. Pero ojo: si un campo es un puntero (`name`), se copia **la dirección**, no la cadena. Las dos copias comparten la misma cadena (copia superficial).
- Los structs **sí** se pueden asignar con `=`, al contrario que los arrays. Lo que **no** se puede es compararlos con `==`.

## Dónde verás structs en 42

| Proyecto | Uso típico |
|---|---|
| libft (Parte 3) | `t_list` |
| ft_printf | Un struct con los flags de cada conversión (en el bonus) |
| get_next_line | Bonus: guardar el resto de lectura de varios fd |
| push_swap | Pilas como listas de nodos con valor, índice… |

## Errores frecuentes

| Error | Síntoma |
|---|---|
| `malloc(sizeof(t_list *))` en vez de `malloc(sizeof(t_list))` | Reservas 8 bytes (lo que ocupa un puntero) en vez de 16. Al escribir `next` te sales del bloque. Valgrind: `Invalid write of size 8 … 0 bytes after a block of size 8 alloc'd` |
| `.` con un puntero o `->` con una variable | Error de compilación (ver arriba) |
| Declarar el struct en un `.c` | Error de norminette |
| Pasar un struct grande por valor | Copias muchos bytes en cada llamada y los cambios se pierden |
| Olvidar la etiqueta `s_list` y escribir `t_list *next` dentro | `unknown type name 't_list'` |

> [!warning] Truco para `sizeof` en `malloc`
> Escribe `ptr = malloc(sizeof(*ptr));`. Así el tamaño siempre corresponde al tipo apuntado, aunque cambies el tipo de `ptr` más tarde.

> [!question] Pregunta típica de evaluación
> «¿Por qué dentro de `t_list` pones `struct s_list *next` y no `t_list *next`?»
> Porque el alias `t_list` solo existe cuando termina la declaración del `typedef`. Dentro de las llaves el compilador aún no lo conoce; la etiqueta `s_list`, en cambio, ya está declarada desde que se escribe `struct s_list`.

## Relacionadas

[[Punteros en C]] · [[Listas enlazadas]] · [[ft_lstnew]] · Preprocesador y headers · [[La Norma]] · [[Segmentos de memoria en C]] · [[Tipos enteros y conversiones]]

## Referencias

- [Struct declaration — cppreference](https://en.cppreference.com/w/c/language/struct) — sintaxis, etiquetas, structs incompletos y autorreferencia.
- [Typedef declaration — cppreference](https://en.cppreference.com/w/c/language/typedef) — `typedef` crea un alias, no un tipo nuevo.
- [Member access operators — cppreference](https://en.cppreference.com/w/c/language/operator_member_access) — `.` y `->`.
- [Beej's Guide to C: Structs](https://beej.us/guide/bgc/html/split/structs.html) y [Structs II: More Fun with Structs](https://beej.us/guide/bgc/html/split/structs-ii-more-fun-with-structs.html) — padding, `offsetof`, copia de structs.
- [N1570 (borrador C11)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) — §6.7.2.1 (los campos se colocan en orden y puede haber relleno, nunca al principio), §6.7.8 (`typedef`).
- La Norma v4 (`Normativa 42/es.norm-2.pdf`) — prefijos `s_`/`t_` y reglas de declaración de structs (citas literales).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — definición de `t_list`.
- Tamaños medidos con `cc` (Ubuntu clang 12.0.1) en Linux x86_64.
