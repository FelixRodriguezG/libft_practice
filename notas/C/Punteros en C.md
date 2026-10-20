---
tags: [c, punteros, memoria, libft]
aliases: ["Punteros", "Puntero", "Pointers"]
---
# Punteros en C

← Inicio · C

> Un **puntero** es una variable que guarda una **dirección de memoria**: el «número de casilla» donde vive otro dato. Sirven para que una función pueda modificar variables ajenas, para recorrer cadenas y arrays, para usar memoria de `malloc` y para pasar funciones como parámetro. Casi toda la libft está hecha de punteros.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Dirección** | Número que identifica un byte de la memoria. Se suele escribir en hexadecimal: `0x7fff356143c8` |
| **Puntero** | Variable cuyo valor es una dirección. `int *p` = «p guarda la dirección de un `int`» |
| **`&` (dirección de)** | Operador que da la dirección de una variable: `&x` |
| **`*` (desreferenciar)** | Operador que va a la dirección y lee o escribe lo que hay allí: `*p` |
| **Tipo apuntado** | El tipo del dato al que apunta: en `char *s` es `char`. Decide cuántos bytes se leen con `*s` y cuánto avanza `s + 1` |
| **`NULL`** | Valor de puntero que no apunta a nada. Ver [[Carácter nulo y puntero NULL]] |

## Dirección, `&` y `*`

Piensa en la memoria como una fila enorme de casillas de 1 byte, cada una con su número (su dirección). Una variable `int` ocupa 4 casillas seguidas; su dirección es la de la primera.

```c
#include <stdio.h>

int	main(void)
{
	int	x;
	int	*p;

	x = 42;
	p = &x;
	printf("x vale %d\n", x);
	printf("&x es  %p\n", (void *)&x);
	printf("p vale %p\n", (void *)p);
	printf("*p vale %d\n", *p);
	*p = 21;
	printf("ahora x vale %d\n", x);
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror ptr1.c -o ptr1 && ./ptr1
x vale 42
&x es  0x7fff356143c8
p vale 0x7fff356143c8
*p vale 42
ahora x vale 21
```

```text
      x  (int, 4 bytes)              p  (int *, 8 bytes)
    ┌──────────────┐               ┌──────────────────┐
    │      42      │ ◄──────────── │  0x7fff356143c8  │
    └──────────────┘               └──────────────────┘
    0x7fff356143c8
```

- `p = &x;` guarda en `p` la dirección de `x`.
- `*p` significa «lo que hay en la dirección que guarda `p`». Por eso `*p = 21` cambia `x`.
- Las direcciones cambian en cada ejecución (el sistema las aleatoriza), así que las tuyas serán otras.

> [!note] El `*` tiene dos papeles
> En una **declaración** (`int *p;`) el `*` dice «p es un puntero». En una **expresión** (`*p = 21;`) el `*` significa «ve a la dirección». Es el mismo símbolo con dos usos distintos.

> [!tip] `%p` y el cast a `void *`
> `printf` con `%p` espera un `void *`. El cast `(void *)p` es lo correcto según el estándar; sin él, algunos compiladores avisan con `-Wformat-pedantic`. Más en printf.

### ¿Para qué sirve? Modificar variables de quien te llama

En C los argumentos se pasan **por valor**: la función recibe una **copia**. Si quieres que una función cambie una variable tuya, le pasas su dirección. Es lo que hace `ft_lstadd_front(t_list **lst, …)`: recibe la dirección de tu puntero a la lista para poder cambiarlo.

## Aritmética de punteros

Sumar 1 a un puntero **no** suma 1 byte: avanza **un elemento** del tipo apuntado. Un `int *` salta 4 bytes; un `char *`, 1.

```c
#include <stdio.h>

int	main(void)
{
	int		nums[3] = {10, 20, 30};
	int		*p;
	char	*c;

	p = nums;
	c = (char *)nums;
	printf("p     = %p  *p     = %d\n", (void *)p, *p);
	printf("p + 1 = %p  *(p+1) = %d\n", (void *)(p + 1), *(p + 1));
	printf("c + 1 = %p\n", (void *)(c + 1));
	printf("p[2] = %d, *(p + 2) = %d\n", p[2], *(p + 2));
	printf("distancia (p + 2) - p = %ld\n", (long)((p + 2) - p));
	return (0);
}
```

```text
p     = 0x7fff09489240  *p     = 10
p + 1 = 0x7fff09489244  *(p+1) = 20
c + 1 = 0x7fff09489241
p[2] = 30, *(p + 2) = 30
distancia (p + 2) - p = 2
```

Tres reglas que salen de aquí:

1. `p[i]` es exactamente `*(p + i)`. Los corchetes son aritmética de punteros disfrazada (ver [[Arrays en C]]).
2. Restar dos punteros del mismo array da el **número de elementos** entre ellos, no de bytes. Es un truco habitual en [[ft_strrchr]] o al calcular longitudes.
3. Por eso [[ft_memcpy]] y [[ft_memset]] convierten su `void *` a `unsigned char *`: quieren avanzar **de byte en byte**.

> [!warning] Solo dentro del array
> Solo puedes moverte dentro del array (y una posición más allá del final, sin desreferenciarla). Salirte es comportamiento indefinido: a veces funciona, a veces crashea, y valgrind lo marca como `Invalid read`. Ver [[Valgrind y sanitizers]].

## Puntero a puntero

Un puntero también es una variable con su propia dirección, así que puede haber un puntero que apunte a otro puntero. Aparece en dos sitios de la libft:

- **Arrays de cadenas**: [[ft_split]] devuelve un `char **`, un array de `char *` terminado en `NULL`.
- **Modificar un puntero ajeno**: [[ft_lstadd_front]], [[ft_lstadd_back]] y [[ft_lstclear]] reciben `t_list **lst`.

```c
#include <stdio.h>

static void	set_null_mal(char *s)
{
	s = NULL;
}

static void	set_null_bien(char **s)
{
	*s = NULL;
}

int	main(void)
{
	char	*str;

	str = "hola";
	set_null_mal(str);
	printf("tras set_null_mal:  %s\n", str);
	set_null_bien(&str);
	printf("tras set_null_bien: %s\n", str ? str : "(NULL)");
	return (0);
}
```

```text
tras set_null_mal:  hola
tras set_null_bien: (NULL)
```

`set_null_mal` cambia **su copia** de `s`; `str` no se entera. `set_null_bien` recibe la dirección de `str` y escribe **en ella**. Es justo lo que pide el subject de [[ft_lstclear]]: «al final, el puntero a la lista debe ser `NULL`».

```text
   str (en main)              s (en set_null_bien)
  ┌─────────────┐            ┌─────────────┐
  │  ptr ───────┼──► "hola"  │ &str ───────┼──► str
  └─────────────┘            └─────────────┘
           *s = NULL  ⇒  escribe NULL dentro de str
```

## `const` y punteros

`const` promete que algo no se va a modificar. Con punteros importa **dónde** lo pongas:

| Declaración | ¿Puedo cambiar `*p`? | ¿Puedo cambiar `p`? | Dónde lo ves |
|---|---|---|---|
| `const char *p` | ❌ | ✅ | [[ft_strlen]], [[ft_strdup]], [[ft_strchr]]: «solo leo tu cadena» |
| `char *const p` | ✅ | ❌ | Poco habitual |
| `const char *const p` | ❌ | ❌ | Poco habitual |

Truco: lee de derecha a izquierda. `const char *p` = «p es un puntero a char constante».

```text
$ cc -Wall -Wextra -Werror err2.c
err2.c:6:7: error: read-only variable is not assignable
        s[0] = 'H';
        ~~~~ ^
```

> [!danger] Los literales de cadena no se pueden modificar
> `char *s = "hola"; s[0] = 'H';` **compila** sin avisos, pero `"hola"` vive en una zona de solo lectura (ver [[Segmentos de memoria en C]]). Al ejecutarlo: `Segmentation fault` (código de salida 139). Si necesitas modificarla, usa un array (`char s[] = "hola";`) o una copia con [[ft_strdup]].

## `void *`: el puntero genérico

`void *` es «una dirección de algo, no digo de qué». Se usa cuando la función no necesita saber el tipo:

- `malloc` devuelve `void *` y se asigna sin cast a cualquier puntero.
- [[ft_memset]], [[ft_memcpy]], [[ft_bzero]] trabajan con bytes de cualquier tipo.
- El `content` de `t_list` es `void *` para poder guardar cualquier cosa (ver [[Structs y typedef]]).

No se puede desreferenciar un `void *` ni hacer aritmética con él (en C estándar): antes hay que convertirlo a un tipo concreto, normalmente `unsigned char *`.

```c
void	*ft_memset(void *b, int c, size_t len)
{
	unsigned char	*ptr;
	size_t			i;

	ptr = (unsigned char *)b;
	i = 0;
	while (i < len)
		ptr[i++] = (unsigned char)c;
	return (b);
}
```

## Punteros a función

Una función también está en memoria (en el segmento *text*), así que tiene dirección. Un **puntero a función** guarda esa dirección y permite llamar a la función a través de él. Así una función de la libft puede aplicar **la función que tú le digas**.

La sintaxis asusta, pero se lee igual que un prototipo con `(*nombre)` en lugar del nombre:

| Prototipo de la libft | El parámetro es… |
|---|---|
| `void ft_striteri(char *s, void (*f)(unsigned int, char *))` | `f`: función que recibe un índice y un `char *`, y no devuelve nada |
| `char *ft_strmapi(char const *s, char (*f)(unsigned int, char))` | `f`: recibe índice y `char`, devuelve un `char` |
| `void ft_lstiter(t_list *lst, void (*f)(void *))` | `f`: recibe el `content` de cada nodo |
| `t_list *ft_lstmap(t_list *lst, void *(*f)(void *), void (*del)(void *))` | `f` devuelve un `void *` (el nuevo contenido); `del` lo libera |

```c
#include <stdio.h>

static void	to_upper_odd(unsigned int i, char *c)
{
	if (i % 2 == 1 && *c >= 'a' && *c <= 'z')
		*c = *c - 32;
}

static void	my_striteri(char *s, void (*f)(unsigned int, char *))
{
	unsigned int	i;

	if (!s || !f)
		return ;
	i = 0;
	while (s[i])
	{
		f(i, &s[i]);
		i++;
	}
}

int	main(void)
{
	char	str[] = "abcdefg";

	my_striteri(str, to_upper_odd);
	printf("%s\n", str);
	return (0);
}
```

```text
aBcDeFg
```

- Se pasa la función **sin paréntesis**: `to_upper_odd`, no `to_upper_odd()`. El nombre de una función, sin llamarla, es su dirección.
- Dentro se llama como a una función normal: `f(i, &s[i])`.
- `&s[i]` es la dirección del carácter, para que `f` pueda modificarlo. Ver [[ft_striteri]], [[ft_lstiter]] y [[ft_lstmap]].

> [!tip] Un `typedef` aclara la sintaxis
> En proyectos grandes se suele escribir `typedef void (*t_del)(void *);` y luego `void ft_lstclear(t_list **lst, t_del del);`. En la libft debes respetar el prototipo exacto del subject. Ver [[Structs y typedef]].

## Errores frecuentes

| Error | Qué pasa | Cómo detectarlo |
|---|---|---|
| Usar un puntero sin inicializar (`int *p; *p = 5;`) | Escribe en una dirección aleatoria | clang: `variable 'p' is uninitialized when used here [-Wuninitialized]` |
| Devolver la dirección de una variable local | La variable muere al salir de la función: el puntero queda «colgando» | clang: `address of stack memory associated with local variable 'buf' returned [-Wreturn-stack-address]` |
| Desreferenciar `NULL` (p. ej. no comprobar `malloc`) | `SIGSEGV` | [[Depurar con gdb]], [[Control de errores en C]] |
| Usar memoria después de `free` | Lees basura o crasheas más tarde | valgrind: `Invalid read … inside a block … free'd` |
| Modificar un literal (`"hola"`) | `SIGSEGV` | Declara `const char *` y el compilador te frenará |
| Confundir `char *` y `char **` | Cambias la copia en vez del original | Dibuja las cajas y flechas |

Los dos primeros, compilados de verdad:

```text
$ cc -Wall -Wextra -Werror err1.c
err1.c:5:10: error: address of stack memory associated with local variable 'buf' returned [-Werror,-Wreturn-stack-address]
        return (buf);
                ^~~
err1.c:12:3: error: variable 'p' is uninitialized when used here [-Werror,-Wuninitialized]
        *p = 5;
         ^
```

> [!info] Los ejemplos y la Norma
> Los `main` de esta nota inicializan arrays al declararlos (`int nums[3] = {…}`) y usan `?:`, cosas que la [[La Norma|Norma]] prohíbe. Son ejemplos ilustrativos; en tu código de proyecto, sepáralo.

> [!question] Pregunta típica de evaluación
> «¿Por qué `ft_lstclear` recibe un `t_list **` y no un `t_list *`?»
> Porque tiene que dejar **el puntero del que llama** a `NULL`. Con un `t_list *` solo tendría una copia de ese puntero; cambiarla no afecta al original y el que llama se quedaría con un puntero a memoria ya liberada.

## Relacionadas

[[Arrays en C]] · [[Carácter nulo y puntero NULL]] · [[Segmentos de memoria en C]] · [[Structs y typedef]] · [[Listas enlazadas]] · [[Tipos enteros y conversiones]] · [[ft_split]] · [[ft_striteri]] · [[ft_lstmap]] · [[Valgrind y sanitizers]]

## Referencias

- [Pointer declaration — cppreference](https://en.cppreference.com/w/c/language/pointer) — punteros a objeto, a función, `void *`, puntero nulo.
- [const type qualifier — cppreference](https://en.cppreference.com/w/c/language/const) — `const char *` frente a `char *const`.
- [Additive operators (Arithmetic operators) — cppreference](https://en.cppreference.com/w/c/language/operator_arithmetic) — aritmética de punteros y resta de punteros.
- [Beej's Guide to C: Pointers—Cower In Fear!](https://beej.us/guide/bgc/html/split/pointers.html), [Pointers II: Arithmetic](https://beej.us/guide/bgc/html/split/pointers2.html) y [Pointers III: Pointers to Pointers and More](https://beej.us/guide/bgc/html/split/pointers-iii-pointers-to-pointers-and-more.html) — explicaciones de base y punteros a función.
- [N1570 (borrador C11)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) — §6.5.2.1 (`E1[E2]` es `*((E1)+(E2))`), §6.5.6 (operadores aditivos), §6.4.5p7 (modificar un literal de cadena es comportamiento indefinido).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — prototipos de `ft_striteri`, `ft_lstiter`, `ft_lstmap` y `ft_lstclear`.
- Ejemplos compilados con `cc` (Ubuntu clang 12.0.1) en Linux x86_64.
