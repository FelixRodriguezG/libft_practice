---
tags: [libft, libft/parte2]
funcion: ft_split
original: ninguna
externas: "malloc, free"
estado: pendiente
---
# ft_split

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Corta una cadena en «palabras» usando un carácter como separador y devuelve un array de cadenas nuevas terminado en `NULL`. Es la función de libft que más memoria reserva, y la que más leaks suele tener.

## Explicación sencilla

```c
char **tab = ft_split("  hola  que tal ", ' ');
```

```text
tab[0] = "hola"
tab[1] = "que"
tab[2] = "tal"
tab[3] = NULL
```

El resultado es un `char **`: un puntero a un array de punteros, y cada uno apunta a una palabra. Hay **4 reservas** con `malloc`: el array y las 3 palabras ([[Punteros en C]], [[Arrays en C]]).

```text
 tab
  │
  ▼   array de char*  (malloc nº 1: 4 punteros)
┌──────────┐
│ tab[0] ──┼──► ┌───┬───┬───┬───┬────┐   malloc nº 2
│          │    │ h │ o │ l │ a │ \0 │
├──────────┤    └───┴───┴───┴───┴────┘
│ tab[1] ──┼──► ┌───┬───┬───┬────┐       malloc nº 3
│          │    │ q │ u │ e │ \0 │
├──────────┤    └───┴───┴───┴────┘
│ tab[2] ──┼──► ┌───┬───┬───┬────┐       malloc nº 4
│          │    │ t │ a │ l │ \0 │
├──────────┤    └───┴───┴───┴────┘
│   NULL   │  ← tab[3]: marca el final del array
└──────────┘
```

Fíjate en las **dos marcas de final** distintas: cada palabra acaba en `'\0'` (un `char`) y el array acaba en `NULL` (un puntero). Ver [[Carácter nulo y puntero NULL]].

Más ejemplos:

| Llamada | Resultado |
|---|---|
| `ft_split("a,b,,c", ',')` | `{"a", "b", "c", NULL}` |
| `ft_split(",,,", ',')` | `{NULL}` (array de 1 puntero) |
| `ft_split("", ' ')` | `{NULL}` |
| `ft_split("hola", ' ')` | `{"hola", NULL}` |

## Prototipo

```c
char **ft_split(char const *s, char c);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Reserva memoria (utilizando malloc(3)) y devuelve un arreglo (array) de cadenas obtenido al dividir la cadena ‘s’ en subcadenas utilizando el carácter ‘c’ como delimitador.
> Cada cadena del arreglo devuelto se reserva de manera independiente.
> El arreglo de punteros también se reserva dinámicamente.
> El arreglo devuelto debe terminar con un puntero a NULL.

| | |
|---|---|
| **Parámetros** | `s`: La cadena que se va a dividir.<br>`c`: El carácter delimitador. |
| **Valor devuelto** | El arreglo de nuevas cadenas resultante de la división.<br>NULL si falla cualquier reserva de memoria.<br>La estructura devuelta debe liberarse utilizando: 1) free() sobre cada cadena del arreglo; 2) free() sobre el arreglo. |
| **Funciones autorizadas** | malloc, free |

## Funciones externas (man)

> [!quote] man 3 malloc — RETURN VALUE
> The malloc() and calloc() functions return a pointer to the allocated memory, which is suitably aligned for any built-in type.  On error, these functions return NULL.

> [!note] Traducción
> malloc() y calloc() devuelven un puntero a la memoria reservada, alineada adecuadamente para cualquier tipo predefinido. En caso de error, devuelven NULL.

> [!quote] man 3 free — DESCRIPTION
> The free() function frees the memory space pointed to by ptr, which must have been returned by a previous call to malloc(), calloc(), or realloc().  Otherwise, or if free(ptr) has already been called before, undefined behavior occurs.  If ptr is NULL, no operation is performed.

> [!note] Traducción
> La función free() libera el espacio de memoria apuntado por ptr, que debe haber sido devuelto por una llamada previa a malloc(), calloc() o realloc(). Si no, o si ya se llamó antes a free(ptr), el comportamiento es indefinido. Si ptr es NULL, no se hace nada.

## Cómo implementarla

Divídela en funciones auxiliares `static` (con una sola no cabes en 25 líneas):

```text
contar_palabras(s, c):
    cuenta = 0
    recorre s; cada vez que encuentres un carácter != c
    que esté al principio o justo después de un c → cuenta + 1

liberar_todo(tab, hasta):
    para i de 0 a hasta - 1: free(tab[i])
    free(tab)
    devuelve NULL

ft_split(s, c):
    1. Si s es NULL → devuelve NULL.
    2. n = contar_palabras(s, c)
    3. tab = malloc((n + 1) * sizeof(char *))      ← +1 para el NULL final
       si falla → devuelve NULL
    4. i = 0 (palabra actual), pos = 0 (posición en s)
       mientras i < n:
           salta los c que haya en s desde pos
           inicio = pos; avanza pos hasta el siguiente c o el '\0'
           tab[i] = ft_substr(s, inicio, pos - inicio)
           si tab[i] es NULL → devuelve liberar_todo(tab, i)
           i = i + 1
    5. tab[n] = NULL
    6. Devuelve tab
```

## Puntos clave y casos límite

- Delimitadores consecutivos, al principio o al final no generan cadenas vacías: `ft_split("  a  b ", ' ')` → `{"a", "b", NULL}`.
- Si un `malloc` intermedio falla, libera **todo** lo reservado antes de devolver NULL (por eso se permite `free`).
- Cada palabra termina en `'\0'` y el array termina en `NULL`: no los confundas, ver [[Carácter nulo y puntero NULL]].
- Estructura típica: contar palabras → reservar array → reservar cada palabra con `ft_substr`.

> [!danger] Leak en el camino de error
> Si al reservar la palabra 3 falla `malloc` y devuelves NULL sin más, las palabras 0–2 y el array quedan reservados y **nadie** tiene ya un puntero a ellos: leak seguro. Libera cada `tab[0..i-1]` y luego `tab`, en ese orden (si liberas `tab` primero ya no puedes leer sus punteros). Los testers como *francinette* simulan fallos de `malloc` precisamente para pillar esto. Ver [[Control de errores en C]] y [[Valgrind y sanitizers]].

> [!warning] Errores típicos
> - **Reservar `n` punteros en vez de `n + 1`**: no queda sitio para el `NULL` final y escribes fuera del array.
> - **`sizeof(char)` en vez de `sizeof(char *)`** al reservar el array: reservas 1 byte por puntero cuando cada uno ocupa 8.
> - **Devolver `NULL` para `""` o `",,,"`**: lo esperado es un array válido con solo el `NULL` (`{NULL}`); `NULL` se reserva para fallos de memoria.
> - **Bucle que no avanza** si `c == '\0'`: protege el caso; con `ft_split("hola", '\0')` lo normal es `{"hola", NULL}`.
> - **Para liberar desde fuera** (en tu `main` o tus tests): un `free` por palabra y después `free(tab)`. Solo `free(tab)` deja las palabras perdidas.

> [!question] Pregunta típica de evaluación
> «¿Qué pasa si falla el tercer `malloc`?» Debes enseñar el código que libera lo anterior.

## Relacionadas

[[ft_substr]] · [[ft_strchr]] · [[ft_strdup]] · [[Carácter nulo y puntero NULL]] · [[Control de errores en C]] · [[Punteros en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 malloc` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [malloc(3) en man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html).
- `man 3 free` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [free(3) en man7.org](https://man7.org/linux/man-pages/man3/free.3.html).
