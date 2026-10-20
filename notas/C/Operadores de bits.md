---
tags: [c, bits, operadores, push-swap, a-maze-ing]
aliases: ["Operadores bit a bit", "Bitwise", "Máscaras de bits"]
---
# Operadores de bits

← Inicio · C

> Los **operadores de bits** (`&`, `|`, `^`, `~`, `<<`, `>>`) trabajan sobre cada bit de un número por separado, en lugar de sobre el número entero. Sirven para leer o cambiar bits concretos, guardar varios «interruptores» en una sola variable y multiplicar o dividir por potencias de 2. En 42 los necesitas en el radix sort de push_swap y para codificar los muros de cada celda en A-Maze-ing.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Bit** | Un dígito binario: 0 o 1 |
| **Binario** | Base 2. `0b01000001` = 65 = `'A'` |
| **Hexadecimal** | Base 16. Cada cifra hex son 4 bits: `0x5A` = `0101 1010` |
| **Bit 0** (o bit menos significativo) | El de más a la derecha, vale 1 |
| **Bit 7** (más significativo en un byte) | El de más a la izquierda, vale 128 |
| **Máscara** | Un número con unos en las posiciones que te interesan, para «filtrar» bits |
| **Encender / apagar** un bit | Ponerlo a 1 / a 0 |

## Los seis operadores

| Operador | Nombre | Regla para cada pareja de bits | Ejemplo con `a = 0101 1010`, `b = 0000 1111` |
|---|---|---|---|
| `a & b` | AND | 1 si **los dos** son 1 | `0000 1010` |
| `a \| b` | OR | 1 si **alguno** es 1 | `0101 1111` |
| `a ^ b` | XOR | 1 si son **distintos** | `0101 0101` |
| `~a` | NOT | invierte cada bit | `1010 0101` |
| `a << 1` | desplazamiento izq. | mueve todo n posiciones a la izquierda, entra 0 por la derecha | `1011 0100` |
| `a >> 2` | desplazamiento der. | mueve todo n posiciones a la derecha | `0001 0110` |

> [!warning] No confundir con los lógicos
> `&` y `|` operan **bit a bit** y devuelven un número. `&&` y `||` son **lógicos**: devuelven 0 o 1 y cortan la evaluación en cuanto saben el resultado. `5 & 2` es 0, pero `5 && 2` es 1.

## Ver los bits de un `char`

La tabla anterior está generada con este programa, que es además un ejercicio clásico del examen (`print_bits`):

```c
#include <unistd.h>

static void	print_bits(unsigned char octet)
{
	int		i;
	char	bit;

	i = 7;
	while (i >= 0)
	{
		bit = '0' + ((octet >> i) & 1);
		write(1, &bit, 1);
		i--;
	}
	write(1, "\n", 1);
}

int	main(void)
{
	unsigned char	a;
	unsigned char	b;

	a = 0x5A;
	b = 0x0F;
	print_bits(a);
	print_bits(b);
	print_bits(a & b);
	print_bits(a | b);
	print_bits(a ^ b);
	print_bits(~a);
	print_bits(a << 1);
	print_bits(a >> 2);
	print_bits('A');
	return (0);
}
```

```text
$ cc -Wall -Wextra -Werror bit1.c -o bit1 && ./bit1
01011010
00001111
00001010
01011111
01010101
10100101
10110100
00010110
01000001
```

La clave está en `(octet >> i) & 1`:

```text
octet       = 0101 1010
octet >> 4  = 0000 0101     ← el bit 4 queda en la posición 0
      & 1   = 0000 0001     ← la máscara 1 se queda solo con esa posición
resultado   = 1             ← el bit 4 de octet era 1
```

> [!note] Promoción a `int`
> `~a` y `a << 1` con un `unsigned char` se calculan en `int` (ver [[Tipos enteros y conversiones#Promociones y conversiones automáticas|promociones]]): `~a` vale en realidad `0xFFFFFFA5`. Al pasarlo a `print_bits`, que recibe `unsigned char`, se queda con los 8 bits bajos.

## Máscaras: leer, encender, apagar, alternar

Con una máscara `m` que tiene a 1 los bits que te interesan:

| Quiero… | Código | Por qué funciona |
|---|---|---|
| Saber si un bit está a 1 | `if (x & m)` | AND deja solo ese bit; si era 0, todo queda a 0 |
| Encenderlo | `x \|= m;` | OR con 1 siempre da 1; con 0 no cambia nada |
| Apagarlo | `x &= ~m;` | `~m` tiene un 0 en ese bit y 1 en el resto |
| Alternarlo | `x ^= m;` | XOR con 1 invierte; con 0 no cambia |
| Máscara del bit `n` | `1 << n` | Un 1 desplazado `n` posiciones |

Un uso típico: guardar varios *flags* en un solo entero, por ejemplo los de una conversión de ft_printf (`-`, `0`, `#`, `+`):

```c
#include <stdio.h>

#define FLAG_MINUS 1
#define FLAG_ZERO 2
#define FLAG_HASH 4
#define FLAG_PLUS 8

int	main(void)
{
	unsigned int	flags;

	flags = 0;
	flags |= FLAG_MINUS;
	flags |= FLAG_HASH;
	printf("flags = %u\n", flags);
	printf("tiene '#'? %s\n", (flags & FLAG_HASH) ? "si" : "no");
	printf("tiene '+'? %s\n", (flags & FLAG_PLUS) ? "si" : "no");
	flags &= ~FLAG_MINUS;
	printf("tras quitar '-': %u\n", flags);
	flags ^= FLAG_ZERO;
	printf("tras alternar '0': %u\n", flags);
	printf("5 & 1 = %d (impar), 8 & 1 = %d (par)\n", 5 & 1, 8 & 1);
	printf("1 << 4 = %d, 40 >> 1 = %d\n", 1 << 4, 40 >> 1);
	printf("'a' ^ 32 = '%c', 'A' | 32 = '%c'\n", 'a' ^ 32, 'A' | 32);
	return (0);
}
```

```text
flags = 5
tiene '#'? si
tiene '+'? no
tras quitar '-': 4
tras alternar '0': 6
5 & 1 = 1 (impar), 8 & 1 = 0 (par)
1 << 4 = 16, 40 >> 1 = 20
'a' ^ 32 = 'A', 'A' | 32 = 'a'
```

Trucos que salen de aquí:

- `x & 1` dice si `x` es impar (el bit 0 vale 1 solo en los impares).
- `x << n` multiplica por 2ⁿ y `x >> n` divide por 2ⁿ (para valores sin signo o positivos).
- En ASCII, mayúscula y minúscula solo se diferencian en el bit 5 (valor 32). Por eso `'a' ^ 32` es `'A'`. Para [[ft_toupper]] y [[ft_tolower]] es más claro `c - 32` o `c + 32` tras comprobar el rango.

> [!info] Los flags del sistema son máscaras
> Cuando escribes `open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644)`, cada `O_*` es un bit distinto y el `|` los combina. El `0644` de permisos también son bits (ver [[Descriptores de fichero y read]]).

## Aplicación: muros de A-Maze-ing

En A-Maze-ing cada celda del laberinto se guarda como un número de 4 bits, **un bit por muro**: norte = 1, este = 2, sur = 4, oeste = 8. Bit a 1 = muro cerrado. Así cada celda cabe en una sola cifra hexadecimal en el fichero de salida (`F` = los cuatro muros, `0` = ninguno).

- **Leer** si un muro está cerrado: `cell & WALL_E`.
- **Abrir** un muro: `cell &= ~WALL_E;`.
- **Cerrar** un muro: `cell |= WALL_E;`.

El proyecto es en Python, pero los operadores son los mismos. En C:

```c
#include <stdio.h>

#define WALL_N 1
#define WALL_E 2
#define WALL_S 4
#define WALL_W 8

static void	print_cell(const char *name, unsigned int cell)
{
	printf("%s = %X:", name, cell);
	printf(" N %s,", (cell & WALL_N) ? "cerrado" : "abierto");
	printf(" E %s,", (cell & WALL_E) ? "cerrado" : "abierto");
	printf(" S %s,", (cell & WALL_S) ? "cerrado" : "abierto");
	printf(" W %s\n", (cell & WALL_W) ? "cerrado" : "abierto");
}

int	main(void)
{
	unsigned int	left;
	unsigned int	right;

	left = 0xF;
	right = 0xF;
	print_cell("izq", left);
	left &= ~WALL_E;
	right &= ~WALL_W;
	printf("-- abro el paso entre las dos --\n");
	print_cell("izq", left);
	print_cell("der", right);
	return (0);
}
```

```text
izq = F: N cerrado, E cerrado, S cerrado, W cerrado
-- abro el paso entre las dos --
izq = D: N cerrado, E abierto, S cerrado, W cerrado
der = 7: N cerrado, E cerrado, S cerrado, W abierto
```

Fíjate en que para abrir **un** paso se tocan **dos** celdas: el muro este de la izquierda es el mismo que el muro oeste de la derecha. Si solo apagas uno de los dos bits, el fichero hexadecimal queda incoherente.

## Aplicación: radix sort en push_swap

En push_swap una estrategia conocida es el **radix sort binario**: primero se sustituye cada número por su **índice** (su posición en el orden final: 0, 1, 2…) para que todos sean positivos y pequeños. Luego, para cada bit desde el 0:

- Si el bit del número de arriba de `a` es 0 → `pb` (a la pila `b`).
- Si es 1 → `ra` (rotarlo al fondo de `a`).
- Al terminar la pasada, `pa` hasta vaciar `b`.

Simulado con arrays (los ceros primero y luego los unos, conservando el orden relativo):

```c
#include <stdio.h>

int	main(void)
{
	int	a[6] = {5, 2, 7, 0, 3, 6};
	int	tmp[6];
	int	bit;
	int	i;
	int	j;

	bit = 0;
	while (bit < 3)
	{
		j = 0;
		i = -1;
		while (++i < 6)
			if (((a[i] >> bit) & 1) == 0)
				tmp[j++] = a[i];
		i = -1;
		while (++i < 6)
			if (((a[i] >> bit) & 1) == 1)
				tmp[j++] = a[i];
		i = -1;
		printf("tras bit %d:", bit);
		while (++i < 6)
		{
			a[i] = tmp[i];
			printf(" %d", a[i]);
		}
		printf("\n");
		bit++;
	}
	return (0);
}
```

```text
tras bit 0: 2 0 6 5 7 3
tras bit 1: 0 5 2 6 7 3
tras bit 2: 0 2 3 5 6 7
```

Con `n` números hacen falta tantas pasadas como bits tenga el índice máximo (`n - 1`): 7 pasadas para 100 números, 9 para 500. Es sencillo y siempre funciona, pero no es la estrategia con menos movimientos; ver [[Algoritmos de ordenación y complejidad]].

> [!info] Sobre el código de ejemplo
> Los `main` de esta nota usan `++i` dentro del `while`, inicializan arrays al declararlos y usan `?:`: son ejemplos compactos que la [[La Norma|Norma]] no aceptaría en un proyecto.

> [!warning] Comprueba el subject
> Resumen basado en versiones públicas de los subjects de push_swap y A-Maze-ing; los detalles cambian entre versiones. Lo que manda es el PDF de tu intra.

## Errores frecuentes

| Error | Qué pasa | Cómo evitarlo |
|---|---|---|
| `if (x & 1 == 0)` | `==` tiene **más** prioridad que `&`: se calcula `x & (1 == 0)` = `x & 0` = siempre 0 | Paréntesis: `if ((x & 1) == 0)`. Clang lo frena con `-Wparentheses` |
| Confundir `&` con `&&` | `if (a & b)` con `a = 1`, `b = 2` es falso | Usa `&&` para condiciones |
| `1 << 31` con `int` | No cabe en un `int` con signo: comportamiento indefinido | Usa `1u << 31` |
| Desplazar ≥ ancho del tipo (`x << 32` con 32 bits) | Comportamiento indefinido | Comprueba el rango del desplazamiento |
| `>>` de un negativo | Depende de la implementación (casi siempre rellena con unos) | Trabaja con `unsigned` |

Los dos primeros, de verdad:

```text
$ cc -Wall -Wextra -Werror bit5.c
bit5.c:4:11: error: & has lower precedence than ==; == will be evaluated first [-Werror,-Wparentheses]
        if (argc & 1 == 0)
                 ^~~~~~~~

$ cc -Wall -Wextra -Werror -fsanitize=undefined … && ./b6     # printf("%d\n", argc << 31);
<stdin>:6:22: runtime error: left shift of 1 by 31 places cannot be represented in type 'int'
-2147483648
```

> [!question] Pregunta típica de evaluación
> «En tu A-Maze-ing, ¿qué significa la `D` del fichero de salida?»
> `0xD` = `1101`: bits 0, 2 y 3 a 1, así que los muros norte, sur y oeste están cerrados y el este abierto. Se comprueba cada muro con `cell & mascara`.

## Relacionadas

[[Tipos enteros y conversiones]] · push_swap - Índice · A-Maze-ing - Índice · [[Algoritmos de ordenación y complejidad]] · ft_printf - Índice · Exam Rank 02 · [[ft_toupper]] · [[ft_tolower]]

## Referencias

- [Bitwise operation — Wikipedia](https://en.wikipedia.org/wiki/Bitwise_operation) — AND, OR, XOR, NOT y desplazamientos; máscaras.
- [Arithmetic operators — cppreference](https://en.cppreference.com/w/c/language/operator_arithmetic) — operadores bit a bit y de desplazamiento, casos indefinidos.
- [C Operator Precedence — cppreference](https://en.cppreference.com/w/c/language/operator_precedence) — `&`, `^`, `|` van por debajo de `==`.
- [Logical operators — cppreference](https://en.cppreference.com/w/c/language/operator_logical) — diferencia entre `&&` y `&`.
- [Beej's Guide to C: Bitwise Operations](https://beej.us/guide/bgc/html/split/bitwise-operations.html).
- [N1570 (borrador C11)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) — §6.5.7 (desplazamientos: UB si el resultado no cabe o el desplazamiento es negativo o ≥ ancho; `>>` de negativos definido por la implementación), §6.5.10–6.5.12 (`&`, `^`, `|`).
- [Radix sort — Wikipedia](https://en.wikipedia.org/wiki/Radix_sort) — radix sort LSD.
- Ejemplos compilados con `cc` (Ubuntu clang 12.0.1) en Linux x86_64.
