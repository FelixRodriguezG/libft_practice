---
tags: [c, algoritmos, ordenacion, complejidad, push-swap]
aliases: ["Notación O grande", "Big O", "Algoritmos de ordenación"]
---
# Algoritmos de ordenación y complejidad

← Inicio · C

> Un **algoritmo de ordenación** coloca los elementos de una lista de menor a mayor. Hay muchos, y la diferencia entre ellos no se nota con 10 números, pero sí con 10 000. La **notación O grande** es la forma de describir **cómo crece el trabajo** de un algoritmo cuando crece el tamaño de la entrada. Es la base para entender push_swap, donde lo que te puntúan es precisamente cuántas operaciones necesitas.

## Vocabulario

| Término | Qué significa |
|---|---|
| **n** | El tamaño de la entrada: cuántos números hay que ordenar |
| **Comparación** | Mirar si `a < b`. Es lo que solemos contar para medir el coste de ordenar |
| **Complejidad** | Cuánto trabajo (tiempo) o memoria (espacio) necesita un algoritmo, en función de `n` |
| **Peor caso / caso medio** | El coste con la entrada más desfavorable / con una entrada aleatoria típica |
| **Estable** | Si dos elementos son iguales, mantienen su orden original |
| **In situ** (*in place*) | Ordena dentro del mismo array, sin otro array del mismo tamaño |

## La notación O grande, sin fórmulas

La idea: no importa si tu algoritmo hace `3n + 5` o `n` operaciones; lo que importa es **qué pasa al duplicar `n`**. Por eso se quedan solo con el término que más crece y se quitan las constantes: `3n + 5` es **O(n)**, `n²/2 + n` es **O(n²)**.

| Notación | Nombre | Al duplicar `n`, el trabajo… | Ejemplo |
|---|---|---|---|
| O(1) | Constante | no cambia | Leer `t[5]`, `sa` en push_swap |
| O(log n) | Logarítmica | suma un paso | Búsqueda binaria |
| O(n) | Lineal | se duplica | [[ft_strlen]], recorrer una lista |
| O(n log n) | «n log n» | algo más que se duplica | Merge sort, quicksort (medio) |
| O(n²) | Cuadrática | se multiplica por 4 | Burbuja, dos bucles anidados sobre `n` |

`log n` (en base 2) es «cuántas veces puedo dividir `n` entre 2 hasta llegar a 1»: log 1000 ≈ 10, log 1 000 000 ≈ 20. Crece **muy** despacio.

```text
             n = 10     n = 100     n = 1000      n = 1 000 000
log n           ~3          ~7          ~10                 ~20
n               10         100         1000           1 000 000
n log n        ~33        ~664       ~9 966         ~20 000 000
n²             100      10 000    1 000 000   1 000 000 000 000
```

Con un millón de elementos, un algoritmo O(n²) hace unas **50 000 veces** más trabajo que uno O(n log n).

> [!tip] Cómo estimarla mirando el código
> - Un bucle que recorre `n` elementos: O(n).
> - Un bucle dentro de otro, ambos sobre `n`: O(n²).
> - Un bucle que divide el problema por 2 en cada paso: O(log n).
> - Dividir en dos mitades, resolver cada una y juntar en O(n): O(n log n).

## Contar operaciones de verdad

Burbuja, cumpliendo la Norma, contando comparaciones:

```c
#include <stdio.h>

static void	imprimir(int *t, int n)
{
	int	i;

	i = 0;
	while (i < n)
		printf("%d ", t[i++]);
	printf("\n");
}

static long	burbuja(int *t, int n)
{
	int		i;
	int		j;
	int		tmp;
	long	comparaciones;

	comparaciones = 0;
	i = 0;
	while (i < n - 1)
	{
		j = 0;
		while (j < n - 1 - i)
		{
			comparaciones++;
			if (t[j] > t[j + 1])
			{
				tmp = t[j];
				t[j] = t[j + 1];
				t[j + 1] = tmp;
			}
			j++;
		}
		i++;
	}
	return (comparaciones);
}

int	main(void)
{
	int		t[6];
	long	c;

	t[0] = 5;
	t[1] = 1;
	t[2] = 4;
	t[3] = 2;
	t[4] = 8;
	t[5] = 0;
	imprimir(t, 6);
	c = burbuja(t, 6);
	imprimir(t, 6);
	printf("comparaciones: %ld\n", c);
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror burbuja.c -o burbuja && ./burbuja
5 1 4 2 8 0 
0 1 2 4 5 8 
comparaciones: 15
```

15 = 5 + 4 + 3 + 2 + 1 = n(n−1)/2 con n = 6. Eso es O(n²).

Ahora los cinco algoritmos de esta nota sobre los **mismos** números aleatorios (`srand(42)`), contando comparaciones. El programa de medida (`medir.c`) es ilustrativo y no cumple la Norma (usa `for` y ternarios):

```text
$ cc -Wall -Wextra -Werror medir.c -o medir && ./medir
n =                  10        100       1000      10000
burbuja              45       4950     499500   49995000
insercion            35       2492     250461   25112788
seleccion            45       4950     499500   49995000
merge sort           22        546       8684     120503
quicksort            19        645      10365     155256

Ya ordenado, n = 1000: insercion 999, quicksort 499500
```

Lo que enseña esta tabla:

- Al multiplicar `n` por 10, burbuja y selección multiplican su trabajo por **100**: O(n²).
- Merge sort y quicksort lo multiplican por ~14–15: O(n log n). Con 10 000 números hacen entre **300 y 400 veces menos** comparaciones que burbuja.
- La última línea: inserción con una entrada **ya ordenada** hace solo n−1 comparaciones (su mejor caso), mientras que este quicksort (que toma el último como pivote) cae en su **peor caso**, O(n²).

## Los algoritmos

### Burbuja (*bubble sort*) — O(n²)

Recorre el array comparando cada pareja de vecinos y los intercambia si están al revés. Tras cada pasada, el mayor «sube» al final.

```text
pasada 1:  [5 1] 4 2 8 0 → 1 [5 4] 2 8 0 → 1 4 [5 2] 8 0 → 1 4 2 [5 8] 0 → 1 4 2 5 [8 0]
           → 1 4 2 5 0 | 8      ← el 8 ya está en su sitio
pasada 2:  ...         → 1 2 4 0 | 5 8
```

### Inserción (*insertion sort*) — O(n²), O(n) si ya está casi ordenado

Como ordenar cartas en la mano: tomas el siguiente elemento y lo desplazas hacia la izquierda hasta su sitio.

```text
[5] 1 4 2      → [1 5] 4 2      → [1 4 5] 2      → [1 2 4 5]
     ▲ entra 1        ▲ entra 4         ▲ entra 2
```

### Selección (*selection sort*) — O(n²) siempre

Busca el mínimo de lo que queda y lo pone al principio. Siempre hace n(n−1)/2 comparaciones, esté como esté la entrada. Es la estrategia «ingenua» que muchos prueban primero en push_swap: buscar el mínimo de la pila A, rotar hasta él y pasarlo a B.

### Merge sort — O(n log n) siempre

**Divide y vencerás** (ver [[Recursión]]): parte el array por la mitad, ordena cada mitad recursivamente y luego **mezcla** las dos mitades ordenadas en una.

```text
            [5 1 4 2 8 0]
           /             \
      [5 1 4]           [2 8 0]          dividir: log n niveles
      /     \           /     \
   [5]    [1 4]      [2]    [8 0]
      \     /           \     /
      [1 4 5]           [0 2 8]          mezclar: n comparaciones por nivel
           \             /
            [0 1 2 4 5 8]
```

log n niveles × n trabajo por nivel = O(n log n). Su pega: necesita un array auxiliar de tamaño n.

### Quicksort — O(n log n) de media, O(n²) en el peor caso

Elige un **pivote**, pone a su izquierda los menores y a su derecha los mayores, y repite en cada lado. Si el pivote cae siempre en un extremo (p. ej. elegir el último con una lista ya ordenada) degenera en O(n²), como se vio en la tabla. Por eso se elige un pivote mejor: la mediana de tres, uno aleatorio… En push_swap se usa mucho la idea de partir alrededor de un pivote (la **mediana**) para mandar «los pequeños» a B.

### Radix sort — sin comparaciones

No compara elementos entre sí: los reparte según sus **dígitos**, del menos significativo al más. Con números en base 2, cada pasada mira un bit (ver [[Operadores de bits]]):

```text
números (índices): 2=010  0=000  3=011  1=001
bit 0:  los que tienen 0 → [2 0]   los que tienen 1 → [3 1]   → 2 0 3 1
bit 1:  los que tienen 0 → [0 1]   los que tienen 1 → [2 3]   → 0 1 2 3  ✅
```

Coste: O(n · k), donde `k` es el número de bits. Si primero sustituyes cada número por su **posición en el orden final** (su índice, de 0 a n−1), `k` es solo log₂ n: 7 bits para 100 números, 9 para 500.

| Algoritmo | Mejor | Medio | Peor | Memoria extra | Estable |
|---|---|---|---|---|---|
| Burbuja | O(n)* | O(n²) | O(n²) | O(1) | ✅ |
| Inserción | O(n) | O(n²) | O(n²) | O(1) | ✅ |
| Selección | O(n²) | O(n²) | O(n²) | O(1) | ❌ |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ |
| Quicksort | O(n log n) | O(n log n) | O(n²) | O(log n) | ❌ |
| Radix (LSD) | O(n·k) | O(n·k) | O(n·k) | O(n) | ✅ |

\* Con la mejora de parar si una pasada no hizo ningún intercambio (el código de arriba no la tiene).

## Conexión con push_swap

En push_swap no tienes un array, sino **dos pilas**, A y B, y solo puedes moverlas con un juego fijo de operaciones. Lo que se mide no es el tiempo, sino **cuántas operaciones** imprime tu programa.

| Operación | Efecto |
|---|---|
| `sa` / `sb` / `ss` | Intercambia los dos primeros de A / de B / de ambas |
| `pa` / `pb` | Pasa el primero de B a A / de A a B |
| `ra` / `rb` / `rr` | Rota hacia arriba: el primero pasa a ser el último |
| `rra` / `rrb` / `rrr` | Rota hacia abajo: el último pasa a ser el primero |

```text
     A        B                 A        B                 A        B
   ┌───┐                      ┌───┐    ┌───┐             ┌───┐    ┌───┐
   │ 2 │ ← cima         pb    │ 0 │    │ 2 │      ra     │ 3 │    │ 2 │
   │ 0 │               ───►   │ 3 │    └───┘     ───►    │ 1 │    └───┘
   │ 3 │                      │ 1 │                      │ 0 │
   │ 1 │                      └───┘                      └───┘
   └───┘
```

Las pilas se suelen implementar con [[Listas enlazadas]] (doblemente enlazadas facilitan `rra`) o con arrays.

El radix binario encaja muy bien con estas operaciones: para cada bit, recorre A una vez; si el bit del primero es 0 haz `pb`, si es 1 haz `ra`; al terminar, devuelve todo con `pa`. Simulándolo con dos arrays sobre índices barajados al azar (`radix.c`, ilustrativo, no cumple la Norma):

```text
$ cc -Wall -Wextra -Werror radix.c -o radix && ./radix
100 numeros: 1084 operaciones
500 numeros: 6784 operaciones
```

Es correcto y sencillo, pero no óptimo: hace n operaciones por cada bit, se necesite o no. Por eso muchos estudiantes, para bajar el número de movimientos, usan algoritmos que **calculan el coste de cada movimiento** (el «algoritmo turco», por chunks alrededor de la mediana…) y casos especiales para 3 y 5 números.

> [!warning] Comprueba el subject
> Resumen basado en versiones públicas del subject; los detalles cambian entre versiones. Lo que manda es el PDF de tu intra. En particular, los **límites de operaciones** para 100 y 500 números que dan la nota máxima vienen en la escala de evaluación de tu versión: compara los tuyos con ellos.

> [!tip] Cómo medir tu push_swap
> ```bash
> ARG=$(seq 1 100 | shuf | tr '\n' ' '); ./push_swap $ARG | wc -l
> ./push_swap $ARG | ./checker_linux $ARG
> ```
> La primera línea cuenta tus operaciones; la segunda usa el `checker` que da la intra para comprobar que la pila queda ordenada (`OK`/`KO`). Repite con muchas entradas aleatorias: importa el **peor** caso, no el mejor.

## Errores frecuentes

> [!warning] Confundir O grande con tiempo real
> O(n²) no significa «lento» con 5 números: con n pequeño, un algoritmo cuadrático sencillo puede ganar. Por eso en push_swap se tratan 3 y 5 números aparte, a mano.

> [!warning] Radix con números negativos u originales
> El radix por bits sobre los valores originales falla con negativos (el bit de signo) y necesita 32 pasadas. Normaliza primero: sustituye cada número por su índice en el orden final.

> [!warning] Medir con una sola entrada
> Quicksort, inserción y los algoritmos de push_swap dependen de la entrada. Una lista ya ordenada o al revés puede ser el peor caso.

> [!danger] Overflow al leer los números
> `atoi("2147483648")` se desborda en silencio. En push_swap hay que detectar los valores fuera de `int` y los duplicados y responder `Error` (ver [[Tipos enteros y conversiones]] y [[ft_atoi]]).

> [!question] Pregunta típica de evaluación
> **«¿Qué complejidad tiene tu algoritmo y por qué elegiste ese?»**
> Respuesta modelo para radix: «Cambio cada número por su posición en el orden final, de 0 a n−1. Así necesito log₂ n bits: 7 para 100 números. En cada bit recorro la pila A una vez (n operaciones `pb`/`ra`) y devuelvo B con `pa`, así que el total es del orden de n · log n operaciones. Es simple y siempre termina, pero da más movimientos que un algoritmo que calcula el coste de cada movimiento.» Ten preparadas las cifras reales de tus pruebas.

## Relacionadas

[[Recursión]] · [[Operadores de bits]] · [[Listas enlazadas]] · [[Arrays en C]] · [[Tipos enteros y conversiones]] · [[ft_atoi]] · push_swap · Exam Rank 02

## Referencias

- [Wikipedia: Big O notation](https://en.wikipedia.org/wiki/Big_O_notation) — definición y órdenes de crecimiento habituales.
- [Wikipedia (es): Cota superior asintótica](https://es.wikipedia.org/wiki/Cota_superior_asint%C3%B3tica) — la misma idea en español.
- [Wikipedia: Sorting algorithm](https://en.wikipedia.org/wiki/Sorting_algorithm) — tabla comparativa de complejidades y estabilidad.
- [Wikipedia: Bubble sort](https://en.wikipedia.org/wiki/Bubble_sort), [Insertion sort](https://en.wikipedia.org/wiki/Insertion_sort), [Selection sort](https://en.wikipedia.org/wiki/Selection_sort) — algoritmos O(n²).
- [Wikipedia: Merge sort](https://en.wikipedia.org/wiki/Merge_sort) y [Quicksort](https://en.wikipedia.org/wiki/Quicksort) — divide y vencerás, peor caso de quicksort.
- [Wikipedia: Radix sort](https://en.wikipedia.org/wiki/Radix_sort) — variante LSD y coste O(n·k).
- [VisuAlgo: Sorting](https://visualgo.net/en/sorting) — animaciones paso a paso de cada algoritmo.
- Cifras de comparaciones y operaciones: medidas propias (`medir.c`, `radix.c`) con Ubuntu clang 12.0.1, `srand(42)`.
