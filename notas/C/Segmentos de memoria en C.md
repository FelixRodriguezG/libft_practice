---
tags: [c, memoria, punteros, sistemas]
aliases: ["Mapa de memoria", "Stack y heap"]
---
# Segmentos de memoria en C

← Inicio · C

> Cuando ejecutas un programa, el sistema le da un espacio de memoria propio dividido en **zonas (segmentos)**, cada una con un uso y unas reglas: el código va en una, las variables globales en otra, las locales en la pila (*stack*) y lo que pides con `malloc` en el montón (*heap*). Saber dónde vive cada variable explica cuánto dura, si se puede modificar y por qué a veces el programa crashea.

> [!summary] Resumen
> De la dirección más alta a la más baja:
> 1. **Argumentos y entorno** (`argc`, `argv`, `envp`): en lo más alto, justo encima de la pila.
> 2. **Stack (pila)**: variables locales y parámetros de cada función. Se reserva y libera sola al entrar y salir de la función. Crece hacia abajo.
> 3. **Heap (montón)**: memoria dinámica que pides con `malloc` y devuelves con `free`. Crece hacia arriba.
> 4. **BSS**: variables globales y `static` **sin inicializar** (o inicializadas a cero). Empiezan valiendo 0.
> 5. **Data**: variables globales y `static` **inicializadas** con un valor distinto de cero.
> 6. **Text y rodata**: el código máquina del programa y los datos de solo lectura, como los literales de cadena.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Proceso** | Un programa mientras se está ejecutando |
| **Memoria virtual** | Cada proceso ve sus propias direcciones, como si tuviera toda la memoria para él; el sistema las traduce a RAM real |
| **Segmento** | Zona de esa memoria con un propósito y unos permisos (lectura, escritura, ejecución) |
| **LIFO** | *Last In, First Out*: lo último que entra es lo primero que sale, como una pila de platos |
| **Frame (marco de pila)** | El trozo de stack que usa una llamada a función: sus variables locales, parámetros y dirección de retorno |
| **Ámbito** (*scope*) | Zona del código donde una variable existe y se puede usar (ver [[Variables static y ámbito]]) |
| **Literal de cadena** | El texto entre comillas que escribes en el código, como `"hola"` |
| **Segfault** (`SIGSEGV`) | El sistema mata el programa porque ha tocado memoria que no puede tocar |

## Mapa de memoria virtual

Disposición típica de un proceso en Linux x86-64 (en 32 bits es igual, con direcciones más pequeñas):

```text
  +-----------------------------------------+  Direcciones altas (p. ej. 0x7FFF...)
  | Argumentos y entorno                    |  envp, argv, argc
  +-----------------------------------------+
  |                  STACK                  |  <-- Crece hacia abajo (direcciones menores)
  |                    |                    |      LIFO: un frame por cada llamada
  |                    v                    |
  |                                         |
  |       mmap / librerías compartidas      |  <-- libc.so, malloc grandes, etc.
  |                                         |
  |                    ^                    |
  |                    |                    |
  |                  HEAP                   |  <-- Crece hacia arriba (direcciones mayores)
  |                                         |      Se amplía con brk / sbrk / mmap
  +-----------------------------------------+
  |                  BSS                    |  <-- Block Started by Symbol
  |                                         |      Globales/static sin inicializar (a 0)
  +-----------------------------------------+
  |                  DATA                   |  <-- Globales/static inicializadas
  |                                         |      (el valor inicial va dentro del binario)
  +-----------------------------------------+
  |              RODATA + TEXT              |  <-- Literales de cadena, constantes (solo lectura)
  |                                         |      Código máquina (lectura + ejecución)
  +-----------------------------------------+  Direcciones bajas (p. ej. 0x0040...)
```

> [!info] Es un modelo simplificado
> Las direcciones del stack, del heap y de las librerías cambian en cada ejecución por seguridad (*ASLR*, aleatorización del espacio de direcciones), y si el ejecutable se compila como PIE también se mueven las de text, data y BSS. Lo que se mantiene es el orden general y los permisos de cada zona. En el [[#Ver dónde vive cada variable|ejemplo de abajo]] lo puedes comprobar tú mismo.

## Cada segmento en detalle

### Argumentos y entorno

- **Contenido:** las variables de entorno (`envp`) y los argumentos de la línea de comandos (`argc`, `argv`).
- **Ubicación:** en lo más alto del espacio de usuario, justo encima del stack.
- **Acceso:** lectura y escritura (puedes modificar las cadenas de `argv` dentro de tu proceso).

### Stack (pila de llamadas)

- **Propósito:** guarda un *frame* por cada función que está en marcha. Cada frame contiene:
  - Variables locales (también llamadas *automáticas*).
  - Parámetros de la función.
  - **Dirección de retorno**: dónde debe seguir el programa cuando la función haga `return`.
  - Registros de la CPU que hay que restaurar al volver (`RBP`, etc.).
- **Comportamiento:** **LIFO**. La memoria se reserva sola al entrar en la función y se libera sola al salir. No llamas a `free` para nada del stack.
- **Crecimiento:** hacia direcciones **más bajas**.
- **Ejemplo:**
  ```c
  void	funcion(int param)
  {
  	int	local;      // 'local' vive en el frame de funcion()

  	local = param;  // 'param' también vive en ese frame
  }                   // al salir, el frame desaparece: local y param ya no existen
  ```
- **Riesgo:** *stack overflow* por recursión infinita o por [[Arrays en C|arrays]] locales gigantes (ver [[#Stack overflow]]). También devolver la dirección de una variable local: al salir de la función esa memoria se reutiliza.

### Heap (memoria dinámica)

- **Propósito:** datos cuyo tamaño o duración no se conoce al compilar (una cadena que lees del teclado, una lista que crece…).
- **Gestión:** **100 % manual**. Pides memoria con `malloc`, `calloc` o `realloc` y la devuelves con `free`. Si no la devuelves, se queda reservada hasta que acaba el programa (*leak*).
- **Crecimiento:** hacia direcciones **más altas** (hacia el stack).
- **Ejemplo:**
  ```c
  int	*ptr;

  ptr = malloc(sizeof(int) * 100);   // 400 bytes en el heap (con int de 4 bytes)
  if (ptr == NULL)
  	return (1);
  ptr[0] = 10;
  free(ptr);                         // liberación obligatoria
  ptr = NULL;                        // evita usar por error un puntero colgante
  ```
  `ptr` (la variable con la dirección) está en el **stack**; los 400 bytes a los que apunta están en el **heap**. Ver [[Punteros en C]].
- **Riesgos:** fugas de memoria (*memory leaks*), *use-after-free*, *double free* (ver [[#Errores de memoria frecuentes]]).

> [!note] En C no hace falta el cast de `malloc`
> `malloc` devuelve `void *`, que se convierte solo a cualquier puntero. `(int *)malloc(...)` funciona pero sobra; en 42 lo habitual es no ponerlo.

### BSS (*Block Started by Symbol*)

- **Propósito:** variables globales y `static` **sin valor inicial** (o inicializadas a cero).
- **Características:** **no ocupan espacio en el ejecutable**, solo se apunta cuántos bytes harán falta. Al cargar el programa, el sistema reserva esa zona y la llena de ceros (`0`, `'\0'` o `NULL` según el tipo).
- **Ejemplo:**
  ```c
  int			g_uninit_global;   // en BSS, vale 0
  static char	s_buffer[2048];    // en BSS, todo '\0'
  ```

### Data (datos inicializados)

- **Propósito:** variables globales y `static` **inicializadas** con un valor distinto de cero.
- **Características:** **sí ocupan espacio en el ejecutable**, porque hay que guardar su valor inicial para copiarlo a memoria al arrancar.
- **Ejemplo:**
  ```c
  int				g_init_global = 100;   // en DATA
  static float	s_pi = 3.14159f;       // en DATA
  ```

> [!note] Norma
> La [[La Norma|Norma]] solo permite declarar e inicializar en la misma línea las globales (cuando el proyecto las permite), las `static` y las constantes. Además, las globales deben empezar por `g_` y, salvo que el proyecto diga otra cosa, ser `const` o `static`.

### Text (código) y rodata

- **Propósito:** **text** contiene las instrucciones máquina que ejecuta el procesador. Al lado está **`.rodata`** (*read-only data*), donde van los literales de cadena y las constantes globales. Técnicamente `.rodata` no es text, pero las dos son de solo lectura y en la práctica se agrupan.
- **Permisos:** text es de lectura y ejecución (`R-X`); rodata, solo lectura (`R--`).
- **Protección:** cualquier intento de escribir aquí provoca un **segfault** (`SIGSEGV`).
- **Ejemplo:**
  ```c
  char	*str;

  str = "Hola 42";   // "Hola 42" está en .rodata (solo lectura);
                     // 'str' es un puntero en el stack que apunta ahí
  ```

## Tabla comparativa y modificadores de almacenamiento

### Tabla general de segmentos

| Segmento | Se reserva | Se libera | Dura | Permisos | Crece hacia |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Text / rodata** | Al compilar (va en el binario) | Fin del proceso | Todo el programa | `R-X` / `R--` | Fijo |
| **Data** | Al compilar (va en el binario) | Fin del proceso | Todo el programa | `RW-` | Fijo |
| **BSS** | Al cargar el proceso | Fin del proceso | Todo el programa | `RW-` | Fijo |
| **Heap** | En ejecución (`malloc`) | Manual (`free`) | Hasta `free()` o fin | `RW-` | Direcciones altas (↑) |
| **Stack** | Al entrar en la función | Al salir de la función | Mientras dura la llamada | `RW-` | Direcciones bajas (↓) |

### Relación con las palabras clave de almacenamiento

Estas palabras (*storage class specifiers*) cambian dónde vive una variable o quién la puede ver. Más en [[Variables static y ámbito]].

- **`static` en una variable local:** la saca del **stack** y la lleva a **DATA** (si tiene valor inicial distinto de 0) o **BSS** (si no). Conserva su valor entre llamadas a la función.
- **`static` en una global o función:** sigue en **DATA/BSS**, pero solo es visible dentro de su fichero `.c` (su *unidad de traducción*).
- **`const`:**
  - Global inicializada: suele ir a **rodata** (solo lectura).
  - Local: vive en el **stack**; es el compilador quien impide modificarla.
- **`register`:** sugiere guardar la variable en un **registro de la CPU** en lugar del stack. Los compiladores modernos lo ignoran y deciden solos; lo único que garantiza es que no puedes obtener su dirección (`&var`).
- **`extern`:** dice que la variable existe (en **DATA/BSS**) pero está definida en otro fichero. Ver Preprocesador y headers.

## Ver dónde vive cada variable

Este programa imprime la dirección de una variable de cada zona. Compila con `cc -Wall -Wextra -Werror`:

```c
#include <stdio.h>
#include <stdlib.h>

int			g_data = 42;
int			g_bss;
const char	g_rodata[] = "CONSTANTE";

static void	show(const char *name, void *addr)
{
	printf("%-28s %p\n", name, addr);
}

int	main(int argc, char **argv)
{
	static int	s_counter;
	int			local;
	char		*literal;
	int			*heap;

	local = argc;
	literal = "hola";
	heap = malloc(sizeof(int) * 5);
	if (!heap)
		return (1);
	show("argv[0]       (stack, arriba)", argv[0]);
	show("&local        (stack)", &local);
	show("heap          (heap)", heap);
	show("&s_counter    (bss)", &s_counter);
	show("&g_bss        (bss)", &g_bss);
	show("&g_data       (data)", &g_data);
	show("literal       (rodata)", literal);
	show("g_rodata      (rodata)", (void *)g_rodata);
	show("main          (text)", (void *)main);
	free(heap);
	return (0);
}
```

Salida real (Ubuntu 22.04, clang 12; tus direcciones serán otras):

```text
argv[0]       (stack, arriba) 0x7ffd62faa33a
&local        (stack)        0x7ffd62fa9a2c
heap          (heap)         0x1c27d2a0
&s_counter    (bss)          0x404048
&g_bss        (bss)          0x40404c
&g_data       (data)         0x404040
literal       (rodata)       0x40200e
g_rodata      (rodata)       0x402004
main          (text)         0x401150
```

Fíjate en el orden: el stack está arriba del todo (`0x7ffd...`), el heap bastante más abajo, y data, BSS, rodata y text al fondo (`0x40...`).

> [!note] Este ejemplo no es de proyecto
> Usa variables globales (la Norma las prohíbe si no son `const` o `static`) y convierte `main` (una función) a `void *`, algo que el estándar no garantiza: con `-pedantic` no compila. Sirve para mirar la memoria, no para entregarlo.

## Herramientas de inspección

### `size`: tamaño de cada segmento

Muestra cuántos bytes ocupa cada segmento fijo en el ejecutable:

```bash
cc -Wall -Wextra -Werror main.c -o programa_demo
size programa_demo
```

```text
   text	   data	    bss	    dec	    hex	filename
   1775	    580	     12	   2367	    93f	programa_demo
```

- `text`: código y datos de solo lectura (incluye rodata).
- `data`: globales y `static` inicializadas (más algunas tablas internas del programa, por eso sale más que tu `int`).
- `bss`: globales y `static` sin inicializar.
- `dec` / `hex`: la suma de los tres, en decimal y hexadecimal.

### `nm`: en qué sección está cada símbolo

Un *símbolo* es el nombre de una función o variable global dentro del binario.

```bash
nm programa_demo | grep -E ' (g_|s_counter|main|show)'
```

```text
000000000040404c B g_bss
0000000000404040 D g_data
0000000000402004 R g_rodata
0000000000401150 T main
0000000000404048 b main.s_counter
0000000000401290 t show
```

| Letra | Sección |
|---|---|
| `T` / `t` | **Text** (código) |
| `D` / `d` | **Data** |
| `B` / `b` | **BSS** |
| `R` / `r` | **Rodata** (solo lectura) |

Mayúscula = símbolo global (visible desde otros ficheros); minúscula = local (`static`). Por eso `show` y `s_counter` salen en minúscula.

### `valgrind`: fugas y accesos inválidos

`valgrind` ejecuta tu programa en una CPU simulada y vigila cada lectura, escritura, `malloc` y `free`:

```bash
valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./programa_demo
```

Ver [[Valgrind y sanitizers]] para leer su salida y para la alternativa `-fsanitize=address`.

## Errores de memoria frecuentes

> [!note] Ejemplos ilustrativos
> Los fragmentos de esta sección declaran e inicializan en la misma línea para ser más cortos; norminette los marcaría.

### Segmentation fault (`SIGSEGV`)

Ocurre cuando el proceso accede a una dirección que no tiene asignada o viola los permisos del segmento:

- **Escribir en un literal (rodata):**
  ```c
  char	*str = "Hola";

  str[0] = 'h';   // ❌ segfault: rodata es de solo lectura
  ```
- **Desreferenciar un puntero `NULL` o inválido** (ver [[Carácter nulo y puntero NULL]]):
  ```c
  int	*p = NULL;

  *p = 5;         // ❌ segfault: puntero nulo
  ```

Para saber en qué línea pasa: [[Depurar con gdb]].

### Stack overflow

Se agota el espacio reservado para la pila (8 MB por defecto en Linux; compruébalo con `ulimit -s`, que lo muestra en KB):

- **Recursión infinita** (ver [[Recursión]]):
  ```c
  void	funcion_infinita(void)
  {
  	funcion_infinita();   // ❌ cada llamada añade un frame y nunca se quitan
  }
  ```
- **Arrays locales enormes:**
  ```c
  void	matriz_gigante(void)
  {
  	char	buffer[10 * 1024 * 1024];   // ❌ 10 MB: no caben en un stack de 8 MB
  }
  ```
  Si necesitas tanto, reserva con `malloc`.

### Fuga de memoria (*memory leak*)

Reservar en el heap con `malloc` y perder el puntero sin llamar a `free()`:

```c
void	leak_ejemplo(void)
{
	int	*p = malloc(100);

	// falta free(p);
}   // al salir, 'p' desaparece del stack y nadie conoce ya la dirección de esos 100 bytes
```

### Use-after-free y double free

- **Use-after-free:** usar memoria del heap después de haberla liberado con `free()`. Puede «funcionar» un tiempo y fallar más tarde, cuando esa memoria se reutiliza.
- **Double free:** llamar dos veces a `free()` con la misma dirección. glibc suele abortar el programa con un mensaje `free(): double free detected...`. Poner el puntero a `NULL` tras liberarlo lo evita, porque `free(NULL)` no hace nada.

## Relacionadas

- [[Punteros en C]]: qué es una dirección y cómo se usa.
- [[Carácter nulo y puntero NULL]]: `'\0'` termina cadenas, `NULL` indica «sin memoria» o fin de un array de punteros.
- [[Arrays en C]]: arrays locales en el stack, literales de solo lectura.
- [[Variables static y ámbito]]: `static`, globales y cuánto vive cada variable.
- [[Valgrind y sanitizers]] · [[Depurar con gdb]]: encontrar leaks y crashes.
- [[Control de errores en C]]: comprobar `malloc` y liberar en los caminos de error.
- [[libft - Anexo comparativo]]: qué funciones de libft reservan memoria en el heap.
- [[ft_calloc]] · [[ft_strdup]] · [[ft_split]]: ejemplos de reserva y liberación en el heap.

## Referencias

- [Storage duration — cppreference](https://en.cppreference.com/w/c/language/storage_duration) — duración automática, estática y asignada; `static`, `extern`, `register`.
- [Borrador del estándar C11 (N1570)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) — §6.2.4 (duración de almacenamiento), §6.7.9p10 (los objetos estáticos sin inicializar valen 0).
- [String literals — cppreference](https://en.cppreference.com/w/c/language/string_literal) — modificar un literal es comportamiento indefinido.
- [malloc(3)](https://man7.org/linux/man-pages/man3/malloc.3.html) y [brk(2)](https://man7.org/linux/man-pages/man2/brk.2.html) — reserva dinámica; las peticiones grandes usan `mmap`.
- [proc_pid_maps(5)](https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html) — cómo ver las zonas reales de un proceso en `/proc/<pid>/maps`.
- [size(1)](https://man7.org/linux/man-pages/man1/size.1.html) y [nm(1)](https://man7.org/linux/man-pages/man1/nm.1.html) — columnas de `size` y letras de `nm`.
- [Valgrind: Memcheck manual](https://valgrind.org/docs/manual/mc-manual.html) — detección de leaks, *use-after-free* y *double free*.
- Wikipedia: [Data segment](https://en.wikipedia.org/wiki/Data_segment), [.bss](https://en.wikipedia.org/wiki/.bss), [Code segment](https://en.wikipedia.org/wiki/Code_segment) — disposición general de la memoria de un proceso.
- La Norma v4 (`Normativa 42/es.norm-2.pdf`) — reglas sobre variables globales e inicialización.
- Salidas de `./programa_demo`, `size` y `nm` obtenidas en Ubuntu 22.04 con clang 12.0.1.
