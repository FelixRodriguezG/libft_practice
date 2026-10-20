---
tags: [c, recursion, pila, algoritmos, libft]
aliases: ["Recursividad", "Función recursiva", "Recursion"]
---
# Recursión

← Inicio · C

> Una función es **recursiva** cuando se llama a sí misma para resolver una versión más pequeña del mismo problema. Necesita un **caso base** que pare las llamadas. En 42 aparece en [[ft_putnbr_fd]], en el *flood fill* (recorrer un mapa o un laberinto), en ejercicios del examen y en algoritmos de ordenación.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Caso base** | La situación que se resuelve **sin** volver a llamarse. Sin él, la recursión no termina |
| **Caso recursivo** | La parte que se llama a sí misma con un problema **más pequeño** |
| **Pila de llamadas** (*call stack*) | Zona de memoria donde cada llamada en curso guarda sus variables locales y a dónde volver |
| **Marco** (*frame*) | El trozo de pila de **una** llamada concreta |
| **Stack overflow** | Se acaba la pila por demasiadas llamadas anidadas → `Segmentation fault` |

## La receta

Toda función recursiva tiene la misma forma:

```c
tipo	f(problema)
{
	if (problema es trivial)        // caso base
		return (solución directa);
	return (combinar(f(problema más pequeño)));   // caso recursivo
}
```

Para escribir una, hazte dos preguntas:

1. ¿Cuál es el caso más simple que sé resolver sin pensar? (Caso base.)
2. Si alguien me resolviera el problema **un poco más pequeño**, ¿cómo lo usaría para resolver el mío? (Caso recursivo.)

## La pila de llamadas, en vivo

Cada llamada tiene **sus propias** variables locales, guardadas en su propio marco de la pila (ver [[Segmentos de memoria en C]]). Este `factorial` imprime al entrar y al salir, con sangría según la profundidad:

```c
#include <stdio.h>

static int	factorial(int n)
{
	int	res;

	printf("%*sentra factorial(%d)\n", (4 - n) * 2, "", n);
	if (n <= 1)
		res = 1;
	else
		res = n * factorial(n - 1);
	printf("%*ssale  factorial(%d) = %d\n", (4 - n) * 2, "", n, res);
	return (res);
}

int	main(void)
{
	factorial(4);
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror rec1.c -o rec1 && ./rec1
entra factorial(4)
  entra factorial(3)
    entra factorial(2)
      entra factorial(1)
      sale  factorial(1) = 1
    sale  factorial(2) = 2
  sale  factorial(3) = 6
sale  factorial(4) = 24
```

Lo que pasa en la pila cuando se llega al caso base:

```text
          ┌───────────────────────────┐  ← cima de la pila (crece hacia abajo en memoria)
          │ factorial  n=1  res=1     │  caso base: devuelve 1
          ├───────────────────────────┤
          │ factorial  n=2  res=?     │  esperando a factorial(1)
          ├───────────────────────────┤
          │ factorial  n=3  res=?     │  esperando a factorial(2)
          ├───────────────────────────┤
          │ factorial  n=4  res=?     │  esperando a factorial(3)
          ├───────────────────────────┤
          │ main                      │
          └───────────────────────────┘
```

- **A la ida** se apilan marcos, cada uno con su `n`. Nadie ha terminado todavía.
- **A la vuelta** se desapilan en orden inverso, y cada uno completa su multiplicación con el resultado del de arriba.
- Todo lo que escribas **después** de la llamada recursiva se ejecuta a la vuelta, en orden inverso. Ese es el truco de `ft_putnbr_fd`.

> [!tip] Verlo con gdb
> Pon un breakpoint en el caso base y escribe `bt` (*backtrace*): verás un marco por cada llamada pendiente, con su valor de `n`. Ver [[Depurar con gdb]].

## `ft_putnbr_fd`: imprimir al volver

Para escribir `1234` cifra a cifra con `write`, necesitas las cifras de izquierda a derecha, pero `% 10` te las da de derecha a izquierda (4, 3, 2, 1). La recursión lo resuelve: primero imprime «todo menos la última cifra» (`n / 10`) y **luego**, a la vuelta, la última (`n % 10`).

```c
#include <unistd.h>
#include <limits.h>

void	ft_putnbr_fd(int n, int fd)
{
	long	nb;
	char	c;

	nb = n;
	if (nb < 0)
	{
		write(fd, "-", 1);
		nb = -nb;
	}
	if (nb >= 10)
		ft_putnbr_fd(nb / 10, fd);
	c = '0' + nb % 10;
	write(fd, &c, 1);
}

int	main(void)
{
	ft_putnbr_fd(1234, 1);
	write(1, "\n", 1);
	ft_putnbr_fd(INT_MIN, 1);
	write(1, "\n", 1);
	ft_putnbr_fd(0, 1);
	write(1, "\n", 1);
	return (0);
}
```

```text
1234
-2147483648
0
```

```text
ft_putnbr_fd(1234) → llama a ft_putnbr_fd(123) → llama a ft_putnbr_fd(12) → llama a ft_putnbr_fd(1)
                                                                              escribe '1'
                                                            escribe '2'  ◄────┘
                                  escribe '3'  ◄────────────┘
escribe '4'  ◄────────────────────┘
```

- **Caso base**: `nb < 10` → una sola cifra, se escribe directamente.
- El `long` evita el problema de `-INT_MIN` (ver [[Tipos enteros y conversiones#Overflow en la libft|overflow en la libft]]).
- Como `nb / 10` ya es positivo, en las llamadas internas no vuelve a entrar en el `if (nb < 0)`.

> [!note] Un detalle de tipos
> `ft_putnbr_fd(nb / 10, fd)` pasa un `long` a un parámetro `int`. Funciona porque `nb / 10` siempre cabe en un `int`, y `-Wall -Wextra` no avisa de esta conversión (`-Wconversion` sí lo haría).

## Flood fill: rellenar un mapa

*Flood fill* («inundar») es el algoritmo del bote de pintura: desde una casilla, pinta todas las casillas conectadas que no sean pared. Sirve para saber qué casillas son alcanzables desde un punto: por ejemplo, si desde la entrada de un mapa se puede llegar a la salida. Es un ejercicio clásico del examen y la misma idea (recorrer celdas vecinas marcando las visitadas) es la base para generar y comprobar laberintos en A-Maze-ing.

```c
#include <stdio.h>

#define ROWS 5
#define COLS 8

static void	flood_fill(char map[ROWS][COLS + 1], int y, int x)
{
	if (y < 0 || y >= ROWS || x < 0 || x >= COLS)
		return ;
	if (map[y][x] == '1' || map[y][x] == 'F')
		return ;
	map[y][x] = 'F';
	flood_fill(map, y - 1, x);
	flood_fill(map, y + 1, x);
	flood_fill(map, y, x - 1);
	flood_fill(map, y, x + 1);
}

int	main(void)
{
	char	map[ROWS][COLS + 1] = {
		"11111111",
		"1S001001",
		"10001E01",
		"11110001",
		"11111111"};
	int		y;

	flood_fill(map, 1, 1);
	y = 0;
	while (y < ROWS)
		printf("%s\n", map[y++]);
	return (0);
}
```

```text
11111111
1FFF1001
1FFF1E01
11110001
11111111
```

Desde la entrada `S` se ha pintado toda su zona, pero la salida `E` sigue ahí: **no se puede llegar de `S` a `E`**. Hay dos casos base: fuera del mapa, y casilla que es pared o ya está pintada. Este segundo es esencial: sin él, dos casillas vecinas se llamarían la una a la otra para siempre.

> [!warning] Trabaja sobre una copia del mapa
> El flood fill **modifica** el mapa. Si después lo necesitas intacto, haz una copia (y libérala después) antes de rellenar.

> [!warning] Comprueba el subject
> Resumen basado en versiones públicas del examen; los detalles cambian entre versiones. Lo que manda es el PDF de tu intra.

## Cuándo **no** usar recursión

Cada llamada ocupa un marco en la pila, y la pila es pequeña: 8 MiB por defecto en Linux (`ulimit -s` → `8192` KiB). Con demasiadas llamadas anidadas, se acaba:

```c
static long	sum_to(long n)
{
	if (n == 0)
		return (0);
	return (n + sum_to(n - 1));
}
```

```text
$ ./rec4                      # printf("%ld\n", sum_to(1000)); luego sum_to(10000000)
500500
bash: line 1: 2824144 Segmentation fault      (core dumped) ./rec4
```

Con gdb se ve la profundidad a la que murió:

```text
Program received signal SIGSEGV, Segmentation fault.
0x00000000004011b8 in sum_to (n=9825341) at rec4.c:7
7		return (n + sum_to(n - 1));
...
#174659 0x00000000004011c9 in sum_to (n=10000000) at rec4.c:7
#174660 0x0000000000401167 in main () at rec4.c:13
```

Unas 175 000 llamadas y la pila se agotó. Usa un bucle (`while`) cuando:

- La profundidad depende de la entrada y puede ser grande (recorrer una lista de 100 000 nodos, una cadena larga).
- La versión iterativa es igual de clara: `ft_strlen`, `ft_lstsize`, `ft_lstclear`.
- Hay **recálculo**: el Fibonacci recursivo ingenuo repite las mismas llamadas una y otra vez (coste exponencial).

Usa recursión cuando el problema **es** recursivo y la profundidad está acotada: cifras de un número (máximo ~20 niveles), mapas pequeños, árboles, *quicksort*/*mergesort* (ver [[Algoritmos de ordenación y complejidad]]).

> [!info] Recursión de cola
> Si la llamada recursiva es **lo último** que hace la función (`return (f(n - 1));` sin operar después), el compilador puede convertirla en un bucle con optimizaciones (`-O2`). Pero C no lo garantiza, y con `-O0` no lo hace: no cuentes con ello.

## Errores frecuentes

| Error | Síntoma |
|---|---|
| Sin caso base, o inalcanzable | Recursión infinita → `Segmentation fault` (stack overflow) |
| El problema no se reduce (`f(n)` llama a `f(n)`) | Igual que el anterior |
| Flood fill sin marcar las visitadas | Infinito entre dos casillas vecinas |
| Olvidar `return` del resultado recursivo | Devuelve basura; clang avisa con `-Wreturn-type` si falta en algún camino |
| Leaks: `malloc` en cada nivel sin `free` | Valgrind: un bloque perdido por llamada |
| Comprobar límites **después** de acceder (`map[y][x]` antes de `y < 0`) | Lectura fuera del array |

> [!question] Pregunta típica de evaluación
> «Tu `ft_putnbr_fd` es recursiva: ¿cuántas veces se llama como máximo y por qué no hay riesgo de *stack overflow*?»
> Una vez por cifra: con un `int` como mucho 10 cifras más el signo, unas 10–11 llamadas. Cada marco ocupa unas decenas de bytes, nada comparado con los 8 MiB de pila. El caso base es `nb < 10`.

## Relacionadas

[[Segmentos de memoria en C]] · [[ft_putnbr_fd]] · [[ft_itoa]] · [[Depurar con gdb]] · [[Tipos enteros y conversiones]] · [[Algoritmos de ordenación y complejidad]] · A-Maze-ing - Índice · Exam Rank 02 · [[Listas enlazadas]]

## Referencias

- [Recursion (computer science) — Wikipedia](https://en.wikipedia.org/wiki/Recursion_(computer_science)) — caso base, recursión frente a iteración.
- [Flood fill — Wikipedia](https://en.wikipedia.org/wiki/Flood_fill) — algoritmo recursivo de 4 vecinos y sus límites de pila.
- [Tail call — Wikipedia](https://en.wikipedia.org/wiki/Tail_call) — recursión de cola y su eliminación por el compilador.
- [Function definitions — cppreference](https://en.cppreference.com/w/c/language/functions) — cada llamada tiene sus propios objetos automáticos.
- [N1570 (borrador C11)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) — §6.5.2.2p11: «Recursive function calls shall be permitted, both directly and indirectly».
- [GDB: Backtraces](https://sourceware.org/gdb/current/onlinedocs/gdb/Backtrace.html) — `bt`, `bt N` y `bt -N`.
- `ulimit -s` en bash (Ubuntu 22.04): tamaño de pila por defecto 8192 KiB.
- Ejemplos compilados con `cc` (Ubuntu clang 12.0.1) y depurados con gdb en Linux x86_64.
