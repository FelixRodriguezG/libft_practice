---
tags: [42, norma, c, norminette]
aliases: ["Norma", "Norminette"]
---
# La Norma

← Inicio · 42

> La **Norma** (versión 4) es el conjunto de reglas de estilo que debe seguir todo el código C del Common Core de 42: cómo nombrar, cómo indentar, cuánto puede medir una función, qué está prohibido… La comprueba automáticamente el programa `norminette`, salvo el Makefile y algunas reglas que revisa una persona. **Un solo error de Norma es un 0** en el proyecto.

> [!info] Comprobarla
> ```bash
> norminette              # todos los .c y .h de la carpeta actual (y subcarpetas)
> norminette ft_split.c   # un archivo concreto
> ```
> Un archivo que **no compila** no se espera que pase la Norma.

> [!info] Por qué existe
> Según el propio PDF: funciones cortas y sin `for` ni ternarios obligan a escribir instrucciones **una tras otra, fáciles de seguir**; un aspecto común hace que leas el código de otros estudiantes sin esfuerzo en las evaluaciones; y el código claro es más fácil de mantener.

## Límites

| Qué | Límite |
|---|---|
| Líneas por función | **25**, sin contar las llaves de la función |
| Parámetros por función | **4** (sin parámetros → `void`) |
| Variables declaradas por función | **5** |
| Definiciones de funciones por archivo `.c` | **5** |
| Ancho de línea | **80 columnas**, comentarios incluidos. Un tab cuenta como los espacios que ocupa, no como 1 |
| Instrucciones por línea | **1** |

## Formato e indentación

- **Indentación con tabulaciones reales** (de 4 espacios de ancho), nunca con espacios. Con la configuración de Vim ya lo tienes.
- **Espacios:**
  - Nada de espacios ni tabs al final de una línea. Una línea vacía debe estar realmente vacía.
  - Nunca dos espacios seguidos.
  - Después de `,` y `;` va un espacio (salvo a final de línea).
  - Cada operador y operando separados por **un** espacio: `a + b`, `i = 0`.
  - Después de una palabra clave de C va un espacio (`if (`, `while (`, `return (`), excepto en los tipos (`int`, `char`…) y en `sizeof`.
- **Llaves:** salto de línea antes y después de cada llave de función, declaración o estructura de control. Las estructuras de control (`if`, `while`…) llevan llaves, salvo que contengan una sola línea.
- **Líneas largas:** puedes partirlas indentando la continuación; los **operadores van al principio** de la nueva línea.
- **Funciones:**
  - Separadas entre sí por **una línea vacía**. Justo encima de una función puede ir un comentario o una instrucción del preprocesador.
  - **Un tab** entre el tipo de retorno y el nombre: `int	ft_strlen(...)`.
  - Los parámetros de los prototipos deben tener nombre.
  - El valor de retorno va entre paréntesis: `return (valor);` o `return ;` en una función `void`.

## Variables

- **Declaraciones al principio** de la función, **una por línea**, con los nombres **alineados en la misma columna** (con tabs).
- **No se declara e inicializa en la misma línea**, salvo variables globales (si se permiten), `static` y constantes.
- **Una línea vacía** entre las declaraciones y el resto del código. **No se permite ninguna otra** línea vacía dentro de la función.
- El `*` de los punteros va **pegado al nombre**: `char	*str;` (ver [[Punteros en C]]).
- **Prohibidas las asignaciones múltiples**: `a = b = 0;`.

```c
int	ft_count(char const *s, char c)
{
	int		count;
	size_t	i;

	count = 0;
	i = 0;
	while (s[i])
	{
		if (s[i] == c)
			count++;
		i++;
	}
	return (count);
}
```

| ❌ Lo marca la norminette | ✅ Correcto |
|---|---|
| `int i = 0;` | `int	i;` … línea vacía … `i = 0;` |
| `char* str;` | `char	*str;` |
| `int a, b;` | una declaración por línea |
| `return 0;` | `return (0);` |

## Nombres

| Elemento | Prefijo | Ejemplo |
|---|---|---|
| `struct` | `s_` | `struct s_list` |
| `typedef` | `t_` | `t_list` |
| `union` | `u_` | `u_value` |
| `enum` | `e_` | `e_state` |
| Variable global | `g_` | `g_count` |

- Variables, funciones, archivos y directorios en **snake_case**: minúsculas, dígitos y `_`. Nada de mayúsculas.
- Solo caracteres de la tabla **ASCII estándar**.
- Todos los identificadores (funciones, macros, tipos, variables…) **en inglés** y con nombres **explícitos** o fáciles de recordar.
- **Variables globales**: el PDF prohíbe las que no estén marcadas como `const` y `static`, salvo que el subject las permita expresamente. Muchos subjects (libft incluido) las prohíben todas. Ver [[Variables static y ámbito]].

## `typedef`, `struct`, `enum` y `union`

- Un tab al declarar un `struct`, `enum` o `union`, y otro antes del nombre del `typedef`.
- Al declarar una **variable** de tipo `struct`, `enum` o `union`, un solo espacio dentro del tipo: `struct s_list	*node;`.
- Los nombres de los campos, alineados en la misma columna.
- **No se puede declarar un `struct` en un archivo `.c`**: va en el `.h`.

```c
typedef struct s_list
{
	void			*content;
	struct s_list	*next;
}	t_list;
```

Más en [[Structs y typedef]].

## Headers (`.h`)

- Solo pueden contener: **includes (del sistema o propios), declaraciones, defines, prototipos y macros**.
- Todos los `#include` **al principio** del archivo, y cada uno debe estar **justificado** tanto en los `.c` como en los `.h` (prohibido incluir algo que no se usa).
- **Nunca se incluye un `.c`**.
- **Protección contra doble inclusión**: si el archivo es `ft_foo.h`, la macro es `FT_FOO_H`.
- Lo que va dentro de `#ifndef`/`#if` se indenta con un espacio tras el `#`.

```c
#ifndef LIBFT_H
# define LIBFT_H

# include <stdlib.h>

size_t	ft_strlen(const char *s);

#endif
```

Más en Preprocesador y headers.

## Cabecera de 42

- Todo `.c` y `.h` **empieza** con la cabecera estándar de 42: login y correo de quien lo creó, fecha de creación, y login y fecha de la última actualización.
- Se inserta con `:Stdheader` o `F1` en Vim, o con `C-c C-h` en Emacs, y se actualiza sola al guardar. Ver Vim.

## Macros y preprocesador

- `#define` **solo para valores literales y constantes**. Prohibidos los que sirven para saltarse la Norma u ofuscar el código (esto lo revisa una persona).
- Puedes usar macros de las librerías estándar solo si esas librerías están permitidas en el proyecto.
- Nombres de macros **en MAYÚSCULAS**.
- **Prohibidas las macros de varias líneas**.
- Las directivas del preprocesador solo en el ámbito global (nunca dentro de una función).

## Comentarios

- **Prohibidos dentro del cuerpo de las funciones.** Fuera de ellas pueden ir en su propia línea o al final de una línea.
- En **inglés** y útiles. Un comentario no justifica una función confusa: nombres como `f1`, `a`, `b` o una función que solo existe para esquivar la Norma se consideran «mala función».

## Prohibido

- `for`, `do…while`, `switch`, `case`, `goto`.
- Operador ternario `? :`.
- **VLA** (*variable length array*, array cuyo tamaño se decide al ejecutar): `char buf[n];` con `n` variable. Ver [[Arrays en C]].
- Tipos implícitos en las declaraciones (declarar sin escribir el tipo).

## Makefile

La `norminette` no revisa el Makefile: lo revisa quien te evalúa.

- Reglas obligatorias: `$(NAME)`, `all`, `clean`, `fclean`, `re`.
- **Si hace relink, el proyecto se considera no funcional.**
- Si usas una librería propia (p. ej. libft), el Makefile debe compilarla automáticamente.
- **Todos los archivos fuente nombrados explícitamente** en el Makefile. En la práctica, por eso no se aceptan `*.c` ni `$(wildcard ...)`.
- Proyectos con varios binarios: una regla que compile todos y otra para cada uno.

Más detalle en [[Makefile y librerías estáticas]].

## Relacionadas

Vim · [[Makefile y librerías estáticas]] · Preprocesador y headers · [[Structs y typedef]] · [[Variables static y ámbito]] · [[Punteros en C]] · [[Arrays en C]] · [[Control de errores en C]] · [[libft - Índice]]

## Referencias

- La Norma, versión 4 (PDF oficial de 42, en español): es.norm-2.pdf — fuente de todas las reglas de esta nota (capítulos III.1 a III.11).
- [42School/norminette](https://github.com/42School/norminette) — código fuente de la herramienta que comprueba la Norma.
- [42Paris/42header](https://github.com/42Paris/42header) — plugin de la cabecera de 42 para Vim.
