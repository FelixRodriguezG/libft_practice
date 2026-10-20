---
tags: [c, arrays, memoria, punteros]
---
# Arrays en C

← Inicio · C

> Un array es una **colección de elementos del mismo tipo** guardados en **posiciones de memoria contiguas** (uno detrás de otro), a los que se accede por su **índice**. Sirve para guardar «muchos de lo mismo» (notas, letras de una cadena, píxeles…) sin declarar una variable por cada uno.

| Término | Qué significa |
|---|---|
| **Elemento** | Cada una de las casillas del array (`arr[0]`, `arr[1]`…) |
| **Índice** | El número de la casilla. Empieza en **0** |
| **Contiguo** | Pegados en memoria, sin huecos entre un elemento y el siguiente |
| **`sizeof`** | Operador que da el tamaño en bytes de una variable o tipo (devuelve un `size_t`, ver [[Tipos enteros y conversiones]]) |
| **Comportamiento indefinido** (*undefined behavior*, UB) | Algo que el estándar de C no define: puede funcionar, crashear o fallar solo a veces |

## Declaración

```c
int	arr[4];
```

Reserva espacio para 4 `int` seguidos: `4 * sizeof(int)` bytes (16 bytes con `int` de 4 bytes). El tamaño tiene que ser una **constante** conocida al compilar.

```text
 índice     arr[0]      arr[1]      arr[2]      arr[3]
         +-----------+-----------+-----------+-----------+
         |    ???    |    ???    |    ???    |    ???    |
         +-----------+-----------+-----------+-----------+
dirección  0x1000      0x1004      0x1008      0x100C
           ↑ arr       (cada salto = sizeof(int) = 4 bytes)
```

> [!warning] Sin inicializar = basura
> Un array local (en el [[Segmentos de memoria en C|stack]]) **no se pone a cero solo**: contiene lo que hubiera antes en esa memoria. Los arrays globales y `static` sí empiezan a cero (van al segmento BSS).

## Inicialización

| Forma | Resultado |
|---|---|
| `int a[4] = {1, 2, 3, 4};` | `{1, 2, 3, 4}` |
| `int a[4] = {1, 2};` | `{1, 2, 0, 0}`: lo que falta se rellena con 0 |
| `int a[4] = {0};` | `{0, 0, 0, 0}`: truco para poner todo a cero |
| `int a[] = {7, 8, 9};` | El compilador deduce el tamaño: 3 |
| `char s[] = "hola";` | `{'h', 'o', 'l', 'a', '\0'}`: **5** bytes, incluye el `'\0'` |

> [!note] La Norma de 42
> La [[La Norma|Norma de 42]] **prohíbe declarar e inicializar en la misma línea** dentro de una función, así que en tus proyectos se declara arriba y se rellena después:
> ```c
> int	arr[4];
>
> ft_bzero(arr, sizeof(arr));
> arr[0] = 42;
> ```
> También prohíbe los **VLA** (arrays de longitud variable, `int arr[n];`). Si el tamaño se conoce en ejecución, usa [[ft_calloc]] o `malloc`.

## Acceso por índice

- Los índices van de **0 a n − 1**. En `int arr[4]`, el último es `arr[3]`.
- `arr[i]` es exactamente `*(arr + i)`: la dirección de inicio más `i` elementos (no bytes; el compilador multiplica por `sizeof(int)`).

```c
arr[0] = 10;          // primer elemento
arr[3] = 40;          // último elemento
arr[4] = 50;          // ❌ fuera de rango: comportamiento indefinido
```

> [!danger] C no comprueba los límites
> Escribir en `arr[4]` **no da error al compilar** y puede que tampoco al ejecutar: pisa la memoria de al lado (otra variable, la dirección de retorno…). Es la causa típica de bugs raros y segfaults. Para detectarlo compila con `-fsanitize=address -g` o pasa `valgrind` (ver [[Valgrind y sanitizers]]). Ojo: valgrind detecta bien los desbordamientos en el heap, pero casi nunca en arrays del stack; para esos usa `-fsanitize=address`.

## Tamaño con `sizeof`

```c
int		arr[4];
size_t	n;

n = sizeof(arr) / sizeof(arr[0]);   // 16 / 4 = 4 elementos
```

Esto **solo funciona donde el array está declarado**. Al pasarlo a una función, deja de ser un array (ver abajo).

## Arrays y punteros: parecidos, pero no iguales

Al usar un array en casi cualquier expresión, **se convierte en un puntero a su primer elemento** (*array decay*, «decaimiento»): `arr` vale `&arr[0]`. Las excepciones son `sizeof(arr)` y `&arr`, donde sigue siendo el array entero. Si los punteros aún te bailan, repasa [[Punteros en C]].

| | `int arr[4];` | `int *p;` |
|---|---|---|
| Qué es | 16 bytes de datos | 8 bytes con una dirección |
| `sizeof` | 16 (el array entero) | 8 (el puntero) |
| ¿Se puede reasignar? | ❌ `arr = otro;` no compila | ✅ `p = otro;` |
| `arr[i]` / `p[i]` | ✅ | ✅ (misma sintaxis) |

### Pasar un array a una función

Una función **nunca recibe el array**, recibe un puntero. Estas dos firmas son idénticas:

```c
void	print_all(int arr[], size_t n);
void	print_all(int *arr, size_t n);
```

Por eso hay que **pasar el tamaño aparte** (igual que [[ft_memset]], [[ft_memcpy]]… reciben `n`). Dentro de la función, `sizeof(arr)` vale 8 (el puntero), no el tamaño del array.

> [!tip] Consecuencia útil
> Como recibe la dirección, la función **modifica el array original** sin necesidad de `&`.

## Cadenas: arrays de `char`

Una cadena en C es un array de `char` que **termina en `'\0'`** (no confundir con `NULL`: ver [[Carácter nulo y puntero NULL]]). Hay dos formas de crearla y no son equivalentes:

```c
char	s1[] = "hola";   // array de 5 bytes en el stack: se puede modificar
char	*s2 = "hola";    // puntero a un literal de solo lectura
```

> [!note] Norma
> Estos ejemplos declaran e inicializan en la misma línea para que se lean mejor; norminette lo marcaría dentro de una función. En un proyecto, declara arriba y asigna después.

```c
s1[0] = 'H';   // ✅ "Hola"
s2[0] = 'H';   // ❌ segfault: el literal está en memoria de solo lectura
```

Un *literal de cadena* es el texto entre comillas que escribes en el código; se guarda en una zona de solo lectura del programa. Ver [[Segmentos de memoria en C]] y el aviso de [[ft_striteri]] en el [[libft - Anexo comparativo|anexo de libft]].

> [!warning] Error clásico: olvidar el `'\0'`
> Para guardar una cadena de longitud `n` necesitas **`n + 1`** bytes. Si reservas `ft_strlen(s)` en vez de `ft_strlen(s) + 1`, la copia no termina y funciones como [[ft_strlen]] siguen leyendo fuera.

## Arrays bidimensionales

```c
int	m[3][4];   // 3 filas × 4 columnas = 12 int seguidos
```

En memoria se guardan **fila tras fila** (*row-major*): `m[1][0]` va justo después de `m[0][3]`.

```text
m[0][0] m[0][1] m[0][2] m[0][3] | m[1][0] m[1][1] ... | m[2][0] ... m[2][3]
```

No confundir con un **array de punteros** como el que devuelve [[ft_split]] (`char **`): ahí cada fila es un `malloc` independiente, en sitios distintos de la memoria, y la lista termina en `NULL`.

## No se pueden copiar ni comparar con operadores

| Quiero… | ❌ No funciona | ✅ Usa |
|---|---|---|
| Copiar un array en otro | `a = b;` | [[ft_memcpy]] / [[ft_memmove]] |
| Comparar dos arrays | `a == b` (compara direcciones) | [[ft_memcmp]] |
| Ponerlo a cero | — | [[ft_bzero]] / [[ft_memset]] |

## Errores frecuentes

1. **Salirse del rango** (`arr[n]` en vez de `arr[n - 1]`), sobre todo en bucles con `<=`.
2. **Devolver un array local** desde una función: se destruye al salir y el puntero queda colgando. Reserva con `malloc` y devuelve eso.
   ```c
   char	*bad(void)
   {
   	char	buf[10];

   	return (buf);   // ❌ buf ya no existe al volver
   }
   ```
3. **Usar `sizeof` dentro de una función** para saber cuántos elementos tiene el array recibido (da el tamaño del puntero).
4. **Olvidar el `'\0'`** al reservar o copiar cadenas.

## Relacionadas

[[Punteros en C]] · [[Segmentos de memoria en C]] · [[Carácter nulo y puntero NULL]] · [[Tipos enteros y conversiones]] · [[Control de errores en C]] · [[Valgrind y sanitizers]] · [[La Norma]] · [[libft - Anexo comparativo]] · [[ft_calloc]] · [[ft_split]]

## Referencias

- [Array declaration — cppreference](https://en.cppreference.com/w/c/language/array) — declaración, conversión de array a puntero, arrays como parámetros.
- [Array initialization — cppreference](https://en.cppreference.com/w/c/language/array_initialization) — inicialización parcial con ceros y tamaño deducido.
- [String literals — cppreference](https://en.cppreference.com/w/c/language/string_literal) — modificar un literal es comportamiento indefinido.
- [Borrador del estándar C11 (N1570)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) — §6.5.2.1 (`E1[E2]` es `*((E1)+(E2))`), §6.3.2.1p3 (decay), §6.7.9 (inicialización).
- [Beej's Guide to C — Arrays](https://beej.us/guide/bgc/html/split/arrays.html) — explicación introductoria.
- La Norma v4 (`Normativa 42/es.norm-2.pdf`) — prohíbe los VLA y declarar e inicializar en la misma línea.
