---
tags: [libft, tests, edge-cases, defensa, valgrind]
---
# libft - Edge cases y tests por función

[[libft - Índice|← Índice]] · Edge cases

> Esta nota tiene **un `main` por cada función** de la libft, para ejecutarlo en la **defensa**. Para cada función explica el *happy path* (el uso normal) y los *edge cases* (los casos límite donde suelen esconderse los fallos), con un `main` listo para copiar y la salida que tiene que dar.

> [!note] Vocabulario
> - **Happy path**: la entrada normal, la que esperas recibir.
> - **Edge case**: una entrada en el límite (vacía, `0`, `INT_MIN`, solape de memoria…). Es donde fallan casi todas las implementaciones.
> - **Test independiente**: un `main` que solo llama a **la función que pruebas**. Si falla `ft_lstnew`, no deben fallar también los tests de `ft_lstsize` o `ft_lstlast`.

---

## Cómo testear en la defensa

El subject no deja entregar archivos que no se usan, así que **no puedes entregar una suite de tests** dentro de la libft. En la defensa se testea **función a función**: el evaluador elige una, tú compilas su `main` contra tu `libft.a` y explicas qué prueba cada línea.

### Dónde están los `main`

Cada `main` de esta nota está también **al final de su `ft_*.c`**, dentro de un comentario `/* */`, así que no se compila con la libft. Justo encima hay otro comentario con el comando para compilarlo y la **lista de casos que prueba**, en el mismo orden en que salen en pantalla. Los dos comentarios pasan `norminette`.

Para usar uno en la defensa:

1. `make` para tener `libft.a`.
2. En `ft_xxx.c`, borra la línea `/*` que abre el bloque del `main` y la `*/` que lo cierra (la primera y la última línea del bloque).
3. Compila ese fichero solo, enlazado con la libft: `cc -Wall -Wextra -Werror ft_xxx.c -L. -lft && ./a.out`. No hay conflicto: como `ft_xxx` ya está definida en tu `.c`, el enlazador no saca la de `libft.a`.
4. Vuelve a poner el comentario (o `git checkout ft_xxx.c`) antes de seguir.

> [!warning] Antes de entregar
> Un `main` comentado no se compila y pasa `norminette`, pero algunos evaluadores piden que no haya código comentado. Si prefieres entregar sin él, guarda los `main` **fuera** de la carpeta que entregas (por ejemplo en `~/libft_mains/`) y usa los de esta nota. Ver [[Git para 42]].

### Compilar y ejecutar

```bash
cd ~/cursus/libft && make                    # genera libft.a
cd ~/libft_mains                             # si los tienes fuera del repo
cc -Wall -Wextra -Werror main_ft_strlen.c -I ~/cursus/libft -L ~/cursus/libft -lft -o t
./t
valgrind --leak-check=full ./t               # en las funciones que usan malloc
```

- `-I ~/cursus/libft`: dónde está `libft.h`.
- `-L ~/cursus/libft -lft`: enlaza con `libft.a` (`-lft` busca `libft.a`). Ver [[Makefile y librerías estáticas]].
- El programa devuelve `0` si todo está `[OK]` y `1` si hay algún `[KO]` (`echo $?` justo después lo muestra).

> [!tip] ¿De qué otras funciones depende la tuya?
> Si compilas con **solo el `.c` de la función** en vez de `-lft` (`cc main_ft_split.c ~/cursus/libft/ft_split.c -I ~/cursus/libft`), el enlazador avisa de las funciones tuyas que usa (`undefined reference to 'ft_strlen'`). Es una pregunta típica de la defensa.

### Cómo están hechos los `main`

Todos siguen el mismo patrón, para que en la defensa los leas igual:

1. Una función `test()` (o `check()`) por fichero que ejecuta **un caso**, imprime `[OK]` o `[KO]`, el resultado de tu función y el **esperado**, y cuenta los fallos en `g_ko`.
2. El esperado sale de la **función original de la libc** siempre que existe (`strlen`, `memmove`, `atoi`…). Si no existe en Linux (`strlcpy`, `strlcat`, `strnstr`, las de la Parte 2 y las listas), está escrito a mano en la llamada.
3. `main` llama primero al **happy path** y después a los **edge cases**, separados por un título. Empieza por el happy path: demuestra que la función funciona y luego defiende los límites.

> [!example] Así se lee una línea de salida
> ```text
> [OK] "ab\0cd" (para en el \0)   ft: 2  libc: 2
> ```
> El caso es `"ab\0cd"`: tu `ft_strlen` devuelve `2`, el `strlen` de la libc también, así que `[OK]`.

> [!note] La Norma
> Los `main` no se entregan y no tienen que pasar `norminette` (algunos pasan de 25 líneas). Aun así están escritos con su estilo (tabulaciones, declaraciones arriba, `while` en vez de `for`) para que los puedas explicar con el mismo lenguaje que tu código. Ver [[La Norma]].

> [!info] Verificado
> Todos los `main` de esta nota se han compilado con `-Wall -Wextra -Werror` y ejecutado con valgrind contra la libft de `cursus/libft` (18-10-2026). Valgrind no da ningún error ni fuga en ninguno. Todos salen `[OK]`. Las salidas que aparecen son las reales.

---

## Parte 1 — Funciones de la libc

### ft_isalpha

Nota: [[ft_isalpha]]

**Happy path**
- Un carácter del rango (`a-z`, `A-Z`) → 1
- Un carácter fuera del rango → 0

**Edge cases**
- Los vecinos de los límites: `@` y `[` (alrededor de `A-Z`), `` ` `` y `{` (alrededor de `a-z`) → 0
- `EOF` (`-1`) → 0
- Bytes 128–255 → 0 (en el locale `C` la libc devuelve 0)
- Barrido completo `-1..255` comparando con la función de la libc: tu función tiene que devolver **exactamente 1 o 0** (lo exige el subject). La libc devuelve 1024, 2048…, así que solo su resultado se pasa a 0/1 antes de comparar

> [!example]- main_ft_isalpha.c
> ```c
> #include <ctype.h>
> #include <stdio.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* El subject exige 1 o 0 exactos; la libc devuelve 1024, 2048... (0 / no 0) */
> static void	test(char *label, int c)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = ft_isalpha(c);
> 	libc = (isalpha(c) != 0);
> 	printf("[%s] %-20s ft: %d  libc: %d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> static void	sweep(void)
> {
> 	int	c;
> 	int	fails;
>
> 	fails = 0;
> 	c = -1;
> 	while (c <= 255)
> 	{
> 		if (ft_isalpha(c) != (isalpha(c) != 0))
> 		{
> 			printf("     distinto en c = %d\n", c);
> 			fails++;
> 		}
> 		c++;
> 	}
> 	printf("[%s] barrido -1..255 contra isalpha (%d diferencias)\n",
> 		fails == 0 ? "OK" : "KO", fails);
> 	if (fails)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'a'", 'a');
> 	test("'Z'", 'Z');
> 	test("'5'", '5');
> 	test("' '", ' ');
> 	printf("--- edge cases ---\n");
> 	test("'A' - 1 ('@')", 'A' - 1);
> 	test("'Z' + 1 ('[')", 'Z' + 1);
> 	test("'a' - 1 ('`')", 'a' - 1);
> 	test("'z' + 1 ('{')", 'z' + 1);
> 	test("EOF (-1)", EOF);
> 	test("0 ('\\0')", 0);
> 	test("200 (byte > 127)", 200);
> 	sweep();
> 	printf("\nft_isalpha: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'a'                  ft: 1  libc: 1
> [OK] 'Z'                  ft: 1  libc: 1
> [OK] '5'                  ft: 0  libc: 0
> [OK] ' '                  ft: 0  libc: 0
> --- edge cases ---
> [OK] 'A' - 1 ('@')        ft: 0  libc: 0
> [OK] 'Z' + 1 ('[')        ft: 0  libc: 0
> [OK] 'a' - 1 ('`')        ft: 0  libc: 0
> [OK] 'z' + 1 ('{')        ft: 0  libc: 0
> [OK] EOF (-1)             ft: 0  libc: 0
> [OK] 0 ('\0')             ft: 0  libc: 0
> [OK] 200 (byte > 127)     ft: 0  libc: 0
> [OK] barrido -1..255 contra isalpha (0 diferencias)
>
> ft_isalpha: 0 KO
> ```

### ft_isdigit

Nota: [[ft_isdigit]]

**Happy path**
- Un carácter del rango (`0-9`) → 1
- Un carácter fuera del rango → 0

**Edge cases**
- Los vecinos de los límites: `'0' - 1` (`/`) y `'9' + 1` (`:`) → 0
- `EOF` (`-1`) → 0
- Bytes 128–255 → 0 (en el locale `C` la libc devuelve 0)
- Barrido completo `-1..255` comparando con la función de la libc: tu función tiene que devolver **exactamente 1 o 0** (lo exige el subject). La libc devuelve 1024, 2048…, así que solo su resultado se pasa a 0/1 antes de comparar

> [!example]- main_ft_isdigit.c
> ```c
> #include <ctype.h>
> #include <stdio.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* El subject exige 1 o 0 exactos; la libc devuelve 1024, 2048... (0 / no 0) */
> static void	test(char *label, int c)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = ft_isdigit(c);
> 	libc = (isdigit(c) != 0);
> 	printf("[%s] %-20s ft: %d  libc: %d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> static void	sweep(void)
> {
> 	int	c;
> 	int	fails;
>
> 	fails = 0;
> 	c = -1;
> 	while (c <= 255)
> 	{
> 		if (ft_isdigit(c) != (isdigit(c) != 0))
> 		{
> 			printf("     distinto en c = %d\n", c);
> 			fails++;
> 		}
> 		c++;
> 	}
> 	printf("[%s] barrido -1..255 contra isdigit (%d diferencias)\n",
> 		fails == 0 ? "OK" : "KO", fails);
> 	if (fails)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'0'", '0');
> 	test("'7'", '7');
> 	test("'a'", 'a');
> 	test("' '", ' ');
> 	printf("--- edge cases ---\n");
> 	test("'0' - 1 ('/')", '0' - 1);
> 	test("'9' + 1 (':')", '9' + 1);
> 	test("'9'", '9');
> 	test("EOF (-1)", EOF);
> 	test("0 ('\\0')", 0);
> 	test("200 (byte > 127)", 200);
> 	sweep();
> 	printf("\nft_isdigit: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] '0'                  ft: 1  libc: 1
> [OK] '7'                  ft: 1  libc: 1
> [OK] 'a'                  ft: 0  libc: 0
> [OK] ' '                  ft: 0  libc: 0
> --- edge cases ---
> [OK] '0' - 1 ('/')        ft: 0  libc: 0
> [OK] '9' + 1 (':')        ft: 0  libc: 0
> [OK] '9'                  ft: 1  libc: 1
> [OK] EOF (-1)             ft: 0  libc: 0
> [OK] 0 ('\0')             ft: 0  libc: 0
> [OK] 200 (byte > 127)     ft: 0  libc: 0
> [OK] barrido -1..255 contra isdigit (0 diferencias)
>
> ft_isdigit: 0 KO
> ```

### ft_isalnum

Nota: [[ft_isalnum]]

**Happy path**
- Un carácter del rango (letras y dígitos) → 1
- Un carácter fuera del rango → 0

**Edge cases**
- Los vecinos de los tres rangos: `/` y `:`, `@` y `[`, `` ` `` y `{` → 0
- `EOF` (`-1`) → 0
- Bytes 128–255 → 0 (en el locale `C` la libc devuelve 0)
- Barrido completo `-1..255` comparando con la función de la libc: tu función tiene que devolver **exactamente 1 o 0** (lo exige el subject). La libc devuelve 1024, 2048…, así que solo su resultado se pasa a 0/1 antes de comparar

> [!example]- main_ft_isalnum.c
> ```c
> #include <ctype.h>
> #include <stdio.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* El subject exige 1 o 0 exactos; la libc devuelve 1024, 2048... (0 / no 0) */
> static void	test(char *label, int c)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = ft_isalnum(c);
> 	libc = (isalnum(c) != 0);
> 	printf("[%s] %-20s ft: %d  libc: %d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> static void	sweep(void)
> {
> 	int	c;
> 	int	fails;
>
> 	fails = 0;
> 	c = -1;
> 	while (c <= 255)
> 	{
> 		if (ft_isalnum(c) != (isalnum(c) != 0))
> 		{
> 			printf("     distinto en c = %d\n", c);
> 			fails++;
> 		}
> 		c++;
> 	}
> 	printf("[%s] barrido -1..255 contra isalnum (%d diferencias)\n",
> 		fails == 0 ? "OK" : "KO", fails);
> 	if (fails)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'a'", 'a');
> 	test("'Z'", 'Z');
> 	test("'5'", '5');
> 	test("' '", ' ');
> 	test("'!'", '!');
> 	printf("--- edge cases ---\n");
> 	test("'0' - 1 ('/')", '0' - 1);
> 	test("'9' + 1 (':')", '9' + 1);
> 	test("'A' - 1 ('@')", 'A' - 1);
> 	test("'Z' + 1 ('[')", 'Z' + 1);
> 	test("'a' - 1 ('`')", 'a' - 1);
> 	test("'z' + 1 ('{')", 'z' + 1);
> 	test("EOF (-1)", EOF);
> 	test("200 (byte > 127)", 200);
> 	sweep();
> 	printf("\nft_isalnum: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'a'                  ft: 1  libc: 1
> [OK] 'Z'                  ft: 1  libc: 1
> [OK] '5'                  ft: 1  libc: 1
> [OK] ' '                  ft: 0  libc: 0
> [OK] '!'                  ft: 0  libc: 0
> --- edge cases ---
> [OK] '0' - 1 ('/')        ft: 0  libc: 0
> [OK] '9' + 1 (':')        ft: 0  libc: 0
> [OK] 'A' - 1 ('@')        ft: 0  libc: 0
> [OK] 'Z' + 1 ('[')        ft: 0  libc: 0
> [OK] 'a' - 1 ('`')        ft: 0  libc: 0
> [OK] 'z' + 1 ('{')        ft: 0  libc: 0
> [OK] EOF (-1)             ft: 0  libc: 0
> [OK] 200 (byte > 127)     ft: 0  libc: 0
> [OK] barrido -1..255 contra isalnum (0 diferencias)
>
> ft_isalnum: 0 KO
> ```

### ft_isascii

Nota: [[ft_isascii]]

**Happy path**
- `'a'`, `' '` → 1

**Edge cases**
- `0` y `127` → 1 (son ASCII)
- `-1` y `128` → 0
- `255`, `INT_MIN`, `INT_MAX` → 0
- Barrido `-1..255` contra `isascii` (tu función tiene que devolver **exactamente 1 o 0**)

> [!example]- main_ft_isascii.c
> ```c
> #include <ctype.h>
> #include <limits.h>
> #include <stdio.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* El subject exige 1 o 0 exactos; la libc devuelve 1024, 2048... (0 / no 0) */
> static void	test(char *label, int c)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = ft_isascii(c);
> 	libc = (isascii(c) != 0);
> 	printf("[%s] %-20s ft: %d  libc: %d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> static void	sweep(void)
> {
> 	int	c;
> 	int	fails;
>
> 	fails = 0;
> 	c = -1;
> 	while (c <= 255)
> 	{
> 		if (ft_isascii(c) != (isascii(c) != 0))
> 		{
> 			printf("     distinto en c = %d\n", c);
> 			fails++;
> 		}
> 		c++;
> 	}
> 	printf("[%s] barrido -1..255 contra isascii (%d diferencias)\n",
> 		fails == 0 ? "OK" : "KO", fails);
> 	if (fails)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'a'", 'a');
> 	test("' '", ' ');
> 	printf("--- edge cases ---\n");
> 	test("0", 0);
> 	test("127", 127);
> 	test("-1", -1);
> 	test("128", 128);
> 	test("255", 255);
> 	test("INT_MIN", INT_MIN);
> 	test("INT_MAX", INT_MAX);
> 	sweep();
> 	printf("\nft_isascii: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'a'                  ft: 1  libc: 1
> [OK] ' '                  ft: 1  libc: 1
> --- edge cases ---
> [OK] 0                    ft: 1  libc: 1
> [OK] 127                  ft: 1  libc: 1
> [OK] -1                   ft: 0  libc: 0
> [OK] 128                  ft: 0  libc: 0
> [OK] 255                  ft: 0  libc: 0
> [OK] INT_MIN              ft: 0  libc: 0
> [OK] INT_MAX              ft: 0  libc: 0
> [OK] barrido -1..255 contra isascii (0 diferencias)
>
> ft_isascii: 0 KO
> ```

### ft_isprint

Nota: [[ft_isprint]]

**Happy path**
- `'a'`, `'~'`, `' '` → 1
- `'\n'`, `'\t'` → 0

**Edge cases**
- `31` (`' ' - 1`) y `127` (DEL) → 0
- `0`, `EOF`, bytes > 127 → 0
- Barrido `-1..255` contra `isprint` (tu función tiene que devolver **exactamente 1 o 0**)

> [!example]- main_ft_isprint.c
> ```c
> #include <ctype.h>
> #include <stdio.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* El subject exige 1 o 0 exactos; la libc devuelve 1024, 2048... (0 / no 0) */
> static void	test(char *label, int c)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = ft_isprint(c);
> 	libc = (isprint(c) != 0);
> 	printf("[%s] %-20s ft: %d  libc: %d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> static void	sweep(void)
> {
> 	int	c;
> 	int	fails;
>
> 	fails = 0;
> 	c = -1;
> 	while (c <= 255)
> 	{
> 		if (ft_isprint(c) != (isprint(c) != 0))
> 		{
> 			printf("     distinto en c = %d\n", c);
> 			fails++;
> 		}
> 		c++;
> 	}
> 	printf("[%s] barrido -1..255 contra isprint (%d diferencias)\n",
> 		fails == 0 ? "OK" : "KO", fails);
> 	if (fails)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'a'", 'a');
> 	test("'~'", '~');
> 	test("' '", ' ');
> 	test("'\\n'", '\n');
> 	test("'\\t'", '\t');
> 	printf("--- edge cases ---\n");
> 	test("31 (' ' - 1)", 31);
> 	test("127 (DEL)", 127);
> 	test("0 ('\\0')", 0);
> 	test("EOF (-1)", EOF);
> 	test("200 (byte > 127)", 200);
> 	sweep();
> 	printf("\nft_isprint: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'a'                  ft: 1  libc: 1
> [OK] '~'                  ft: 1  libc: 1
> [OK] ' '                  ft: 1  libc: 1
> [OK] '\n'                 ft: 0  libc: 0
> [OK] '\t'                 ft: 0  libc: 0
> --- edge cases ---
> [OK] 31 (' ' - 1)         ft: 0  libc: 0
> [OK] 127 (DEL)            ft: 0  libc: 0
> [OK] 0 ('\0')             ft: 0  libc: 0
> [OK] EOF (-1)             ft: 0  libc: 0
> [OK] 200 (byte > 127)     ft: 0  libc: 0
> [OK] barrido -1..255 contra isprint (0 diferencias)
>
> ft_isprint: 0 KO
> ```

### ft_toupper

Nota: [[ft_toupper]]

**Happy path**
- `'a'` → `'A'`, `'z'` → `'Z'`

**Edge cases**
- Mayúsculas y no-letras se devuelven **igual** (`'A'`, `'5'`)
- Vecinos `'a' - 1` (`` ` ``) y `'z' + 1` (`{`) sin cambios
- `EOF` (`-1`), `0`, `200` sin cambios
- Barrido `-1..255` comparando el valor **exacto** con `toupper`

> [!example]- main_ft_toupper.c
> ```c
> #include <ctype.h>
> #include <stdio.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Aquí sí importa el valor exacto */
> static void	test(char *label, int c)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = ft_toupper(c);
> 	libc = toupper(c);
> 	printf("[%s] %-20s ft: %4d  libc: %4d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> static void	sweep(void)
> {
> 	int	c;
> 	int	fails;
>
> 	fails = 0;
> 	c = -1;
> 	while (c <= 255)
> 	{
> 		if (ft_toupper(c) != toupper(c))
> 		{
> 			printf("     distinto en c = %d\n", c);
> 			fails++;
> 		}
> 		c++;
> 	}
> 	printf("[%s] barrido -1..255 contra toupper (%d diferencias)\n",
> 		fails == 0 ? "OK" : "KO", fails);
> 	if (fails)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'a'", 'a');
> 	test("'z'", 'z');
> 	test("'m'", 'm');
> 	printf("--- edge cases ---\n");
> 	test("'A' (ya mayúscula)", 'A');
> 	test("'5' (no es letra)", '5');
> 	test("'a' - 1 ('`')", 'a' - 1);
> 	test("'z' + 1 ('{')", 'z' + 1);
> 	test("EOF (-1)", EOF);
> 	test("0 ('\\0')", 0);
> 	test("200 (byte > 127)", 200);
> 	sweep();
> 	printf("\nft_toupper: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'a'                  ft:   65  libc:   65
> [OK] 'z'                  ft:   90  libc:   90
> [OK] 'm'                  ft:   77  libc:   77
> --- edge cases ---
> [OK] 'A' (ya mayúscula)  ft:   65  libc:   65
> [OK] '5' (no es letra)    ft:   53  libc:   53
> [OK] 'a' - 1 ('`')        ft:   96  libc:   96
> [OK] 'z' + 1 ('{')        ft:  123  libc:  123
> [OK] EOF (-1)             ft:   -1  libc:   -1
> [OK] 0 ('\0')             ft:    0  libc:    0
> [OK] 200 (byte > 127)     ft:  200  libc:  200
> [OK] barrido -1..255 contra toupper (0 diferencias)
>
> ft_toupper: 0 KO
> ```

### ft_tolower

Nota: [[ft_tolower]]

**Happy path**
- `'A'` → `'a'`, `'Z'` → `'z'`

**Edge cases**
- Minúsculas y no-letras se devuelven igual
- Vecinos `'A' - 1` (`@`) y `'Z' + 1` (`[`) sin cambios
- `EOF`, `0`, `200` sin cambios
- Barrido `-1..255` contra `tolower`

> [!example]- main_ft_tolower.c
> ```c
> #include <ctype.h>
> #include <stdio.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Aquí sí importa el valor exacto */
> static void	test(char *label, int c)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = ft_tolower(c);
> 	libc = tolower(c);
> 	printf("[%s] %-20s ft: %4d  libc: %4d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> static void	sweep(void)
> {
> 	int	c;
> 	int	fails;
>
> 	fails = 0;
> 	c = -1;
> 	while (c <= 255)
> 	{
> 		if (ft_tolower(c) != tolower(c))
> 		{
> 			printf("     distinto en c = %d\n", c);
> 			fails++;
> 		}
> 		c++;
> 	}
> 	printf("[%s] barrido -1..255 contra tolower (%d diferencias)\n",
> 		fails == 0 ? "OK" : "KO", fails);
> 	if (fails)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'A'", 'A');
> 	test("'Z'", 'Z');
> 	test("'M'", 'M');
> 	printf("--- edge cases ---\n");
> 	test("'a' (ya minúscula)", 'a');
> 	test("'5' (no es letra)", '5');
> 	test("'A' - 1 ('@')", 'A' - 1);
> 	test("'Z' + 1 ('[')", 'Z' + 1);
> 	test("EOF (-1)", EOF);
> 	test("0 ('\\0')", 0);
> 	test("200 (byte > 127)", 200);
> 	sweep();
> 	printf("\nft_tolower: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'A'                  ft:   97  libc:   97
> [OK] 'Z'                  ft:  122  libc:  122
> [OK] 'M'                  ft:  109  libc:  109
> --- edge cases ---
> [OK] 'a' (ya minúscula)  ft:   97  libc:   97
> [OK] '5' (no es letra)    ft:   53  libc:   53
> [OK] 'A' - 1 ('@')        ft:   64  libc:   64
> [OK] 'Z' + 1 ('[')        ft:   91  libc:   91
> [OK] EOF (-1)             ft:   -1  libc:   -1
> [OK] 0 ('\0')             ft:    0  libc:    0
> [OK] 200 (byte > 127)     ft:  200  libc:  200
> [OK] barrido -1..255 contra tolower (0 diferencias)
>
> ft_tolower: 0 KO
> ```

### ft_strlen

Nota: [[ft_strlen]]

**Happy path**
- `"hola"` → 4

**Edge cases**
- `""` → 0
- Un solo carácter
- Para en el **primer** `'\0'` (`"ab\0cd"` → 2)
- Bytes > 127 cuentan como 1
- Cadena larga (1000)

> [!example]- main_ft_strlen.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	test(char *label, const char *s)
> {
> 	size_t	ft;
> 	size_t	libc;
>
> 	ft = ft_strlen(s);
> 	libc = strlen(s);
> 	printf("[%s] %-26s ft: %zu  libc: %zu\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	char	long_str[1001];
>
> 	memset(long_str, 'x', 1000);
> 	long_str[1000] = '\0';
> 	printf("--- happy path ---\n");
> 	test("\"hola\"", "hola");
> 	test("\"hola mundo\"", "hola mundo");
> 	printf("--- edge cases ---\n");
> 	test("\"\" (vacía)", "");
> 	test("\"a\" (un carácter)", "a");
> 	test("\"ab\\0cd\" (para en el \\0)", "ab\0cd");
> 	test("\"\\xe9t\\xe9\" (bytes > 127)", "\xe9t\xe9");
> 	test("1000 'x'", long_str);
> 	printf("\nft_strlen: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] "hola"                     ft: 4  libc: 4
> [OK] "hola mundo"               ft: 10  libc: 10
> --- edge cases ---
> [OK] "" (vacía)                ft: 0  libc: 0
> [OK] "a" (un carácter)         ft: 1  libc: 1
> [OK] "ab\0cd" (para en el \0)   ft: 2  libc: 2
> [OK] "\xe9t\xe9" (bytes > 127)  ft: 3  libc: 3
> [OK] 1000 'x'                   ft: 1000  libc: 1000
>
> ft_strlen: 0 KO
> ```

### ft_memset

Nota: [[ft_memset]]

**Happy path**
- Rellena `n` bytes y **devuelve `b`**

**Edge cases**
- `n = 0` no toca nada
- `c > 255` se trunca a `unsigned char` (`'B' + 256` escribe `'B'`)
- `c` negativo (`-1` → byte `0xFF`)
- Rellenar con `'\0'`
- Buffer de otro tipo (`int[]`) con `sizeof`
- No se pasa de `n` (comprobar el byte siguiente)

> [!example]- main_ft_memset.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Rellena dos buffers iguales, uno con ft_memset y otro con memset,
>    y compara el buffer entero (también lo que hay después de n) */
> static void	test(char *label, int c, size_t n)
> {
> 	char	ft[10];
> 	char	libc[10];
> 	void	*ret;
> 	int		ok;
>
> 	memcpy(ft, "abcdefghi", 10);
> 	memcpy(libc, "abcdefghi", 10);
> 	ret = ft_memset(ft, c, n);
> 	memset(libc, c, n);
> 	ok = (ret == ft && memcmp(ft, libc, 10) == 0);
> 	printf("[%s] %-28s devuelve s: %s  buffer igual que memset: %s\n",
> 		ok ? "OK" : "KO", label, ret == ft ? "sí" : "NO",
> 		memcmp(ft, libc, 10) == 0 ? "sí" : "NO");
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	int		nums[4];
> 	int		expected[4];
>
> 	printf("--- happy path ---\n");
> 	test("'x', n = 5", 'x', 5);
> 	test("'x', n = 10 (todo)", 'x', 10);
> 	printf("--- edge cases ---\n");
> 	test("n = 0 (no toca nada)", 'x', 0);
> 	test("'\\0', n = 3", '\0', 3);
> 	test("'B' + 256 (se trunca a 'B')", 'B' + 256, 4);
> 	test("-1 (byte 0xFF)", -1, 4);
> 	memset(expected, 0, sizeof(expected));
> 	nums[0] = 1;
> 	nums[1] = 2;
> 	nums[2] = 3;
> 	nums[3] = 4;
> 	ft_memset(nums, 0, sizeof(nums));
> 	printf("[%s] int[4] a 0 con sizeof\n",
> 		memcmp(nums, expected, sizeof(nums)) == 0 ? "OK" : "KO");
> 	if (memcmp(nums, expected, sizeof(nums)) != 0)
> 		g_ko++;
> 	printf("\nft_memset: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'x', n = 5                   devuelve s: sí  buffer igual que memset: sí
> [OK] 'x', n = 10 (todo)           devuelve s: sí  buffer igual que memset: sí
> --- edge cases ---
> [OK] n = 0 (no toca nada)         devuelve s: sí  buffer igual que memset: sí
> [OK] '\0', n = 3                  devuelve s: sí  buffer igual que memset: sí
> [OK] 'B' + 256 (se trunca a 'B')  devuelve s: sí  buffer igual que memset: sí
> [OK] -1 (byte 0xFF)               devuelve s: sí  buffer igual que memset: sí
> [OK] int[4] a 0 con sizeof
>
> ft_memset: 0 KO
> ```

### ft_bzero

Nota: [[ft_bzero]]

**Happy path**
- Pone a 0 los `n` primeros bytes

**Edge cases**
- `n = 0` no toca nada
- No se para en un `'\0'` que ya estuviera
- No se pasa de `n`
- Buffer de otro tipo

> [!example]- main_ft_bzero.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include <strings.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Compara el buffer entero con el resultado de bzero de la libc */
> static void	test(char *label, const char *initial, size_t n)
> {
> 	char	ft[10];
> 	char	libc[10];
> 	int		ok;
>
> 	memcpy(ft, initial, 10);
> 	memcpy(libc, initial, 10);
> 	ft_bzero(ft, n);
> 	bzero(libc, n);
> 	ok = (memcmp(ft, libc, 10) == 0);
> 	printf("[%s] %-34s buffer igual que bzero: %s\n",
> 		ok ? "OK" : "KO", label, ok ? "sí" : "NO");
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	int		nums[4];
> 	int		expected[4];
>
> 	printf("--- happy path ---\n");
> 	test("n = 5", "abcdefghi", 5);
> 	test("n = 10 (todo)", "abcdefghi", 10);
> 	printf("--- edge cases ---\n");
> 	test("n = 0 (no toca nada)", "abcdefghi", 0);
> 	test("sigue tras un '\\0' (\"ab\\0defghi\", 6)", "ab\0defghi", 6);
> 	test("no se pasa de n (n = 1)", "abcdefghi", 1);
> 	memset(expected, 0, sizeof(expected));
> 	nums[0] = 1;
> 	nums[1] = 2;
> 	nums[2] = 3;
> 	nums[3] = 4;
> 	ft_bzero(nums, sizeof(nums));
> 	printf("[%s] int[4] a 0 con sizeof\n",
> 		memcmp(nums, expected, sizeof(nums)) == 0 ? "OK" : "KO");
> 	if (memcmp(nums, expected, sizeof(nums)) != 0)
> 		g_ko++;
> 	printf("\nft_bzero: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] n = 5                              buffer igual que bzero: sí
> [OK] n = 10 (todo)                      buffer igual que bzero: sí
> --- edge cases ---
> [OK] n = 0 (no toca nada)               buffer igual que bzero: sí
> [OK] sigue tras un '\0' ("ab\0defghi", 6) buffer igual que bzero: sí
> [OK] no se pasa de n (n = 1)            buffer igual que bzero: sí
> [OK] int[4] a 0 con sizeof
>
> ft_bzero: 0 KO
> ```

### ft_memcpy

Nota: [[ft_memcpy]]

**Happy path**
- Copia `n` bytes y **devuelve `dst`**

**Edge cases**
- `n = 0` no toca nada y devuelve `dst`
- `src = NULL` con `n = 0` → devuelve `dst` sin petar
- Copia **a través** de los `'\0'` (no es una copia de cadena)
- No escribe más allá de `n`
- Buffer de otro tipo

> [!example]- main_ft_memcpy.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	test(char *label, const char *src, size_t n)
> {
> 	char	ft[10];
> 	char	libc[10];
> 	void	*ret;
> 	int		ok;
>
> 	memcpy(ft, "---------", 10);
> 	memcpy(libc, "---------", 10);
> 	ret = ft_memcpy(ft, src, n);
> 	memcpy(libc, src, n);
> 	ok = (ret == ft && memcmp(ft, libc, 10) == 0);
> 	printf("[%s] %-30s devuelve dst: %s  buffer igual que memcpy: %s\n",
> 		ok ? "OK" : "KO", label, ret == ft ? "sí" : "NO",
> 		memcmp(ft, libc, 10) == 0 ? "sí" : "NO");
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	char	dst[4];
> 	int		src_nums[3];
> 	int		dst_nums[3];
>
> 	printf("--- happy path ---\n");
> 	test("\"hola\", n = 4", "hola", 4);
> 	test("\"hola\", n = 5 (con el \\0)", "hola", 5);
> 	printf("--- edge cases ---\n");
> 	test("n = 0 (no toca nada)", "hola", 0);
> 	test("copia a través del \\0 (\"a\\0b\\0c\")", "a\0b\0c", 5);
> 	test("no escribe más allá de n (n = 2)", "hola", 2);
> 	printf("[%s] src = NULL con n = 0 devuelve dst\n",
> 		ft_memcpy(dst, NULL, 0) == dst ? "OK" : "KO");
> 	if (ft_memcpy(dst, NULL, 0) != dst)
> 		g_ko++;
> 	src_nums[0] = -1;
> 	src_nums[1] = 42;
> 	src_nums[2] = 2147483647;
> 	ft_memcpy(dst_nums, src_nums, sizeof(src_nums));
> 	printf("[%s] int[3] con sizeof\n",
> 		memcmp(dst_nums, src_nums, sizeof(src_nums)) == 0 ? "OK" : "KO");
> 	if (memcmp(dst_nums, src_nums, sizeof(src_nums)) != 0)
> 		g_ko++;
> 	printf("\nft_memcpy: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] "hola", n = 4                  devuelve dst: sí  buffer igual que memcpy: sí
> [OK] "hola", n = 5 (con el \0)      devuelve dst: sí  buffer igual que memcpy: sí
> --- edge cases ---
> [OK] n = 0 (no toca nada)           devuelve dst: sí  buffer igual que memcpy: sí
> [OK] copia a través del \0 ("a\0b\0c") devuelve dst: sí  buffer igual que memcpy: sí
> [OK] no escribe más allá de n (n = 2) devuelve dst: sí  buffer igual que memcpy: sí
> [OK] src = NULL con n = 0 devuelve dst
> [OK] int[3] con sizeof
>
> ft_memcpy: 0 KO
> ```

### ft_memmove

Nota: [[ft_memmove]]

**Happy path**
- Copia `n` bytes **aunque las zonas se solapen** y devuelve `dst`

**Edge cases**
- Solape con `dst > src` → hay que copiar **de atrás hacia delante**
- Solape con `dst < src` → de delante hacia atrás
- `dst == src`
- `n = 0`
- Sin solape y con `'\0'` dentro
- Solape máximo (desplazar 1 posición todo el buffer)

> [!example]- main_ft_memmove.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Mueve n bytes de buf + from a buf + to, en dos buffers iguales:
>    uno con ft_memmove y otro con memmove */
> static void	test(char *label, size_t to, size_t from, size_t n)
> {
> 	char	ft[11];
> 	char	libc[11];
> 	void	*ret;
> 	int		ok;
>
> 	memcpy(ft, "0123456789", 11);
> 	memcpy(libc, "0123456789", 11);
> 	ret = ft_memmove(ft + to, ft + from, n);
> 	memmove(libc + to, libc + from, n);
> 	ok = (ret == ft + to && memcmp(ft, libc, 11) == 0);
> 	printf("[%s] %-36s ft: %s  libc: %s\n",
> 		ok ? "OK" : "KO", label, ft, libc);
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	char	a[6];
>
> 	printf("--- happy path ---\n");
> 	test("sin solape (0..3 -> 5..8)", 5, 0, 4);
> 	printf("--- edge cases ---\n");
> 	test("solape, dst > src (0..5 -> 2..7)", 2, 0, 6);
> 	test("solape, dst < src (2..7 -> 0..5)", 0, 2, 6);
> 	test("desplazar todo 1 a la derecha", 1, 0, 9);
> 	test("desplazar todo 1 a la izquierda", 0, 1, 9);
> 	test("dst == src", 3, 3, 4);
> 	test("n = 0", 2, 0, 0);
> 	memcpy(a, "-----", 6);
> 	ft_memmove(a, "a\0b\0", 4);
> 	printf("[%s] copia a través del \\0\n",
> 		memcmp(a, "a\0b\0-", 6) == 0 ? "OK" : "KO");
> 	if (memcmp(a, "a\0b\0-", 6) != 0)
> 		g_ko++;
> 	printf("\nft_memmove: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] sin solape (0..3 -> 5..8)            ft: 0123401239  libc: 0123401239
> --- edge cases ---
> [OK] solape, dst > src (0..5 -> 2..7)     ft: 0101234589  libc: 0101234589
> [OK] solape, dst < src (2..7 -> 0..5)     ft: 2345676789  libc: 2345676789
> [OK] desplazar todo 1 a la derecha        ft: 0012345678  libc: 0012345678
> [OK] desplazar todo 1 a la izquierda      ft: 1234567899  libc: 1234567899
> [OK] dst == src                           ft: 0123456789  libc: 0123456789
> [OK] n = 0                                ft: 0123456789  libc: 0123456789
> [OK] copia a través del \0
>
> ft_memmove: 0 KO
> ```

### ft_memchr

Nota: [[ft_memchr]]

**Happy path**
- Devuelve puntero a la **primera** aparición del byte, o `NULL`

**Edge cases**
- Encuentra el `'\0'` y **sigue buscando después** de él
- Respeta `n` (el byte existe pero más allá de `n` → `NULL`)
- `n = 0` → `NULL`
- Byte > 127 buscado como `200` y como `-56`: ambos deben encontrarlo (se compara como `unsigned char`)
- `c + 256` se trunca

> [!example]- main_ft_memchr.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Muestra la posición encontrada (o NULL) con ft_memchr y con memchr */
> static void	test(char *label, const char *s, int c, size_t n)
> {
> 	char	*ft;
> 	char	*libc;
>
> 	ft = ft_memchr(s, c, n);
> 	libc = memchr(s, c, n);
> 	printf("[%s] %-34s ft: ", ft == libc ? "OK" : "KO", label);
> 	if (ft)
> 		printf("s + %-4ld", (long)(ft - s));
> 	else
> 		printf("NULL    ");
> 	printf(" libc: ");
> 	if (libc)
> 		printf("s + %ld\n", (long)(libc - s));
> 	else
> 		printf("NULL\n");
> 	if (ft != libc)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'l' en \"hola\"", "hola", 'l', 4);
> 	test("'o' en \"hola hola\" (la primera)", "hola hola", 'o', 9);
> 	test("'z' en \"hola\" (no está)", "hola", 'z', 4);
> 	printf("--- edge cases ---\n");
> 	test("busca el '\\0'", "hola", '\0', 5);
> 	test("sigue tras el \\0 (\"ab\\0cd\", 'c')", "ab\0cd", 'c', 5);
> 	test("'a' más allá de n (n = 2)", "hola", 'a', 2);
> 	test("n = 0", "hola", 'h', 0);
> 	test("byte 0xC8 buscado como 200", "ab\xc8z", 200, 4);
> 	test("byte 0xC8 buscado como -56", "ab\xc8z", -56, 4);
> 	test("'l' + 256 (se trunca a 'l')", "hola", 'l' + 256, 4);
> 	printf("\nft_memchr: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'l' en "hola"                      ft: s + 2    libc: s + 2
> [OK] 'o' en "hola hola" (la primera)    ft: s + 1    libc: s + 1
> [OK] 'z' en "hola" (no está)           ft: NULL     libc: NULL
> --- edge cases ---
> [OK] busca el '\0'                      ft: s + 4    libc: s + 4
> [OK] sigue tras el \0 ("ab\0cd", 'c')   ft: s + 3    libc: s + 3
> [OK] 'a' más allá de n (n = 2)        ft: NULL     libc: NULL
> [OK] n = 0                              ft: NULL     libc: NULL
> [OK] byte 0xC8 buscado como 200         ft: s + 2    libc: s + 2
> [OK] byte 0xC8 buscado como -56         ft: s + 2    libc: s + 2
> [OK] 'l' + 256 (se trunca a 'l')        ft: s + 2    libc: s + 2
>
> ft_memchr: 0 KO
> ```

### ft_memcmp

Nota: [[ft_memcmp]]

**Happy path**
- Iguales → 0; distinto → signo de la primera diferencia

**Edge cases**
- Diferencia más allá de `n` → 0
- `n = 0` → 0
- **Sigue tras el `'\0'`** (`"a\0b"` vs `"a\0c"`)
- Comparación **unsigned**: `0x80 > 0x01`, `0xFF > 0x00`

> [!example]- main_ft_memcmp.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static int	sign(int n)
> {
> 	return ((n > 0) - (n < 0));
> }
>
> /* Solo importa el signo (-1, 0, 1), no el valor exacto */
> static void	test(char *label, const char *a, const char *b, size_t n)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = sign(ft_memcmp(a, b, n));
> 	libc = sign(memcmp(a, b, n));
> 	printf("[%s] %-38s ft: %2d  libc: %2d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("\"hola\" vs \"hola\"", "hola", "hola", 4);
> 	test("\"hola\" vs \"hole\"", "hola", "hole", 4);
> 	test("\"hole\" vs \"hola\"", "hole", "hola", 4);
> 	printf("--- edge cases ---\n");
> 	test("diferencia más allá de n (n = 3)", "hola", "hole", 3);
> 	test("n = 0", "abc", "xyz", 0);
> 	test("sigue tras el \\0 (\"a\\0b\" vs \"a\\0c\")", "a\0b", "a\0c", 3);
> 	test("unsigned: \"\\x80\" vs \"\\x01\"", "\x80", "\x01", 1);
> 	test("unsigned: \"\\xff\" vs \"\\0\"", "\xff", "\0", 1);
> 	printf("\nft_memcmp: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] "hola" vs "hola"                       ft:  0  libc:  0
> [OK] "hola" vs "hole"                       ft: -1  libc: -1
> [OK] "hole" vs "hola"                       ft:  1  libc:  1
> --- edge cases ---
> [OK] diferencia más allá de n (n = 3)     ft:  0  libc:  0
> [OK] n = 0                                  ft:  0  libc:  0
> [OK] sigue tras el \0 ("a\0b" vs "a\0c")    ft: -1  libc: -1
> [OK] unsigned: "\x80" vs "\x01"             ft:  1  libc:  1
> [OK] unsigned: "\xff" vs "\0"               ft:  1  libc:  1
>
> ft_memcmp: 0 KO
> ```

### ft_strchr

Nota: [[ft_strchr]]

**Happy path**
- Puntero a la **primera** aparición, o `NULL`

**Edge cases**
- `c = '\0'` → puntero al terminador (no `NULL`)
- Cadena vacía: `'a'` → `NULL`, `'\0'` → la propia cadena
- `c + 256` se convierte a `char`
- Byte > 127 (`0xe9`) tanto como `int` positivo como `char` negativo

> [!example]- main_ft_strchr.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	test(char *label, const char *s, int c)
> {
> 	char	*ft;
> 	char	*libc;
>
> 	ft = ft_strchr(s, c);
> 	libc = strchr(s, c);
> 	printf("[%s] %-34s ft: ", ft == libc ? "OK" : "KO", label);
> 	if (ft)
> 		printf("s + %-4ld", (long)(ft - s));
> 	else
> 		printf("NULL    ");
> 	printf(" libc: ");
> 	if (libc)
> 		printf("s + %ld\n", (long)(libc - s));
> 	else
> 		printf("NULL\n");
> 	if (ft != libc)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'l' en \"hola\"", "hola", 'l');
> 	test("'o' en \"hola hola\" (la primera)", "hola hola", 'o');
> 	test("'z' en \"hola\" (no está)", "hola", 'z');
> 	printf("--- edge cases ---\n");
> 	test("'\\0' (puntero al terminador)", "hola", '\0');
> 	test("'a' en \"\"", "", 'a');
> 	test("'\\0' en \"\"", "", '\0');
> 	test("'h' (posición 0)", "hola", 'h');
> 	test("'l' + 256 (se convierte a 'l')", "hola", 'l' + 256);
> 	test("byte 0xE9 buscado como 233", "caf\xe9", 0xe9);
> 	test("byte 0xE9 buscado como (char)", "caf\xe9", (char)0xe9);
> 	printf("\nft_strchr: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'l' en "hola"                      ft: s + 2    libc: s + 2
> [OK] 'o' en "hola hola" (la primera)    ft: s + 1    libc: s + 1
> [OK] 'z' en "hola" (no está)           ft: NULL     libc: NULL
> --- edge cases ---
> [OK] '\0' (puntero al terminador)       ft: s + 4    libc: s + 4
> [OK] 'a' en ""                          ft: NULL     libc: NULL
> [OK] '\0' en ""                         ft: s + 0    libc: s + 0
> [OK] 'h' (posición 0)                  ft: s + 0    libc: s + 0
> [OK] 'l' + 256 (se convierte a 'l')     ft: s + 2    libc: s + 2
> [OK] byte 0xE9 buscado como 233         ft: s + 3    libc: s + 3
> [OK] byte 0xE9 buscado como (char)      ft: s + 3    libc: s + 3
>
> ft_strchr: 0 KO
> ```

### ft_strrchr

Nota: [[ft_strrchr]]

**Happy path**
- Puntero a la **última** aparición, o `NULL`

**Edge cases**
- Única aparición en la posición 0 (no saltársela al recorrer hacia atrás)
- `c = '\0'` → terminador
- Cadena vacía con `'a'` y con `'\0'`
- `c + 256`

> [!example]- main_ft_strrchr.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	test(char *label, const char *s, int c)
> {
> 	char	*ft;
> 	char	*libc;
>
> 	ft = ft_strrchr(s, c);
> 	libc = strrchr(s, c);
> 	printf("[%s] %-34s ft: ", ft == libc ? "OK" : "KO", label);
> 	if (ft)
> 		printf("s + %-4ld", (long)(ft - s));
> 	else
> 		printf("NULL    ");
> 	printf(" libc: ");
> 	if (libc)
> 		printf("s + %ld\n", (long)(libc - s));
> 	else
> 		printf("NULL\n");
> 	if (ft != libc)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("'o' en \"hola hola\" (la última)", "hola hola", 'o');
> 	test("'z' en \"hola\" (no está)", "hola", 'z');
> 	printf("--- edge cases ---\n");
> 	test("'h' solo en la posición 0", "hola", 'h');
> 	test("'a' en la última posición", "hola", 'a');
> 	test("'\\0' (puntero al terminador)", "hola", '\0');
> 	test("'a' en \"\"", "", 'a');
> 	test("'\\0' en \"\"", "", '\0');
> 	test("'o' + 256 (se convierte a 'o')", "hola hola", 'o' + 256);
> 	printf("\nft_strrchr: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 'o' en "hola hola" (la última)    ft: s + 6    libc: s + 6
> [OK] 'z' en "hola" (no está)           ft: NULL     libc: NULL
> --- edge cases ---
> [OK] 'h' solo en la posición 0         ft: s + 0    libc: s + 0
> [OK] 'a' en la última posición        ft: s + 3    libc: s + 3
> [OK] '\0' (puntero al terminador)       ft: s + 4    libc: s + 4
> [OK] 'a' en ""                          ft: NULL     libc: NULL
> [OK] '\0' en ""                         ft: s + 0    libc: s + 0
> [OK] 'o' + 256 (se convierte a 'o')     ft: s + 6    libc: s + 6
>
> ft_strrchr: 0 KO
> ```

### ft_strncmp

Nota: [[ft_strncmp]]

**Happy path**
- Iguales → 0; distintas → signo de la diferencia

**Edge cases**
- Diferencia más allá de `n` → 0
- `n = 0` → 0
- Una es prefijo de la otra (`"hol"` vs `"hola"`)
- **Para en el `'\0'`**: `"abc\0x"` vs `"abc\0y"` con `n = 5` → 0
- Comparación unsigned (`"\x80"` > `"a"`)
- `n = SIZE_MAX`

> [!example]- main_ft_strncmp.c
> ```c
> #include <stdint.h>
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static int	sign(int n)
> {
> 	return ((n > 0) - (n < 0));
> }
>
> /* Solo importa el signo (-1, 0, 1), no el valor exacto */
> static void	test(char *label, const char *a, const char *b, size_t n)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = sign(ft_strncmp(a, b, n));
> 	libc = sign(strncmp(a, b, n));
> 	printf("[%s] %-40s ft: %2d  libc: %2d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("\"hola\" vs \"hola\"", "hola", "hola", 4);
> 	test("\"hola\" vs \"hole\"", "hola", "hole", 4);
> 	test("\"hole\" vs \"hola\"", "hole", "hola", 4);
> 	printf("--- edge cases ---\n");
> 	test("diferencia más allá de n (n = 3)", "hola", "hole", 3);
> 	test("n = 0", "abc", "xyz", 0);
> 	test("prefijo: \"hol\" vs \"hola\"", "hol", "hola", 10);
> 	test("prefijo: \"hola\" vs \"hol\"", "hola", "hol", 10);
> 	test("\"\" vs \"\"", "", "", 5);
> 	test("\"\" vs \"a\"", "", "a", 5);
> 	test("para en el \\0 (\"abc\\0x\" vs \"abc\\0y\")", "abc\0x", "abc\0y", 5);
> 	test("unsigned: \"\\x80\" vs \"a\"", "\x80", "a", 1);
> 	test("n = SIZE_MAX", "hola", "hole", SIZE_MAX);
> 	printf("\nft_strncmp: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] "hola" vs "hola"                         ft:  0  libc:  0
> [OK] "hola" vs "hole"                         ft: -1  libc: -1
> [OK] "hole" vs "hola"                         ft:  1  libc:  1
> --- edge cases ---
> [OK] diferencia más allá de n (n = 3)       ft:  0  libc:  0
> [OK] n = 0                                    ft:  0  libc:  0
> [OK] prefijo: "hol" vs "hola"                 ft: -1  libc: -1
> [OK] prefijo: "hola" vs "hol"                 ft:  1  libc:  1
> [OK] "" vs ""                                 ft:  0  libc:  0
> [OK] "" vs "a"                                ft: -1  libc: -1
> [OK] para en el \0 ("abc\0x" vs "abc\0y")     ft:  0  libc:  0
> [OK] unsigned: "\x80" vs "a"                  ft:  1  libc:  1
> [OK] n = SIZE_MAX                             ft: -1  libc: -1
>
> ft_strncmp: 0 KO
> ```

### ft_strlcpy

Nota: [[ft_strlcpy]]

**Happy path**
- Copia y devuelve **siempre `strlen(src)`**

**Edge cases**
- Cabe justo (`size = len + 1`)
- Trunca (`size < len + 1`) y siempre termina en `'\0'`
- `size = 1` → solo `'\0'`
- `size = 0` → **no escribe nada** pero devuelve `strlen(src)`
- `src` vacío

> [!example]- main_ft_strlcpy.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* dst empieza lleno de 'X' para ver qué bytes se han escrito */
> static void	test(char *label, const char *src, size_t size,
> 		const char *expected_dst, size_t expected_ret)
> {
> 	char	dst[10];
> 	size_t	ret;
> 	int		ok;
>
> 	memset(dst, 'X', 9);
> 	dst[9] = '\0';
> 	ret = ft_strlcpy(dst, src, size);
> 	ok = (ret == expected_ret && strcmp(dst, expected_dst) == 0);
> 	printf("[%s] %-30s dst: \"%s\" (esperado \"%s\")"
> 		"  ret: %zu (esperado %zu)\n",
> 		ok ? "OK" : "KO", label, dst, expected_dst, ret, expected_ret);
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("\"hola\", size = 10", "hola", 10, "hola", 4);
> 	printf("--- edge cases ---\n");
> 	test("cabe justo (size = 5)", "hola", 5, "hola", 4);
> 	test("trunca (size = 3)", "hola", 3, "ho", 4);
> 	test("size = 1 (solo el \\0)", "hola", 1, "", 4);
> 	test("size = 0 (no escribe nada)", "hola", 0, "XXXXXXXXX", 4);
> 	test("src vacío", "", 10, "", 0);
> 	printf("\nft_strlcpy: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] "hola", size = 10              dst: "hola" (esperado "hola")  ret: 4 (esperado 4)
> --- edge cases ---
> [OK] cabe justo (size = 5)          dst: "hola" (esperado "hola")  ret: 4 (esperado 4)
> [OK] trunca (size = 3)              dst: "ho" (esperado "ho")  ret: 4 (esperado 4)
> [OK] size = 1 (solo el \0)          dst: "" (esperado "")  ret: 4 (esperado 4)
> [OK] size = 0 (no escribe nada)     dst: "XXXXXXXXX" (esperado "XXXXXXXXX")  ret: 4 (esperado 4)
> [OK] src vacío                     dst: "" (esperado "")  ret: 0 (esperado 0)
>
> ft_strlcpy: 0 KO
> ```

### ft_strlcat

Nota: [[ft_strlcat]]

**Happy path**
- Concatena y devuelve `strlen(dst) + strlen(src)`

**Edge cases**
- Cabe justo
- Trunca
- `size < strlen(dst)` → no toca `dst` y devuelve **`size + strlen(src)`**
- `size == strlen(dst)`
- `size = 0`
- `src` vacío
- `dst` vacío

> [!example]- main_ft_strlcat.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	test(char *label, const char *initial_dst, const char *src,
> 		size_t size, const char *expected_dst, size_t expected_ret)
> {
> 	char	dst[20];
> 	size_t	ret;
> 	int		ok;
>
> 	memset(dst, 'X', 19);
> 	dst[19] = '\0';
> 	strcpy(dst, initial_dst);
> 	ret = ft_strlcat(dst, src, size);
> 	ok = (ret == expected_ret && strcmp(dst, expected_dst) == 0);
> 	printf("[%s] %-34s dst: \"%s\" (esperado \"%s\")"
> 		"  ret: %zu (esperado %zu)\n",
> 		ok ? "OK" : "KO", label, dst, expected_dst, ret, expected_ret);
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("\"ho\" + \"la\", size = 20", "ho", "la", 20, "hola", 4);
> 	printf("--- edge cases ---\n");
> 	test("cabe justo (size = 5)", "ho", "la", 5, "hola", 4);
> 	test("trunca (size = 4)", "ho", "la", 4, "hol", 4);
> 	test("size == strlen(dst) (size = 2)", "ho", "la", 2, "ho", 4);
> 	test("size < strlen(dst) (size = 1)", "hola", "123", 1, "hola", 4);
> 	test("size = 0", "hola", "123", 0, "hola", 3);
> 	test("src vacío", "hola", "", 20, "hola", 4);
> 	test("dst vacío", "", "hola", 20, "hola", 4);
> 	printf("\nft_strlcat: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] "ho" + "la", size = 20             dst: "hola" (esperado "hola")  ret: 4 (esperado 4)
> --- edge cases ---
> [OK] cabe justo (size = 5)              dst: "hola" (esperado "hola")  ret: 4 (esperado 4)
> [OK] trunca (size = 4)                  dst: "hol" (esperado "hol")  ret: 4 (esperado 4)
> [OK] size == strlen(dst) (size = 2)     dst: "ho" (esperado "ho")  ret: 4 (esperado 4)
> [OK] size < strlen(dst) (size = 1)      dst: "hola" (esperado "hola")  ret: 4 (esperado 4)
> [OK] size = 0                           dst: "hola" (esperado "hola")  ret: 3 (esperado 3)
> [OK] src vacío                         dst: "hola" (esperado "hola")  ret: 4 (esperado 4)
> [OK] dst vacío                         dst: "hola" (esperado "hola")  ret: 4 (esperado 4)
>
> ft_strlcat: 0 KO
> ```

### ft_strnstr

Nota: [[ft_strnstr]]

**Happy path**
- Encuentra `needle` dentro de los primeros `len` bytes

**Edge cases**
- `needle` vacío → devuelve `haystack` (incluso con `len = 0`)
- `len = 0` con `needle` no vacío → `NULL`
- `needle` cortado por `len` → `NULL`; cabe justo → encontrado
- Coincidencia parcial y reinicio (`"aaab"` busca `"aab"`)
- `needle` más largo que `haystack`
- `len` mayor que la cadena: para en el `'\0'`

> [!example]- main_ft_strnstr.c
> ```c
> #include <stdio.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* expected_pos = -1 significa que se espera NULL */
> static void	test(char *label, const char *big, const char *little,
> 		size_t len, long expected_pos)
> {
> 	char	*ret;
> 	long	pos;
>
> 	ret = ft_strnstr(big, little, len);
> 	pos = -1;
> 	if (ret)
> 		pos = (long)(ret - big);
> 	printf("[%s] %-38s ft: ", pos == expected_pos ? "OK" : "KO", label);
> 	if (pos == -1)
> 		printf("NULL    ");
> 	else
> 		printf("big + %-2ld", pos);
> 	if (expected_pos == -1)
> 		printf(" esperado: NULL\n");
> 	else
> 		printf(" esperado: big + %ld\n", expected_pos);
> 	if (pos != expected_pos)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("\"mundo\" en \"hola mundo\"", "hola mundo", "mundo", 10, 5);
> 	test("\"adios\" en \"hola mundo\"", "hola mundo", "adios", 10, -1);
> 	printf("--- edge cases ---\n");
> 	test("needle vacío", "hola", "", 4, 0);
> 	test("needle vacío con len = 0", "hola", "", 0, 0);
> 	test("len = 0", "hola", "h", 0, -1);
> 	test("needle cortado por len (len = 9)", "hola mundo", "mundo", 9, -1);
> 	test("needle cabe justo (len = 10)", "hola mundo", "mundo", 10, 5);
> 	test("coincidencia parcial (\"aab\" en \"aaab\")", "aaab", "aab", 4, 1);
> 	test("needle más largo que big", "hola", "hola mundo", 20, -1);
> 	test("len mayor que big", "hola", "la", 100, 2);
> 	printf("\nft_strnstr: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] "mundo" en "hola mundo"                ft: big + 5  esperado: big + 5
> [OK] "adios" en "hola mundo"                ft: NULL     esperado: NULL
> --- edge cases ---
> [OK] needle vacío                          ft: big + 0  esperado: big + 0
> [OK] needle vacío con len = 0              ft: big + 0  esperado: big + 0
> [OK] len = 0                                ft: NULL     esperado: NULL
> [OK] needle cortado por len (len = 9)       ft: NULL     esperado: NULL
> [OK] needle cabe justo (len = 10)           ft: big + 5  esperado: big + 5
> [OK] coincidencia parcial ("aab" en "aaab") ft: big + 1  esperado: big + 1
> [OK] needle más largo que big              ft: NULL     esperado: NULL
> [OK] len mayor que big                      ft: big + 2  esperado: big + 2
>
> ft_strnstr: 0 KO
> ```

### ft_atoi

Nota: [[ft_atoi]]

**Happy path**
- `"42"`, `"-42"`, `"+42"`

**Edge cases**
- Espacios iniciales: **los 6** (`' '`, `\t`, `\n`, `\v`, `\f`, `\r`)
- Ceros a la izquierda (`"0042"`), `"-0"`
- Para en el primer no-dígito (`"42abc"`, `"4 2"`)
- Sin dígitos: `""`, `"   "`, `"+"`, `"-"`, `"abc"` → 0
- Signos dobles o mezclados → 0
- Espacio entre signo y número → 0
- `INT_MAX` y `INT_MIN`
- Todo comparado con `atoi` de la libc. El desbordamiento es comportamiento indefinido: no lo testees

> [!example]- main_ft_atoi.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	test(char *label, const char *s)
> {
> 	int	ft;
> 	int	libc;
>
> 	ft = ft_atoi(s);
> 	libc = atoi(s);
> 	printf("[%s] %-30s ft: %11d  libc: %11d\n",
> 		ft == libc ? "OK" : "KO", label, ft, libc);
> 	if (ft != libc)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("\"42\"", "42");
> 	test("\"-42\"", "-42");
> 	test("\"+42\"", "+42");
> 	printf("--- edge cases ---\n");
> 	test("\" \\t\\n\\v\\f\\r42\" (6 blancos)", " \t\n\v\f\r42");
> 	test("\"   -42\"", "   -42");
> 	test("\"0042\"", "0042");
> 	test("\"-0\"", "-0");
> 	test("\"42abc\"", "42abc");
> 	test("\"4 2\"", "4 2");
> 	test("\"\"", "");
> 	test("\"   \"", "   ");
> 	test("\"+\"", "+");
> 	test("\"-\"", "-");
> 	test("\"abc\"", "abc");
> 	test("\"--42\"", "--42");
> 	test("\"+-42\"", "+-42");
> 	test("\"- 42\"", "- 42");
> 	test("\"2147483647\" (INT_MAX)", "2147483647");
> 	test("\"-2147483648\" (INT_MIN)", "-2147483648");
> 	printf("\nft_atoi: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] "42"                           ft:          42  libc:          42
> [OK] "-42"                          ft:         -42  libc:         -42
> [OK] "+42"                          ft:          42  libc:          42
> --- edge cases ---
> [OK] " \t\n\v\f\r42" (6 blancos)    ft:          42  libc:          42
> [OK] "   -42"                       ft:         -42  libc:         -42
> [OK] "0042"                         ft:          42  libc:          42
> [OK] "-0"                           ft:           0  libc:           0
> [OK] "42abc"                        ft:          42  libc:          42
> [OK] "4 2"                          ft:           4  libc:           4
> [OK] ""                             ft:           0  libc:           0
> [OK] "   "                          ft:           0  libc:           0
> [OK] "+"                            ft:           0  libc:           0
> [OK] "-"                            ft:           0  libc:           0
> [OK] "abc"                          ft:           0  libc:           0
> [OK] "--42"                         ft:           0  libc:           0
> [OK] "+-42"                         ft:           0  libc:           0
> [OK] "- 42"                         ft:           0  libc:           0
> [OK] "2147483647" (INT_MAX)         ft:  2147483647  libc:  2147483647
> [OK] "-2147483648" (INT_MIN)        ft: -2147483648  libc: -2147483648
>
> ft_atoi: 0 KO
> ```

### ft_calloc

Nota: [[ft_calloc]]

**Happy path**
- Reserva `nmemb * size` bytes **todos a 0**

**Edge cases**
- `(0, 0)` y `(0, n)` → puntero válido que se puede pasar a `free`
- **Overflow** de `nmemb * size` → `NULL` (`SIZE_MAX * 2`, `SIZE_MAX/2+1 * 2`, `SIZE_MAX * SIZE_MAX`)
- Comprobar que **todo** el bloque está a 0, no solo el principio

> [!example]- main_ft_calloc.c
> ```c
> #include <stdint.h>
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Comprueba que los n bytes están a 0, no solo el principio */
> static int	all_zero(unsigned char *p, size_t n)
> {
> 	size_t	i;
>
> 	i = 0;
> 	while (i < n)
> 	{
> 		if (p[i] != 0)
> 			return (0);
> 		i++;
> 	}
> 	return (1);
> }
>
> int	main(void)
> {
> 	int		*nums;
> 	char	*p;
>
> 	printf("--- happy path ---\n");
> 	nums = ft_calloc(100, sizeof(int));
> 	check(nums != NULL, "ft_calloc(100, sizeof(int)) no es NULL");
> 	check(nums && all_zero((unsigned char *)nums, 100 * sizeof(int)),
> 		"los 400 bytes están a 0");
> 	free(nums);
> 	printf("--- edge cases ---\n");
> 	p = ft_calloc(0, 0);
> 	check(p != NULL,
> 		"ft_calloc(0, 0) devuelve un puntero que se puede liberar");
> 	free(p);
> 	p = ft_calloc(0, 10);
> 	check(p != NULL,
> 		"ft_calloc(0, 10) devuelve un puntero que se puede liberar");
> 	free(p);
> 	p = ft_calloc(SIZE_MAX, 2);
> 	check(p == NULL, "overflow: ft_calloc(SIZE_MAX, 2) -> NULL");
> 	free(p);
> 	p = ft_calloc(SIZE_MAX / 2 + 1, 2);
> 	check(p == NULL, "overflow: ft_calloc(SIZE_MAX / 2 + 1, 2) -> NULL");
> 	free(p);
> 	p = ft_calloc(SIZE_MAX, SIZE_MAX);
> 	check(p == NULL, "overflow: ft_calloc(SIZE_MAX, SIZE_MAX) -> NULL");
> 	free(p);
> 	printf("\nft_calloc: %d KO (pásalo también por valgrind)\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] ft_calloc(100, sizeof(int)) no es NULL
> [OK] los 400 bytes están a 0
> --- edge cases ---
> [OK] ft_calloc(0, 0) devuelve un puntero que se puede liberar
> [OK] ft_calloc(0, 10) devuelve un puntero que se puede liberar
> [OK] overflow: ft_calloc(SIZE_MAX, 2) -> NULL
> [OK] overflow: ft_calloc(SIZE_MAX / 2 + 1, 2) -> NULL
> [OK] overflow: ft_calloc(SIZE_MAX, SIZE_MAX) -> NULL
>
> ft_calloc: 0 KO (pásalo también por valgrind)
> ```

### ft_strdup

Nota: [[ft_strdup]]

**Happy path**
- Copia idéntica en memoria nueva

**Edge cases**
- Cadena vacía → `""` reservada (1 byte)
- El puntero devuelto **no es** el original
- Modificar la copia no cambia el original
- Reserva exacta `len + 1` (lo detecta valgrind si te quedas corto)

> [!example]- main_ft_strdup.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	char	original[5];
> 	char	*copy;
>
> 	strcpy(original, "hola");
> 	printf("--- happy path ---\n");
> 	copy = ft_strdup(original);
> 	printf("     copia: \"%s\"\n", copy);
> 	check(copy && strcmp(copy, "hola") == 0, "la copia es \"hola\"");
> 	printf("--- edge cases ---\n");
> 	check(copy != original, "el puntero devuelto no es el original");
> 	if (copy)
> 		copy[0] = 'X';
> 	check(strcmp(original, "hola") == 0,
> 		"cambiar la copia no cambia el original");
> 	free(copy);
> 	copy = ft_strdup("");
> 	check(copy && copy[0] == '\0', "ft_strdup(\"\") -> \"\" reservada");
> 	free(copy);
> 	printf("\nft_strdup: %d KO (valgrind detecta si reservas menos"
> 		" de len + 1)\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
>      copia: "hola"
> [OK] la copia es "hola"
> --- edge cases ---
> [OK] el puntero devuelto no es el original
> [OK] cambiar la copia no cambia el original
> [OK] ft_strdup("") -> "" reservada
>
> ft_strdup: 0 KO (valgrind detecta si reservas menos de len + 1)
> ```

---

## Parte 2 — Funciones adicionales

### ft_substr

Nota: [[ft_substr]]

**Happy path**
- `("hola mundo", 5, 5)` → `"mundo"`

**Edge cases**
- `len` mayor que lo que queda → recorta
- `start == strlen(s)` → `""`
- `start` fuera de la cadena → `""` (reservada, no `NULL`)
- `len = 0` → `""`
- `s` vacío
- **`start + len` desborda** (`len = SIZE_MAX`)
- La reserva debe ser del tamaño del resultado, no de `len`

> [!example]- main_ft_substr.c
> ```c
> #include <stdint.h>
> #include <stdio.h>
> #include <stdlib.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	test(char *label, const char *s, unsigned int start, size_t len,
> 		const char *expected)
> {
> 	char	*ret;
> 	int		ok;
>
> 	ret = ft_substr(s, start, len);
> 	ok = (ret != NULL && strcmp(ret, expected) == 0);
> 	printf("[%s] %-34s ft: \"%s\"  esperado: \"%s\"\n",
> 		ok ? "OK" : "KO", label, ret ? ret : "(NULL)", expected);
> 	if (!ok)
> 		g_ko++;
> 	free(ret);
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("(\"hola mundo\", 5, 5)", "hola mundo", 5, 5, "mundo");
> 	test("(\"hola mundo\", 0, 4)", "hola mundo", 0, 4, "hola");
> 	printf("--- edge cases ---\n");
> 	test("len más grande que lo que queda", "hola mundo", 5, 100, "mundo");
> 	test("start == strlen(s)", "hola", 4, 3, "");
> 	test("start fuera de la cadena", "hola", 100, 3, "");
> 	test("len = 0", "hola", 1, 0, "");
> 	test("s vacío", "", 0, 5, "");
> 	test("len = SIZE_MAX (start + len desborda)", "hola mundo", 5, SIZE_MAX,
> 		"mundo");
> 	printf("\nft_substr: %d KO (valgrind: la reserva debe ser la del resultado,"
> 		" no la de len)\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] ("hola mundo", 5, 5)               ft: "mundo"  esperado: "mundo"
> [OK] ("hola mundo", 0, 4)               ft: "hola"  esperado: "hola"
> --- edge cases ---
> [OK] len más grande que lo que queda   ft: "mundo"  esperado: "mundo"
> [OK] start == strlen(s)                 ft: ""  esperado: ""
> [OK] start fuera de la cadena           ft: ""  esperado: ""
> [OK] len = 0                            ft: ""  esperado: ""
> [OK] s vacío                           ft: ""  esperado: ""
> [OK] len = SIZE_MAX (start + len desborda) ft: "mundo"  esperado: "mundo"
>
> ft_substr: 0 KO (valgrind: la reserva debe ser la del resultado, no la de len)
> ```

### ft_strjoin

Nota: [[ft_strjoin]]

**Happy path**
- `("hola ", "mundo")` → `"hola mundo"`

**Edge cases**
- Izquierda vacía, derecha vacía, ambas vacías
- El resultado es memoria nueva (no devuelve `s1` ni `s2`)

> [!example]- main_ft_strjoin.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	test(char *label, const char *s1, const char *s2,
> 		const char *expected)
> {
> 	char	*ret;
> 	int		ok;
>
> 	ret = ft_strjoin(s1, s2);
> 	ok = (ret != NULL && ret != s1 && ret != s2
> 			&& strcmp(ret, expected) == 0);
> 	printf("[%s] %-26s ft: \"%s\"  esperado: \"%s\"\n",
> 		ok ? "OK" : "KO", label, ret ? ret : "(NULL)", expected);
> 	if (!ok)
> 		g_ko++;
> 	free(ret);
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("(\"hola \", \"mundo\")", "hola ", "mundo", "hola mundo");
> 	printf("--- edge cases ---\n");
> 	test("izquierda vacía", "", "mundo", "mundo");
> 	test("derecha vacía", "hola", "", "hola");
> 	test("las dos vacías", "", "", "");
> 	printf("\nft_strjoin: %d KO (cada caso comprueba también que el resultado"
> 		" es memoria nueva)\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] ("hola ", "mundo")         ft: "hola mundo"  esperado: "hola mundo"
> --- edge cases ---
> [OK] izquierda vacía           ft: "mundo"  esperado: "mundo"
> [OK] derecha vacía             ft: "hola"  esperado: "hola"
> [OK] las dos vacías            ft: ""  esperado: ""
>
> ft_strjoin: 0 KO (cada caso comprueba también que el resultado es memoria nueva)
> ```

### ft_strtrim

Nota: [[ft_strtrim]]

**Happy path**
- `("  hola  ", " ")` → `"hola"`

**Edge cases**
- Solo izquierda / solo derecha
- Los caracteres del medio se quedan
- Todo está en `set` → `""`
- `set` vacío → copia
- `s` vacío
- **Trampa**: la última letra de la palabra también está en `set` (`"ab hola ba"`, `"ab "` → `"hol"`)

> [!example]- main_ft_strtrim.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	test(char *label, const char *s, const char *set,
> 		const char *expected)
> {
> 	char	*ret;
> 	int		ok;
>
> 	ret = ft_strtrim(s, set);
> 	ok = (ret != NULL && strcmp(ret, expected) == 0);
> 	printf("[%s] %-34s ft: \"%s\"  esperado: \"%s\"\n",
> 		ok ? "OK" : "KO", label, ret ? ret : "(NULL)", expected);
> 	if (!ok)
> 		g_ko++;
> 	free(ret);
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("(\"  hola  \", \" \")", "  hola  ", " ", "hola");
> 	test("(\"xxhola mundoxx\", \"x\")", "xxhola mundoxx", "x", "hola mundo");
> 	printf("--- edge cases ---\n");
> 	test("solo a la izquierda", "  hola", " ", "hola");
> 	test("solo a la derecha", "hola  ", " ", "hola");
> 	test("los del medio se quedan", " h o l a ", " ", "h o l a");
> 	test("todo está en set", "aaaa", "a", "");
> 	test("set vacío (copia)", "  hola  ", "", "  hola  ");
> 	test("s vacío", "", " ", "");
> 	test("última letra también en set", "ab hola ba", "ab ", "hol");
> 	printf("\nft_strtrim: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] ("  hola  ", " ")                  ft: "hola"  esperado: "hola"
> [OK] ("xxhola mundoxx", "x")            ft: "hola mundo"  esperado: "hola mundo"
> --- edge cases ---
> [OK] solo a la izquierda                ft: "hola"  esperado: "hola"
> [OK] solo a la derecha                  ft: "hola"  esperado: "hola"
> [OK] los del medio se quedan            ft: "h o l a"  esperado: "h o l a"
> [OK] todo está en set                  ft: ""  esperado: ""
> [OK] set vacío (copia)                 ft: "  hola  "  esperado: "  hola  "
> [OK] s vacío                           ft: ""  esperado: ""
> [OK] última letra también en set      ft: "hol"  esperado: "hol"
>
> ft_strtrim: 0 KO
> ```

### ft_split

Nota: [[ft_split]]

**Happy path**
- `("hola que tal", ' ')` → `{"hola", "que", "tal", NULL}`

**Edge cases**
- Separadores al principio, al final y repetidos
- Sin separador → una palabra
- Palabras de 1 carácter
- Solo separadores o cadena vacía → `{NULL}` (array reservado con un único `NULL`)
- `c = '\0'` → la cadena entera
- **Fallo de `malloc` a mitad**: liberar lo ya reservado y devolver `NULL` (ver [[#Fallo de malloc]])

> [!example]- main_ft_split.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	free_result(char **tab)
> {
> 	int	i;
>
> 	i = 0;
> 	while (tab && tab[i])
> 		free(tab[i++]);
> 	free(tab);
> }
>
> /* expected es un array de palabras que termina en NULL, como el resultado */
> static void	test(char *label, const char *s, char c, char **expected)
> {
> 	char	**ret;
> 	int		i;
> 	int		ok;
>
> 	ret = ft_split(s, c);
> 	ok = (ret != NULL);
> 	i = 0;
> 	while (ok && expected[i])
> 	{
> 		if (!ret[i] || strcmp(ret[i], expected[i]) != 0)
> 			ok = 0;
> 		i++;
> 	}
> 	if (ok && ret[i] != NULL)
> 		ok = 0;
> 	printf("[%s] %-32s ft: {", ok ? "OK" : "KO", label);
> 	i = 0;
> 	while (ret && ret[i])
> 		printf("\"%s\", ", ret[i++]);
> 	printf("NULL}\n");
> 	if (!ok)
> 		g_ko++;
> 	free_result(ret);
> }
>
> int	main(void)
> {
> 	char	*three[] = {"hola", "que", "tal", NULL};
> 	char	*one[] = {"hola", NULL};
> 	char	*short_words[] = {"a", "b", "c", NULL};
> 	char	*none[] = {NULL};
> 	char	*whole[] = {"hola que tal", NULL};
>
> 	printf("--- happy path ---\n");
> 	test("(\"hola que tal\", ' ')", "hola que tal", ' ', three);
> 	printf("--- edge cases ---\n");
> 	test("separadores al principio y final", "  hola que tal  ", ' ', three);
> 	test("separadores repetidos", "hola   que    tal", ' ', three);
> 	test("sin separador", "hola", ' ', one);
> 	test("palabras de 1 carácter", "a,b,,c", ',', short_words);
> 	test("solo separadores", "     ", ' ', none);
> 	test("cadena vacía", "", ' ', none);
> 	test("c = '\\0' (la cadena entera)", "hola que tal", '\0', whole);
> 	printf("\nft_split: %d KO (pásalo por valgrind: 0 leaks)\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] ("hola que tal", ' ')            ft: {"hola", "que", "tal", NULL}
> --- edge cases ---
> [OK] separadores al principio y final ft: {"hola", "que", "tal", NULL}
> [OK] separadores repetidos            ft: {"hola", "que", "tal", NULL}
> [OK] sin separador                    ft: {"hola", NULL}
> [OK] palabras de 1 carácter          ft: {"a", "b", "c", NULL}
> [OK] solo separadores                 ft: {NULL}
> [OK] cadena vacía                    ft: {NULL}
> [OK] c = '\0' (la cadena entera)      ft: {"hola que tal", NULL}
>
> ft_split: 0 KO (pásalo por valgrind: 0 leaks)
> ```

### ft_itoa

Nota: [[ft_itoa]]

**Happy path**
- `42` → `"42"`, `-42` → `"-42"`

**Edge cases**
- `0` → `"0"` (el bucle de dígitos no entra)
- Cambio de número de dígitos: `9`, `10`, `-10`, `100`
- `1000000000` (10 dígitos)
- `INT_MAX`
- `INT_MIN` → no se puede hacer `-n` en `int`

> [!example]- main_ft_itoa.c
> ```c
> #include <limits.h>
> #include <stdio.h>
> #include <stdlib.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Compara con lo que escribe sprintf, que hace lo mismo */
> static void	test(char *label, int n)
> {
> 	char	*ft;
> 	char	expected[20];
> 	int		ok;
>
> 	ft = ft_itoa(n);
> 	sprintf(expected, "%d", n);
> 	ok = (ft != NULL && strcmp(ft, expected) == 0);
> 	printf("[%s] %-14s ft: \"%s\"  esperado: \"%s\"\n",
> 		ok ? "OK" : "KO", label, ft ? ft : "(NULL)", expected);
> 	if (!ok)
> 		g_ko++;
> 	free(ft);
> }
>
> int	main(void)
> {
> 	printf("--- happy path ---\n");
> 	test("42", 42);
> 	test("-42", -42);
> 	printf("--- edge cases ---\n");
> 	test("0", 0);
> 	test("9", 9);
> 	test("10", 10);
> 	test("-10", -10);
> 	test("100", 100);
> 	test("-5", -5);
> 	test("1000000000", 1000000000);
> 	test("INT_MAX", INT_MAX);
> 	test("INT_MIN", INT_MIN);
> 	printf("\nft_itoa: %d KO (valgrind: la reserva justa de cada número)\n",
> 		g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] 42             ft: "42"  esperado: "42"
> [OK] -42            ft: "-42"  esperado: "-42"
> --- edge cases ---
> [OK] 0              ft: "0"  esperado: "0"
> [OK] 9              ft: "9"  esperado: "9"
> [OK] 10             ft: "10"  esperado: "10"
> [OK] -10            ft: "-10"  esperado: "-10"
> [OK] 100            ft: "100"  esperado: "100"
> [OK] -5             ft: "-5"  esperado: "-5"
> [OK] 1000000000     ft: "1000000000"  esperado: "1000000000"
> [OK] INT_MAX        ft: "2147483647"  esperado: "2147483647"
> [OK] INT_MIN        ft: "-2147483648"  esperado: "-2147483648"
>
> ft_itoa: 0 KO (valgrind: la reserva justa de cada número)
> ```

### ft_strmapi

Nota: [[ft_strmapi]]

**Happy path**
- Devuelve una cadena **nueva** con `f(i, s[i])`

**Edge cases**
- El índice `i` llega bien (`c + i` sobre `"aaaa"` → `"abcd"`)
- El original no cambia
- Cadena vacía → `""` reservada

> [!example]- main_ft_strmapi.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> static char	add_index(unsigned int i, char c)
> {
> 	return (c + i);
> }
>
> static char	to_upper(unsigned int i, char c)
> {
> 	(void)i;
> 	if (c >= 'a' && c <= 'z')
> 		return (c - 32);
> 	return (c);
> }
>
> int	main(void)
> {
> 	char	original[5];
> 	char	*ret;
>
> 	strcpy(original, "aaaa");
> 	printf("--- happy path ---\n");
> 	ret = ft_strmapi("hola", to_upper);
> 	printf("     ft_strmapi(\"hola\", to_upper) = \"%s\"\n", ret);
> 	check(ret && strcmp(ret, "HOLA") == 0, "devuelve \"HOLA\"");
> 	free(ret);
> 	printf("--- edge cases ---\n");
> 	ret = ft_strmapi(original, add_index);
> 	printf("     ft_strmapi(\"aaaa\", add_index) = \"%s\"\n", ret);
> 	check(ret && strcmp(ret, "abcd") == 0, "el índice i llega bien (\"abcd\")");
> 	check(ret != original, "es una cadena nueva");
> 	check(strcmp(original, "aaaa") == 0, "el original no cambia");
> 	free(ret);
> 	ret = ft_strmapi("", add_index);
> 	check(ret && ret[0] == '\0', "cadena vacía -> \"\" reservada");
> 	free(ret);
> 	printf("\nft_strmapi: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
>      ft_strmapi("hola", to_upper) = "HOLA"
> [OK] devuelve "HOLA"
> --- edge cases ---
>      ft_strmapi("aaaa", add_index) = "abcd"
> [OK] el índice i llega bien ("abcd")
> [OK] es una cadena nueva
> [OK] el original no cambia
> [OK] cadena vacía -> "" reservada
>
> ft_strmapi: 0 KO
> ```

### ft_striteri

Nota: [[ft_striteri]]

**Happy path**
- Modifica **in situ** llamando a `f(i, &s[i])`

**Edge cases**
- Cadena vacía: no llama a `f`
- El puntero que recibe `f` es `&s[i]` real, no una copia: por eso los cambios se ven en la cadena
- `f` se llama una vez por carácter

> [!example]- main_ft_striteri.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include "libft.h"
>
> static int	g_ko = 0;
> static int	g_calls = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Recibe un puntero al carácter: así puede modificarlo en la cadena */
> static void	add_index(unsigned int i, char *c)
> {
> 	*c = *c + i;
> 	g_calls++;
> }
>
> int	main(void)
> {
> 	char	s[5];
> 	char	empty[1];
>
> 	strcpy(s, "aaaa");
> 	printf("--- happy path ---\n");
> 	ft_striteri(s, add_index);
> 	printf("     \"aaaa\" después de ft_striteri: \"%s\"\n", s);
> 	check(strcmp(s, "abcd") == 0, "modifica la propia cadena (\"abcd\")");
> 	check(g_calls == 4, "llama a f una vez por carácter (4)");
> 	printf("--- edge cases ---\n");
> 	g_calls = 0;
> 	empty[0] = '\0';
> 	ft_striteri(empty, add_index);
> 	check(g_calls == 0, "cadena vacía: no llama a f");
> 	printf("\nft_striteri: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
>      "aaaa" después de ft_striteri: "abcd"
> [OK] modifica la propia cadena ("abcd")
> [OK] llama a f una vez por carácter (4)
> --- edge cases ---
> [OK] cadena vacía: no llama a f
>
> ft_striteri: 0 KO
> ```

### ft_putchar_fd

Nota: [[ft_putchar_fd]]

**Happy path**
- Escribe exactamente 1 byte en `fd`

**Edge cases**
- `'\n'`
- `'\0'`: también es un carácter y hay que escribirlo (1 byte)
- Byte > 127
- `fd = -1`: no debe colgarse ni petar (`write` falla y ya está)

> [!example]- main_ft_putchar_fd.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include <unistd.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Escribe en un pipe en vez de en la pantalla y lee lo que llegó */
> static void	test(char *label, char c, const char *expected, int n)
> {
> 	int		fds[2];
> 	char	buf[10];
> 	int		bytes;
> 	int		ok;
>
> 	pipe(fds);
> 	ft_putchar_fd(c, fds[1]);
> 	close(fds[1]);
> 	bytes = read(fds[0], buf, sizeof(buf));
> 	close(fds[0]);
> 	ok = (bytes == n && memcmp(buf, expected, n) == 0);
> 	printf("[%s] %-20s bytes escritos: %d (esperado %d)\n",
> 		ok ? "OK" : "KO", label, bytes, n);
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- demo en pantalla ---\n");
> 	ft_putchar_fd('4', 1);
> 	ft_putchar_fd('2', 1);
> 	ft_putchar_fd('\n', 1);
> 	printf("--- happy path ---\n");
> 	test("'a'", 'a', "a", 1);
> 	printf("--- edge cases ---\n");
> 	test("'\\n'", '\n', "\n", 1);
> 	test("'\\0' (también es 1 byte)", '\0', "\0", 1);
> 	test("byte 0xE9 (> 127)", (char)0xe9, "\xe9", 1);
> 	ft_putchar_fd('a', -1);
> 	printf("[OK] fd = -1: no se cuelga ni peta\n");
> 	printf("\nft_putchar_fd: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- demo en pantalla ---
> 42
> --- happy path ---
> [OK] 'a'                  bytes escritos: 1 (esperado 1)
> --- edge cases ---
> [OK] '\n'                 bytes escritos: 1 (esperado 1)
> [OK] '\0' (también es 1 byte) bytes escritos: 1 (esperado 1)
> [OK] byte 0xE9 (> 127)    bytes escritos: 1 (esperado 1)
> [OK] fd = -1: no se cuelga ni peta
>
> ft_putchar_fd: 0 KO
> ```


### ft_putstr_fd

Nota: [[ft_putstr_fd]]

**Happy path**
- Escribe la cadena sin `'\n'`

**Edge cases**
- Cadena vacía → no escribe nada
- Cadena con `'\n'` dentro
- Para en `'\0'`

> [!example]- main_ft_putstr_fd.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include <unistd.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Escribe en un pipe en vez de en la pantalla y lee lo que llegó */
> static void	test(char *label, char *s, const char *expected)
> {
> 	int		fds[2];
> 	char	buf[50];
> 	int		bytes;
> 	int		ok;
>
> 	pipe(fds);
> 	ft_putstr_fd(s, fds[1]);
> 	close(fds[1]);
> 	bytes = read(fds[0], buf, sizeof(buf));
> 	close(fds[0]);
> 	ok = (bytes == (int)strlen(expected)
> 			&& memcmp(buf, expected, bytes) == 0);
> 	printf("[%s] %-26s bytes escritos: %d (esperado %d)\n",
> 		ok ? "OK" : "KO", label, bytes, (int)strlen(expected));
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- demo en pantalla ---\n");
> 	ft_putstr_fd("hola por la salida estándar (fd 1)\n", 1);
> 	ft_putstr_fd("hola por la salida de error (fd 2)\n", 2);
> 	printf("--- happy path ---\n");
> 	test("\"hola\" (sin '\\n')", "hola", "hola");
> 	printf("--- edge cases ---\n");
> 	test("\"\" (no escribe nada)", "", "");
> 	test("\"a\\nb\" (con '\\n' dentro)", "a\nb", "a\nb");
> 	test("\"ab\\0cd\" (para en el \\0)", "ab\0cd", "ab");
> 	printf("\nft_putstr_fd: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- demo en pantalla ---
> hola por la salida estándar (fd 1)
> hola por la salida de error (fd 2)
> --- happy path ---
> [OK] "hola" (sin '\n')          bytes escritos: 4 (esperado 4)
> --- edge cases ---
> [OK] "" (no escribe nada)       bytes escritos: 0 (esperado 0)
> [OK] "a\nb" (con '\n' dentro)   bytes escritos: 3 (esperado 3)
> [OK] "ab\0cd" (para en el \0)   bytes escritos: 2 (esperado 2)
>
> ft_putstr_fd: 0 KO
> ```

> [!tip] La línea de la salida de error (fd 2) sale por la terminal igual que la de fd 1. Si ejecutas `./t 2>/dev/null`, desaparece: así enseñas que de verdad va por otro fd.

### ft_putendl_fd

Nota: [[ft_putendl_fd]]

**Happy path**
- Escribe la cadena **y** un `'\n'`

**Edge cases**
- Cadena vacía → solo `"\n"`
- Cadena que ya acaba en `'\n'` → dos saltos

> [!example]- main_ft_putendl_fd.c
> ```c
> #include <stdio.h>
> #include <string.h>
> #include <unistd.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Escribe en un pipe en vez de en la pantalla y lee lo que llegó */
> static void	test(char *label, char *s, const char *expected)
> {
> 	int		fds[2];
> 	char	buf[50];
> 	int		bytes;
> 	int		ok;
>
> 	pipe(fds);
> 	ft_putendl_fd(s, fds[1]);
> 	close(fds[1]);
> 	bytes = read(fds[0], buf, sizeof(buf));
> 	close(fds[0]);
> 	ok = (bytes == (int)strlen(expected)
> 			&& memcmp(buf, expected, bytes) == 0);
> 	printf("[%s] %-26s bytes escritos: %d (esperado %d)\n",
> 		ok ? "OK" : "KO", label, bytes, (int)strlen(expected));
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- demo en pantalla ---\n");
> 	ft_putendl_fd("hola por la salida estándar (fd 1)", 1);
> 	ft_putendl_fd("hola por la salida de error (fd 2)", 2);
> 	printf("--- happy path ---\n");
> 	test("\"hola\" (añade el '\\n')", "hola", "hola\n");
> 	printf("--- edge cases ---\n");
> 	test("\"\" (solo el '\\n')", "", "\n");
> 	test("\"hola\\n\" (dos saltos)", "hola\n", "hola\n\n");
> 	printf("\nft_putendl_fd: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- demo en pantalla ---
> hola por la salida estándar (fd 1)
> hola por la salida de error (fd 2)
> --- happy path ---
> [OK] "hola" (añade el '\n')    bytes escritos: 5 (esperado 5)
> --- edge cases ---
> [OK] "" (solo el '\n')          bytes escritos: 1 (esperado 1)
> [OK] "hola\n" (dos saltos)      bytes escritos: 6 (esperado 6)
>
> ft_putendl_fd: 0 KO
> ```

> [!tip] Igual que en `ft_putstr_fd`: con `./t 2>/dev/null` desaparece la línea de fd 2.

### ft_putnbr_fd

Nota: [[ft_putnbr_fd]]

**Happy path**
- `42`, `-42`

**Edge cases**
- `0`
- Negativo de una cifra (`-5`)
- `10`, `100` (ceros)
- `INT_MAX`
- `INT_MIN` (no se puede hacer `-n`)

> [!example]- main_ft_putnbr_fd.c
> ```c
> #include <limits.h>
> #include <stdio.h>
> #include <string.h>
> #include <unistd.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> /* Escribe en un pipe y compara con lo que escribiría printf("%d") */
> static void	test(char *label, int n)
> {
> 	int		fds[2];
> 	char	buf[20];
> 	char	expected[20];
> 	int		bytes;
> 	int		ok;
>
> 	pipe(fds);
> 	ft_putnbr_fd(n, fds[1]);
> 	close(fds[1]);
> 	bytes = read(fds[0], buf, sizeof(buf) - 1);
> 	close(fds[0]);
> 	if (bytes < 0)
> 		bytes = 0;
> 	buf[bytes] = '\0';
> 	sprintf(expected, "%d", n);
> 	ok = (strcmp(buf, expected) == 0);
> 	printf("[%s] %-10s ft: \"%s\"  esperado: \"%s\"\n",
> 		ok ? "OK" : "KO", label, buf, expected);
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	printf("--- demo en pantalla ---\n");
> 	ft_putnbr_fd(INT_MIN, 1);
> 	write(1, "\n", 1);
> 	printf("--- happy path ---\n");
> 	test("42", 42);
> 	test("-42", -42);
> 	printf("--- edge cases ---\n");
> 	test("0", 0);
> 	test("-5", -5);
> 	test("10", 10);
> 	test("100", 100);
> 	test("INT_MAX", INT_MAX);
> 	test("INT_MIN", INT_MIN);
> 	printf("\nft_putnbr_fd: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- demo en pantalla ---
> -2147483648
> --- happy path ---
> [OK] 42         ft: "42"  esperado: "42"
> [OK] -42        ft: "-42"  esperado: "-42"
> --- edge cases ---
> [OK] 0          ft: "0"  esperado: "0"
> [OK] -5         ft: "-5"  esperado: "-5"
> [OK] 10         ft: "10"  esperado: "10"
> [OK] 100        ft: "100"  esperado: "100"
> [OK] INT_MAX    ft: "2147483647"  esperado: "2147483647"
> [OK] INT_MIN    ft: "-2147483648"  esperado: "-2147483648"
>
> ft_putnbr_fd: 0 KO
> ```

---

## Parte 3 — Listas

> [!info] Nodos hechos a mano
> Estos `main` no usan `ft_lstnew` ni `ft_lstadd_*`: crean los nodos con `malloc` en `new_node()` (y el de `ft_lstmap` los cuenta con `list_len()`, no con `ft_lstsize`). Así, si falla `ft_lstnew`, no fallan también los tests de `ft_lstsize` o `ft_lstlast`, y en la defensa sabes cuál es la función rota.

### ft_lstnew

Nota: [[ft_lstnew]]

**Happy path**
- `content` guardado y `next == NULL`

**Edge cases**
- `content = NULL` es válido

> [!example]- main_ft_lstnew.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> int	main(void)
> {
> 	t_list	*n;
> 	int		x;
>
> 	x = 42;
> 	printf("--- happy path ---\n");
> 	n = ft_lstnew(&x);
> 	check(n != NULL, "devuelve un nodo");
> 	check(n && n->content == &x, "content es el puntero que le pasamos");
> 	check(n && *(int *)n->content == 42, "*(int *)content vale 42");
> 	check(n && n->next == NULL, "next es NULL");
> 	free(n);
> 	printf("--- edge cases ---\n");
> 	n = ft_lstnew(NULL);
> 	check(n != NULL && n->content == NULL, "content = NULL es válido");
> 	free(n);
> 	printf("\nft_lstnew: %d KO (valgrind: 0 leaks)\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] devuelve un nodo
> [OK] content es el puntero que le pasamos
> [OK] *(int *)content vale 42
> [OK] next es NULL
> --- edge cases ---
> [OK] content = NULL es válido
>
> ft_lstnew: 0 KO (valgrind: 0 leaks)
> ```

### ft_lstadd_front

Nota: [[ft_lstadd_front]]

**Happy path**
- El nuevo nodo pasa a ser la cabeza

**Edge cases**
- Lista vacía (`*lst == NULL`)
- El antiguo primero queda detrás

> [!example]- main_ft_lstadd_front.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Crea el nodo a mano para no depender de ft_lstnew */
> static t_list	*new_node(void *content)
> {
> 	t_list	*n;
>
> 	n = malloc(sizeof(t_list));
> 	n->content = content;
> 	n->next = NULL;
> 	return (n);
> }
>
> static void	free_list(t_list *lst)
> {
> 	t_list	*next_node;
>
> 	while (lst)
> 	{
> 		next_node = lst->next;
> 		free(lst);
> 		lst = next_node;
> 	}
> }
>
> int	main(void)
> {
> 	t_list	*list;
> 	t_list	*a;
> 	t_list	*b;
>
> 	a = new_node("a");
> 	b = new_node("b");
> 	printf("--- edge cases ---\n");
> 	list = NULL;
> 	ft_lstadd_front(&list, a);
> 	check(list == a, "lista vacía: el nuevo pasa a ser la cabeza");
> 	check(a->next == NULL, "y su next sigue siendo NULL");
> 	printf("--- happy path ---\n");
> 	ft_lstadd_front(&list, b);
> 	check(list == b, "el nuevo nodo es la cabeza");
> 	check(b->next == a, "el antiguo primero queda detrás");
> 	check(a->next == NULL, "la lista sigue terminando en NULL");
> 	free_list(list);
> 	printf("\nft_lstadd_front: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- edge cases ---
> [OK] lista vacía: el nuevo pasa a ser la cabeza
> [OK] y su next sigue siendo NULL
> --- happy path ---
> [OK] el nuevo nodo es la cabeza
> [OK] el antiguo primero queda detrás
> [OK] la lista sigue terminando en NULL
>
> ft_lstadd_front: 0 KO
> ```

### ft_lstsize

Nota: [[ft_lstsize]]

**Happy path**
- Cuenta los nodos

**Edge cases**
- `NULL` → 0
- 1 nodo
- Desde un nodo intermedio

> [!example]- main_ft_lstsize.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Crea el nodo a mano para no depender de ft_lstnew */
> static t_list	*new_node(void *content)
> {
> 	t_list	*n;
>
> 	n = malloc(sizeof(t_list));
> 	n->content = content;
> 	n->next = NULL;
> 	return (n);
> }
>
> static void	free_list(t_list *lst)
> {
> 	t_list	*next_node;
>
> 	while (lst)
> 	{
> 		next_node = lst->next;
> 		free(lst);
> 		lst = next_node;
> 	}
> }
>
> int	main(void)
> {
> 	t_list	*list;
>
> 	list = new_node("a");
> 	list->next = new_node("b");
> 	list->next->next = new_node("c");
> 	printf("--- happy path ---\n");
> 	printf("     ft_lstsize(a -> b -> c) = %u\n", ft_lstsize(list));
> 	check(ft_lstsize(list) == 3, "3 nodos -> 3");
> 	printf("--- edge cases ---\n");
> 	check(ft_lstsize(NULL) == 0, "NULL -> 0");
> 	check(ft_lstsize(list->next->next) == 1, "1 nodo -> 1");
> 	check(ft_lstsize(list->next) == 2, "desde el nodo del medio -> 2");
> 	free_list(list);
> 	printf("\nft_lstsize: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
>      ft_lstsize(a -> b -> c) = 3
> [OK] 3 nodos -> 3
> --- edge cases ---
> [OK] NULL -> 0
> [OK] 1 nodo -> 1
> [OK] desde el nodo del medio -> 2
>
> ft_lstsize: 0 KO
> ```

### ft_lstlast

Nota: [[ft_lstlast]]

**Happy path**
- Devuelve el último nodo

**Edge cases**
- `NULL` → `NULL`
- Lista de un solo nodo → ese nodo

> [!example]- main_ft_lstlast.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Crea el nodo a mano para no depender de ft_lstnew */
> static t_list	*new_node(void *content)
> {
> 	t_list	*n;
>
> 	n = malloc(sizeof(t_list));
> 	n->content = content;
> 	n->next = NULL;
> 	return (n);
> }
>
> static void	free_list(t_list *lst)
> {
> 	t_list	*next_node;
>
> 	while (lst)
> 	{
> 		next_node = lst->next;
> 		free(lst);
> 		lst = next_node;
> 	}
> }
>
> int	main(void)
> {
> 	t_list	*list;
> 	t_list	*last;
>
> 	list = new_node("a");
> 	list->next = new_node("b");
> 	last = new_node("c");
> 	list->next->next = last;
> 	printf("--- happy path ---\n");
> 	printf("     ft_lstlast(a -> b -> c)->content = \"%s\"\n",
> 		(char *)ft_lstlast(list)->content);
> 	check(ft_lstlast(list) == last, "devuelve el último nodo (c)");
> 	printf("--- edge cases ---\n");
> 	check(ft_lstlast(NULL) == NULL, "NULL -> NULL");
> 	check(ft_lstlast(last) == last, "un solo nodo -> ese nodo");
> 	free_list(list);
> 	printf("\nft_lstlast: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
>      ft_lstlast(a -> b -> c)->content = "c"
> [OK] devuelve el último nodo (c)
> --- edge cases ---
> [OK] NULL -> NULL
> [OK] un solo nodo -> ese nodo
>
> ft_lstlast: 0 KO
> ```

### ft_lstadd_back

Nota: [[ft_lstadd_back]]

**Happy path**
- Engancha el nodo al final

**Edge cases**
- Lista vacía: `*lst` pasa a ser el nuevo nodo
- Añadir una cadena entera (no solo un nodo suelto)

> [!example]- main_ft_lstadd_back.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Crea el nodo a mano para no depender de ft_lstnew */
> static t_list	*new_node(void *content)
> {
> 	t_list	*n;
>
> 	n = malloc(sizeof(t_list));
> 	n->content = content;
> 	n->next = NULL;
> 	return (n);
> }
>
> static void	free_list(t_list *lst)
> {
> 	t_list	*next_node;
>
> 	while (lst)
> 	{
> 		next_node = lst->next;
> 		free(lst);
> 		lst = next_node;
> 	}
> }
>
> int	main(void)
> {
> 	t_list	*list;
> 	t_list	*a;
> 	t_list	*b;
> 	t_list	*c;
>
> 	a = new_node("a");
> 	b = new_node("b");
> 	c = new_node("c");
> 	c->next = new_node("d");
> 	printf("--- edge cases ---\n");
> 	list = NULL;
> 	ft_lstadd_back(&list, a);
> 	check(list == a, "lista vacía: *lst pasa a ser el nuevo nodo");
> 	printf("--- happy path ---\n");
> 	ft_lstadd_back(&list, b);
> 	check(a->next == b, "engancha el nodo al final (a -> b)");
> 	check(b->next == NULL, "la lista termina en NULL");
> 	printf("--- edge cases ---\n");
> 	ft_lstadd_back(&list, c);
> 	check(b->next == c && c->next && c->next->next == NULL,
> 		"añadir una cadena entera (a -> b -> c -> d)");
> 	check(list == a, "la cabeza no cambia");
> 	free_list(list);
> 	printf("\nft_lstadd_back: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- edge cases ---
> [OK] lista vacía: *lst pasa a ser el nuevo nodo
> --- happy path ---
> [OK] engancha el nodo al final (a -> b)
> [OK] la lista termina en NULL
> --- edge cases ---
> [OK] añadir una cadena entera (a -> b -> c -> d)
> [OK] la cabeza no cambia
>
> ft_lstadd_back: 0 KO
> ```

### ft_lstdelone

Nota: [[ft_lstdelone]]

**Happy path**
- Llama a `del(content)` **una vez** y libera el nodo

**Edge cases**
- **No** toca `next` ni libera el siguiente nodo
- Sin fugas (valgrind)

> [!example]- main_ft_lstdelone.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Crea el nodo a mano para no depender de ft_lstnew */
> static t_list	*new_node(void *content)
> {
> 	t_list	*n;
>
> 	n = malloc(sizeof(t_list));
> 	n->content = content;
> 	n->next = NULL;
> 	return (n);
> }
>
> static int	g_calls = 0;
> static void	*g_deleted = NULL;
>
> /* Apunta qué content se ha borrado y cuántas veces */
> static void	del(void *content)
> {
> 	g_calls++;
> 	g_deleted = content;
> 	free(content);
> }
>
> static char	*new_str(char *s)
> {
> 	char	*copy;
> 	int		i;
>
> 	copy = malloc(10);
> 	i = 0;
> 	while (s[i])
> 	{
> 		copy[i] = s[i];
> 		i++;
> 	}
> 	copy[i] = '\0';
> 	return (copy);
> }
>
> int	main(void)
> {
> 	t_list	*a;
> 	t_list	*b;
> 	void	*content_a;
>
> 	a = new_node(new_str("a"));
> 	b = new_node(new_str("b"));
> 	a->next = b;
> 	content_a = a->content;
> 	printf("--- happy path ---\n");
> 	ft_lstdelone(a, del);
> 	check(g_calls == 1, "llama a del una sola vez");
> 	check(g_deleted == content_a, "con el content del nodo");
> 	printf("--- edge cases ---\n");
> 	check(((char *)b->content)[0] == 'b' && b->next == NULL,
> 		"el nodo siguiente sigue vivo e intacto");
> 	free(b->content);
> 	free(b);
> 	printf("\nft_lstdelone: %d KO (valgrind: 0 leaks y ningún invalid free)\n",
> 		g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] llama a del una sola vez
> [OK] con el content del nodo
> --- edge cases ---
> [OK] el nodo siguiente sigue vivo e intacto
>
> ft_lstdelone: 0 KO (valgrind: 0 leaks y ningún invalid free)
> ```

### ft_lstclear

Nota: [[ft_lstclear]]

**Happy path**
- Libera todos los nodos con `del` y deja `*lst = NULL`

**Edge cases**
- `del` se llama una vez **por nodo**
- Lista vacía (`*lst == NULL`): no hace nada

> [!example]- main_ft_lstclear.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Crea el nodo a mano para no depender de ft_lstnew */
> static t_list	*new_node(void *content)
> {
> 	t_list	*n;
>
> 	n = malloc(sizeof(t_list));
> 	n->content = content;
> 	n->next = NULL;
> 	return (n);
> }
>
> static int	g_calls = 0;
>
> static void	del(void *content)
> {
> 	g_calls++;
> 	free(content);
> }
>
> static void	*new_int(int value)
> {
> 	int	*p;
>
> 	p = malloc(sizeof(int));
> 	*p = value;
> 	return (p);
> }
>
> int	main(void)
> {
> 	t_list	*list;
>
> 	list = new_node(new_int(1));
> 	list->next = new_node(new_int(2));
> 	list->next->next = new_node(new_int(3));
> 	printf("--- happy path ---\n");
> 	ft_lstclear(&list, del);
> 	check(list == NULL, "deja *lst = NULL");
> 	check(g_calls == 3, "llama a del una vez por nodo (3)");
> 	printf("--- edge cases ---\n");
> 	g_calls = 0;
> 	list = NULL;
> 	ft_lstclear(&list, del);
> 	check(list == NULL && g_calls == 0, "lista vacía: no hace nada");
> 	printf("\nft_lstclear: %d KO (valgrind: 0 leaks)\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
> [OK] deja *lst = NULL
> [OK] llama a del una vez por nodo (3)
> --- edge cases ---
> [OK] lista vacía: no hace nada
>
> ft_lstclear: 0 KO (valgrind: 0 leaks)
> ```

### ft_lstiter

Nota: [[ft_lstiter]]

**Happy path**
- Aplica `f` al `content` de cada nodo, en orden

**Edge cases**
- Visita **todos** (incluido el último)
- `NULL`: no llama a `f`

> [!example]- main_ft_lstiter.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Crea el nodo a mano para no depender de ft_lstnew */
> static t_list	*new_node(void *content)
> {
> 	t_list	*n;
>
> 	n = malloc(sizeof(t_list));
> 	n->content = content;
> 	n->next = NULL;
> 	return (n);
> }
>
> static void	free_list(t_list *lst)
> {
> 	t_list	*next_node;
>
> 	while (lst)
> 	{
> 		next_node = lst->next;
> 		free(lst);
> 		lst = next_node;
> 	}
> }
>
> static int	g_calls = 0;
>
> static void	add_one(void *content)
> {
> 	*(int *)content += 1;
> 	g_calls++;
> }
>
> int	main(void)
> {
> 	int		v[3];
> 	t_list	*list;
>
> 	v[0] = 1;
> 	v[1] = 2;
> 	v[2] = 3;
> 	list = new_node(&v[0]);
> 	list->next = new_node(&v[1]);
> 	list->next->next = new_node(&v[2]);
> 	printf("--- happy path ---\n");
> 	ft_lstiter(list, add_one);
> 	printf("     después de ft_lstiter: %d -> %d -> %d\n", v[0], v[1], v[2]);
> 	check(v[0] == 2 && v[1] == 3, "aplica f a cada content (1,2 -> 2,3)");
> 	printf("--- edge cases ---\n");
> 	check(v[2] == 4, "también el último nodo (3 -> 4)");
> 	check(g_calls == 3, "llama a f exactamente 3 veces");
> 	g_calls = 0;
> 	ft_lstiter(NULL, add_one);
> 	check(g_calls == 0, "NULL: no llama a f");
> 	free_list(list);
> 	printf("\nft_lstiter: %d KO\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
>      después de ft_lstiter: 2 -> 3 -> 4
> [OK] aplica f a cada content (1,2 -> 2,3)
> --- edge cases ---
> [OK] también el último nodo (3 -> 4)
> [OK] llama a f exactamente 3 veces
> [OK] NULL: no llama a f
>
> ft_lstiter: 0 KO
> ```

### ft_lstmap

Nota: [[ft_lstmap]]

**Happy path**
- Lista **nueva** con `f(content)` en cada nodo

**Edge cases**
- Mismo tamaño y orden (cuenta los nodos con `list_len()` antes de leerlos: si tu `ft_lstmap` devuelve menos nodos, sale `[KO]` en vez de un segfault)
- Nodos y contenidos nuevos; la original intacta
- `NULL` → `NULL`
- **Fallo de `malloc`** al crear un nodo: `del` del contenido que ya devolvió `f`, limpiar lo creado y devolver `NULL` (ver [[#Fallo de malloc]])

> [!example]- main_ft_lstmap.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> static int	g_ko = 0;
>
> static void	check(int ok, char *label)
> {
> 	printf("[%s] %s\n", ok ? "OK" : "KO", label);
> 	if (!ok)
> 		g_ko++;
> }
>
> /* Crea el nodo a mano para no depender de ft_lstnew */
> static t_list	*new_node(void *content)
> {
> 	t_list	*n;
>
> 	n = malloc(sizeof(t_list));
> 	n->content = content;
> 	n->next = NULL;
> 	return (n);
> }
>
> static void	free_list(t_list *lst)
> {
> 	t_list	*next_node;
>
> 	while (lst)
> 	{
> 		next_node = lst->next;
> 		free(lst);
> 		lst = next_node;
> 	}
> }
>
> /* Cuenta los nodos a mano para no depender de ft_lstsize */
> static int	list_len(t_list *lst)
> {
> 	int	len;
>
> 	len = 0;
> 	while (lst)
> 	{
> 		len++;
> 		lst = lst->next;
> 	}
> 	return (len);
> }
>
> /* f devuelve un content nuevo (reservado), con el valor por 10 */
> static void	*times_ten(void *content)
> {
> 	int	*new_int;
>
> 	new_int = malloc(sizeof(int));
> 	if (!new_int)
> 		return (NULL);
> 	*new_int = *(int *)content * 10;
> 	return (new_int);
> }
>
> int	main(void)
> {
> 	int		v[3];
> 	int		len;
> 	t_list	*list;
> 	t_list	*new_list;
> 	t_list	*it;
>
> 	v[0] = 1;
> 	v[1] = 2;
> 	v[2] = 3;
> 	list = new_node(&v[0]);
> 	list->next = new_node(&v[1]);
> 	list->next->next = new_node(&v[2]);
> 	printf("--- happy path ---\n");
> 	new_list = ft_lstmap(list, times_ten, free);
> 	printf("     ft_lstmap(1 -> 2 -> 3, times_ten) = ");
> 	it = new_list;
> 	while (it)
> 	{
> 		printf("%d -> ", *(int *)it->content);
> 		it = it->next;
> 	}
> 	printf("NULL\n");
> 	len = list_len(new_list);
> 	check(len == 3 && *(int *)new_list->content == 10
> 		&& *(int *)new_list->next->content == 20
> 		&& *(int *)new_list->next->next->content == 30,
> 		"valores 10, 20, 30 en el mismo orden");
> 	printf("--- edge cases ---\n");
> 	check(len == 3, "mismo tamaño (3 nodos)");
> 	check(new_list && new_list != list && new_list->content != list->content,
> 		"nodos y contents nuevos");
> 	check(v[0] == 1 && v[1] == 2 && v[2] == 3, "la lista original no cambia");
> 	check(ft_lstmap(NULL, times_ten, free) == NULL, "NULL -> NULL");
> 	it = new_list;
> 	while (it)
> 	{
> 		free(it->content);
> 		it = it->next;
> 	}
> 	free_list(new_list);
> 	free_list(list);
> 	printf("\nft_lstmap: %d KO (valgrind: 0 leaks)\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> --- happy path ---
>      ft_lstmap(1 -> 2 -> 3, times_ten) = 10 -> 20 -> 30 -> NULL
> [OK] valores 10, 20, 30 en el mismo orden
> --- edge cases ---
> [OK] mismo tamaño (3 nodos)
> [OK] nodos y contents nuevos
> [OK] la lista original no cambia
> [OK] NULL -> NULL
>
> ft_lstmap: 0 KO (valgrind: 0 leaks)
> ```

---

## Fallo de malloc

Este caso no se puede enseñar con un `main` normal, pero pueden preguntártelo: **¿qué pasa si `malloc` devuelve `NULL` a mitad de `ft_split` o de `ft_lstmap`?** Tu función tiene que devolver `NULL` **y no dejar fugas**: en `ft_split`, liberar las palabras ya reservadas; en `ft_lstmap`, hacer `del` del contenido que ya devolvió `f` y limpiar la lista nueva.

Para probarlo se usa la opción del enlazador `-Wl,--wrap=malloc`: todas las llamadas a `malloc` **dentro de `libft.a`** pasan por `__wrap_malloc`, que puede hacer fallar la llamada número `n`. Solo funciona en Linux (el enlazador de macOS no tiene `--wrap`).

```bash
cc -Wall -Wextra -Werror main_malloc_fail.c -I ~/cursus/libft -L ~/cursus/libft -lft -Wl,--wrap=malloc -o t
valgrind --leak-check=full ./t               # todo [OK] y 0 fugas
```

> [!tip]
> Lo que de verdad importa aquí es **valgrind**: la función debe devolver `NULL` *y además* no dejar ninguna fuga. Ver [[Valgrind y sanitizers]].

> [!example]- main_malloc_fail.c
> ```c
> #include <stdio.h>
> #include <stdlib.h>
> #include "libft.h"
>
> /* Compilar con -Wl,--wrap=malloc: cada malloc de libft.a pasa por
>    __wrap_malloc, que hace fallar la llamada número g_fallar_en */
> void		*__real_malloc(size_t size);
>
> static int	g_fallar_en = -1;
> static int	g_cuenta = 0;
> static int	g_ko = 0;
>
> void	*__wrap_malloc(size_t size)
> {
> 	if (g_cuenta++ == g_fallar_en)
> 		return (NULL);
> 	return (__real_malloc(size));
> }
>
> static void	fallar_en(int n)
> {
> 	g_fallar_en = n;
> 	g_cuenta = 0;
> }
>
> static void	check(int ok, char *caso, int n)
> {
> 	printf("[%s] %s (falla el malloc nº %d)\n", ok ? "OK" : "KO", caso, n);
> 	if (!ok)
> 		g_ko++;
> }
>
> static void	*por_diez(void *content)
> {
> 	int	*nuevo;
>
> 	nuevo = __real_malloc(sizeof(int));
> 	*nuevo = *(int *)content * 10;
> 	return (nuevo);
> }
>
> int	main(void)
> {
> 	int		v[3];
> 	t_list	a;
> 	t_list	b;
> 	t_list	c;
> 	int		n;
>
> 	v[0] = 1;
> 	v[1] = 2;
> 	v[2] = 3;
> 	a.content = &v[0];
> 	a.next = &b;
> 	b.content = &v[1];
> 	b.next = &c;
> 	c.content = &v[2];
> 	c.next = NULL;
> 	n = 0;
> 	while (n < 4)
> 	{
> 		fallar_en(n);
> 		check(ft_split("aa bb cc", ' ') == NULL, "ft_split -> NULL", n);
> 		n++;
> 	}
> 	n = 0;
> 	while (n < 3)
> 	{
> 		fallar_en(n);
> 		check(ft_lstmap(&a, por_diez, free) == NULL, "ft_lstmap -> NULL", n);
> 		n++;
> 	}
> 	fallar_en(0);
> 	check(ft_itoa(42) == NULL, "ft_itoa -> NULL", 0);
> 	fallar_en(0);
> 	check(ft_strjoin("a", "b") == NULL, "ft_strjoin -> NULL", 0);
> 	fallar_en(0);
> 	check(ft_substr("hola", 0, 2) == NULL, "ft_substr -> NULL", 0);
> 	fallar_en(0);
> 	check(ft_strdup("hola") == NULL, "ft_strdup -> NULL", 0);
> 	printf("\nmalloc_fail: %d KO (y valgrind debe dar 0 leaks)\n", g_ko);
> 	return (g_ko != 0);
> }
> ```

> [!example]- Salida
> ```text
> [OK] ft_split -> NULL (falla el malloc nº 0)
> [OK] ft_split -> NULL (falla el malloc nº 1)
> [OK] ft_split -> NULL (falla el malloc nº 2)
> [OK] ft_split -> NULL (falla el malloc nº 3)
> [OK] ft_lstmap -> NULL (falla el malloc nº 0)
> [OK] ft_lstmap -> NULL (falla el malloc nº 1)
> [OK] ft_lstmap -> NULL (falla el malloc nº 2)
> [OK] ft_itoa -> NULL (falla el malloc nº 0)
> [OK] ft_strjoin -> NULL (falla el malloc nº 0)
> [OK] ft_substr -> NULL (falla el malloc nº 0)
> [OK] ft_strdup -> NULL (falla el malloc nº 0)
>
> malloc_fail: 0 KO (y valgrind debe dar 0 leaks)
> ```

---

## Relacionadas

[[libft - Índice]] · [[libft - Anexo comparativo]] · [[Valgrind y sanitizers]] · [[Depurar con gdb]] · [[Makefile y librerías estáticas]] · [[La Norma]] · [[Git para 42]]
