---
tags: [libft, anexo]
---
# libft - Anexo comparativo

[[libft - Índice|← Índice]] · Anexo

> Las funciones de libft agrupadas por **para qué sirven** (no por la Parte del subject), comparadas con sus «hermanas» y con alternativas de la libc que no están en libft.

> [!info] Cómo leer este anexo
> - Cada sección empieza con una tabla comparativa y sigue con pros/contras.
> - Las funciones con prefijo `ft_` enlazan a su nota. Las que no llevan `ft_` (`strcpy`, `strtol`, `printf`…) son de la libc y **no** forman parte de libft: aparecen solo como referencia.
> - **Complejidad** (notación O grande): cómo crece el trabajo según el tamaño de la entrada. O(1) = siempre lo mismo; O(n) = proporcional a n; O(n·m) = proporcional al producto. Aquí n = bytes/caracteres procesados, m = longitud de la aguja (la subcadena que buscas), N = nodos de la lista. Ver [[Algoritmos de ordenación y complejidad]].
> - **En el sitio**: la función modifica la memoria que ya tienes. **Copia**: reserva memoria nueva con `malloc` y deja el original intacto.
> - ✅ / ❌ marcan ventajas e inconvenientes.

## Guía rápida: «quiero…» → «uso…»

| Quiero… | Uso | En vez de… |
|---|---|---|
| Saber si un carácter es letra / dígito / imprimible | [[ft_isalpha]], [[ft_isdigit]], [[ft_isalnum]], [[ft_isprint]] | Comparar rangos a mano en cada sitio |
| Poner un buffer entero a cero | [[ft_bzero]] o [[ft_memset]] con 0 | — |
| Reservar memoria ya a cero | [[ft_calloc]] | `malloc` + [[ft_bzero]] |
| Copiar bytes entre zonas **que pueden solaparse** | [[ft_memmove]] | [[ft_memcpy]] |
| Copiar una cadena a un buffer que ya tengo | [[ft_strlcpy]] | `strcpy` / `strncpy` |
| Copiar una cadena a memoria nueva | [[ft_strdup]] | `malloc` + [[ft_strlcpy]] |
| Copiar solo un trozo a memoria nueva | [[ft_substr]] | — |
| Añadir una cadena al final de un buffer | [[ft_strlcat]] | `strcat` / `strncat` |
| Unir dos cadenas en memoria nueva | [[ft_strjoin]] | — |
| Buscar un carácter | [[ft_strchr]] (primero) / [[ft_strrchr]] (último) | — |
| Buscar un byte en datos binarios | [[ft_memchr]] | [[ft_strchr]] |
| Buscar una subcadena | [[ft_strnstr]] | `strstr` |
| Comparar cadenas | [[ft_strncmp]] | `strcmp` |
| Comparar bloques de memoria | [[ft_memcmp]] | [[ft_strncmp]] |
| Texto → número | [[ft_atoi]] | `strtol` (no permitido) |
| Número → texto | [[ft_itoa]] (en memoria) / [[ft_putnbr_fd]] (directo a fd) | `sprintf` / `printf` |
| Quitar espacios u otros caracteres de los extremos | [[ft_strtrim]] | — |
| Partir una cadena en palabras | [[ft_split]] | `strtok` |
| Transformar cada carácter | [[ft_strmapi]] (copia) / [[ft_striteri]] (en el sitio) | — |
| Escribir en pantalla / fichero | [[ft_putstr_fd]], [[ft_putendl_fd]], [[ft_putchar_fd]], [[ft_putnbr_fd]] | `printf` |
| Recorrer / transformar una lista | [[ft_lstiter]] (en el sitio) / [[ft_lstmap]] (lista nueva) | — |

---

## Clasificación de caracteres

[[ft_isalpha]] · [[ft_isdigit]] · [[ft_isalnum]] · [[ft_isascii]] · [[ft_isprint]]

| Función | Rango aceptado | Equivale a |
|---|---|---|
| [[ft_isalpha]] | `'A'–'Z'`, `'a'–'z'` | — |
| [[ft_isdigit]] | `'0'–'9'` | — |
| [[ft_isalnum]] | letras + dígitos | `ft_isalpha(c) \|\| ft_isdigit(c)` |
| [[ft_isascii]] | `0–127` | — |
| [[ft_isprint]] | `32–126` (espacio incluido) | — |

**Comparativa**

- **isascii vs isprint:** `isascii` acepta los caracteres de control (`'\n'`, `'\t'`, `127`…); `isprint` no. Todo lo que es `isprint` es `isascii`, pero no al revés.
- **isalnum vs llamar a isalpha + isdigit:** reutilizar las otras dos es más legible y evita duplicar rangos; escribir los rangos directamente ahorra dos llamadas (irrelevante en la práctica).
- **libft vs libc:**
  - ✅ libft devuelve siempre **1 o 0** (lo exige el subject); la libc devuelve «distinto de cero», que puede ser cualquier valor (p. ej. `1024`). No compares nunca el resultado de la original con `== 1`.
  - ❌ libft ignora el *locale*; la libc puede considerar letras otros caracteres (`'ñ'`, `'é'`) según el `setlocale`.
  - **Cuidado:** En la libc es comportamiento indefinido pasar un valor que no sea `EOF` ni representable como `unsigned char` (p. ej. un `char` negativo). Si recorres un `char *`, haz *cast* a `(unsigned char)`.

## Transformación de caracteres

[[ft_toupper]] · [[ft_tolower]] · [[ft_strmapi]] · [[ft_striteri]]

| Función | Trabaja sobre | Reserva memoria | Modifica el original |
|---|---|---|---|
| [[ft_toupper]] / [[ft_tolower]] | un carácter | No | No (devuelve el nuevo valor) |
| [[ft_striteri]] | cadena entera, en el sitio | No | **Sí** |
| [[ft_strmapi]] | cadena entera, copia nueva | Sí (`malloc`) | No |

**Comparativa**

- **toupper / tolower:** si el carácter no es letra del caso contrario, lo devuelven **sin cambios** (no hace falta comprobarlo antes).
- **strmapi vs striteri:** son la pareja «copia vs en el sitio».
  - [[ft_strmapi]] ✅ conserva el original, ✅ funciona con literales (`"hola"`), ❌ cuesta un `malloc` y hay que hacer `free`.
  - [[ft_striteri]] ✅ sin memoria extra, ❌ destruye el original, ❌ **crashea con literales** (están en memoria de solo lectura, ver [[Segmentos de memoria en C]]).
  - Ambas pasan el **índice** a `f`, así que puedes hacer transformaciones que dependen de la posición (alternar mayúsculas, etc.).

## Inicializar memoria

[[ft_memset]] · [[ft_bzero]] · [[ft_calloc]]

| Función | Valor de relleno | Reserva memoria | Devuelve | Estándar |
|---|---|---|---|---|
| [[ft_memset]] | cualquier byte | No | puntero al buffer | C estándar |
| [[ft_bzero]] | solo `0` | No | `void` | BSD; marcada obsoleta en POSIX.1-2001 y eliminada en POSIX.1-2008 |
| [[ft_calloc]] | solo `0` | **Sí** | puntero nuevo o `NULL` | C estándar |

**Comparativa**

- **memset vs bzero:** `bzero(p, n)` ≡ `memset(p, 0, n)`. En libft lo natural es implementar [[ft_bzero]] llamando a [[ft_memset]].
  - [[ft_memset]] ✅ estándar y portable, ✅ cualquier valor, ✅ devuelve el puntero (encadenable).
  - [[ft_bzero]] ✅ más corta y explícita para «poner a cero», ❌ no es C estándar.
- **Cuidado:** `memset` rellena **bytes**, no elementos: `memset(arr_int, 1, n)` **no** pone los `int` a 1 (pone cada int a `0x01010101`). Solo `0` y `-1` funcionan «como esperarías» con enteros.
- **calloc vs malloc + bzero:**
  - [[ft_calloc]] ✅ una sola llamada, ✅ la original comprueba el desbordamiento de `nmemb * size` (devuelve `NULL` en vez de reservar menos de lo pedido). Conviene que tu versión lo haga también.
  - ❌ si vas a sobrescribir toda la memoria de inmediato, poner a cero es trabajo inútil: ahí basta `malloc`.

## Copiar datos

[[ft_memcpy]] · [[ft_memmove]] · [[ft_strlcpy]] · [[ft_strdup]] · [[ft_substr]]

| Función | Para | Para en `'\0'` | Solapamiento | Destino | Termina en `'\0'` |
|---|---|---|---|---|---|
| [[ft_memcpy]] | bytes | No | ❌ indefinido | buffer existente | No aplica |
| [[ft_memmove]] | bytes | No | ✅ seguro | buffer existente | No aplica |
| [[ft_strlcpy]] | cadenas | Sí | ❌ indefinido | buffer existente (`size`) | Sí, si `size > 0` |
| [[ft_strdup]] | cadenas | Sí | — | memoria nueva | Sí |
| [[ft_substr]] | trozo de cadena | Sí | — | memoria nueva | Sí |
| `strcpy` *(libc)* | cadenas | Sí | ❌ | buffer existente | Sí, pero sin control de tamaño |
| `strncpy` *(libc)* | cadenas | Sí | ❌ | buffer existente | **No** si se trunca |

**memcpy vs memmove**

- [[ft_memcpy]] ✅ puede ser algo más rápida (no comprueba direcciones), ❌ resultado indefinido si `src` y `dest` se solapan.
- [[ft_memmove]] ✅ siempre correcta (copia hacia atrás cuando `dest > src`), ❌ una comparación extra.
- **Regla práctica:** usa [[ft_memmove]] salvo que sepas **seguro** que no hay solapamiento (p. ej. dos `malloc` distintos). Desplazar datos dentro del mismo array siempre es `memmove`.

**strlcpy vs strcpy / strncpy**

- [[ft_strlcpy]] ✅ nunca escribe más de `size` bytes, ✅ siempre termina en `'\0'` (si `size > 0`), ✅ devuelve `strlen(src)` → si `retorno >= size`, hubo truncado.
- ❌ recorre `src` entero aunque solo copie un poco (para calcular el retorno), así que `src` **debe** terminar en `'\0'`.
- `strcpy`: ❌ desbordamiento de buffer si `dest` es pequeño. `strncpy`: ❌ si trunca no pone `'\0'`, ❌ si sobra sitio rellena con ceros (lento).

**Copiar a un buffer vs a memoria nueva**

- [[ft_strlcpy]]: tú controlas la memoria (pila, buffer reutilizado…). ✅ sin `malloc`, ❌ tienes que saber el tamaño de antemano.
- [[ft_strdup]]: ✅ reserva exactamente `strlen + 1`, ❌ hay que hacer `free`, ❌ puede devolver `NULL`.
- [[ft_substr]]: como `strdup` pero de un trozo. Casos límite: `start >= ft_strlen(s)` → cadena vacía `""` (no `NULL`); `len` mayor que lo que queda → copia solo lo que queda.

## Concatenar

[[ft_strlcat]] · [[ft_strjoin]]

| Función | Destino | Reserva | Modifica entradas | Devuelve |
|---|---|---|---|---|
| [[ft_strlcat]] | buffer existente (`size` = tamaño total) | No | Sí (`dst`) | longitud que **intentó** crear |
| [[ft_strjoin]] | memoria nueva | Sí | No | nueva cadena o `NULL` |
| `strcat` / `strncat` *(libc)* | buffer existente | No | Sí | `dest` |

**Comparativa**

- [[ft_strlcat]] ✅ no desborda, ✅ el retorno permite detectar truncado (`retorno >= size`), ❌ `size` es el tamaño **total** del buffer (no lo que queda libre, al contrario que `strncat`), ❌ si `size <= strlen(dst)` no copia nada y devuelve `size + strlen(src)` — el caso límite más evaluado.
- [[ft_strjoin]] ✅ no toca las entradas y funciona con literales, ❌ `malloc` en cada llamada.
- **Cuidado:** Patrón peligroso con [[ft_strjoin]] en bucles: `s = ft_strjoin(s, otra);` pierde la referencia al `s` anterior → **leak**. Guarda el viejo y libéralo:
  ```c
  tmp = ft_strjoin(s, otra);
  free(s);
  s = tmp;
  ```
- Rendimiento: concatenar k veces con [[ft_strjoin]] copia todo cada vez (O(n·k)); con un buffer grande y [[ft_strlcat]] evitas los `malloc`, aunque `strlcat` también recorre `dst` en cada llamada.

## Buscar

[[ft_strchr]] · [[ft_strrchr]] · [[ft_memchr]] · [[ft_strnstr]]

| Función | Busca | Dónde | Para en `'\0'` | Devuelve | Coste |
|---|---|---|---|---|---|
| [[ft_strchr]] | un carácter | cadena | Sí | **primera** aparición o `NULL` | O(n), sale pronto |
| [[ft_strrchr]] | un carácter | cadena | Sí | **última** aparición o `NULL` | O(n), siempre entera |
| [[ft_memchr]] | un byte | `n` bytes | **No** | primera aparición o `NULL` | O(n) |
| [[ft_strnstr]] | una subcadena | primeros `len` caracteres | Sí | inicio de la coincidencia o `NULL` | O(n·m) ingenua |
| `strstr` *(libc)* | una subcadena | cadena entera | Sí | igual | — |

**Comparativa**

- **strchr vs strrchr:** misma idea, distinta dirección. `strrchr` es útil para extensiones (`ft_strrchr(file, '.')`) o rutas (`'/'`).
- **c == '\0':** ambas devuelven un puntero al `'\0'` final (no `NULL`). Es un caso clásico de evaluación.
- **c se convierte a `char`:** `ft_strchr(s, 'a' + 256)` debe encontrar `'a'`. Compara con `(char)c` (o `(unsigned char)` en `memchr`).
- **strchr vs memchr:**
  - [[ft_memchr]] ✅ sirve para datos binarios con ceros en medio, ✅ no necesita `'\0'`, ❌ necesitas saber `n`.
  - [[ft_strchr]] ✅ no necesitas la longitud, ❌ se detiene en el primer `'\0'`.
- **strnstr vs strstr:**
  - [[ft_strnstr]] ✅ limita la búsqueda (útil en buffers no terminados), ✅ aguja vacía → devuelve `haystack`.
  - ❌ no es estándar (BSD); la aguja debe caber **entera** dentro de los `len` primeros caracteres.

## Comparar

[[ft_strncmp]] · [[ft_memcmp]]

| Función | Para en `'\0'` | Límite | Compara como | Devuelve |
|---|---|---|---|---|
| [[ft_strncmp]] | Sí | `n` caracteres | `unsigned char` | `<0`, `0`, `>0` |
| [[ft_memcmp]] | **No** | `n` bytes exactos | `unsigned char` | `<0`, `0`, `>0` |
| `strcmp` *(libc)* | Sí | ninguno | `unsigned char` | `<0`, `0`, `>0` |

**Comparativa**

- **strncmp vs strcmp:** `ft_strncmp(a, b, n)` con `n` grande se comporta como `strcmp`. Con `n` pequeño sirve para «¿empieza por…?»: `ft_strncmp(linea, "export ", 7) == 0`.
- **strncmp vs memcmp:**
  - [[ft_strncmp]] ✅ seguro con cadenas de distinta longitud (para en el primer `'\0'`).
  - [[ft_memcmp]] ✅ compara datos binarios con ceros dentro, ❌ si una zona es más corta que `n`, lees fuera de ella.
  - **Cuidado:** No uses `memcmp` para comparar `struct`: el *padding* entre campos puede contener basura.
- **Cuidado:** Ambas deben restar como **`unsigned char`**: con `char` con signo, `'\200'` saldría menor que `'a'`. Error típico en la evaluación.
- No supongas que el retorno es `-1/0/1`: solo importa el **signo**.

## Longitudes y recorridos

[[ft_strlen]] · [[ft_lstsize]] · [[ft_lstlast]]

| Función | Mide / busca | Coste |
|---|---|---|
| [[ft_strlen]] | caracteres hasta `'\0'` | O(n) |
| [[ft_lstsize]] | nodos de la lista | O(N) |
| [[ft_lstlast]] | último nodo | O(N) |

- Ninguna guarda la longitud: **cada llamada recorre todo**. Llamar a `ft_strlen(s)` en la condición de un `while` lo vuelve O(n²); guárdalo en una variable antes del bucle.
- [[ft_strlen]] devuelve `size_t` (sin signo): `ft_strlen(s) - 1` con `s == ""` da un número gigante, no `-1`.

## Construir cadenas nuevas (con `malloc`)

[[ft_strdup]] · [[ft_substr]] · [[ft_strjoin]] · [[ft_strtrim]] · [[ft_split]] · [[ft_itoa]] · [[ft_strmapi]]

| Función | Entrada → salida | Cómo se libera |
|---|---|---|
| [[ft_strdup]] | cadena → copia | `free(s)` |
| [[ft_substr]] | cadena, `start`, `len` → trozo | `free(s)` |
| [[ft_strjoin]] | 2 cadenas → unión | `free(s)` |
| [[ft_strtrim]] | cadena, `set` → sin extremos | `free(s)` |
| [[ft_split]] | cadena, `c` → array de cadenas + `NULL` | `free` de cada cadena **y** del array |
| [[ft_itoa]] | `int` → cadena | `free(s)` |
| [[ft_strmapi]] | cadena, `f` → cadena transformada | `free(s)` |

**strtrim vs split**

- [[ft_strtrim]]: quita un **conjunto** de caracteres (`set`) solo de los **extremos**; lo de en medio se queda. `ft_strtrim("  a b  ", " ")` → `"a b"`.
- [[ft_split]]: usa **un solo** carácter delimitador en **toda** la cadena y descarta los trozos vacíos. `ft_split("  a  b ", ' ')` → `{"a", "b", NULL}`.
- `strtok` *(libc)*: ✅ acepta varios delimitadores, ❌ modifica la cadena original, ❌ guarda estado interno (no reentrante), ❌ no está permitida.

> [!warning] Regla común a toda esta sección
> Si un `malloc` intermedio falla, hay que **liberar lo ya reservado** antes de devolver `NULL`. Es crítico en [[ft_split]]: si falla la palabra 5, libera las 4 anteriores y el array.

## Conversión numérica

[[ft_atoi]] · [[ft_itoa]] · [[ft_putnbr_fd]]

| Función | Dirección | Reserva | Errores |
|---|---|---|---|
| [[ft_atoi]] | texto → `int` | No | No detecta ninguno |
| [[ft_itoa]] | `int` → texto (memoria) | Sí | `NULL` si falla `malloc` |
| [[ft_putnbr_fd]] | `int` → texto (escrito en fd) | No | — |
| `strtol` *(libc)* | texto → `long` | No | ✅ `errno`, `endptr`, base |

**Comparativa**

- [[ft_atoi]] ✅ simple, ❌ `"abc"` y `"0"` devuelven ambos `0` (no distingue error), ❌ el desbordamiento es indefinido. En proyectos posteriores (push_swap…) necesitarás una versión que detecte errores.
  - Reglas: salta espacios (`isspace`: `' '`, `\t \n \v \f \r`), acepta **un** `+` o `-`, lee dígitos hasta el primer no‑dígito. `"+-5"` → `0`.
- [[ft_itoa]] vs [[ft_putnbr_fd]]:
  - [[ft_itoa]] ✅ el resultado se puede guardar, concatenar, comparar…, ❌ `malloc` + `free`.
  - [[ft_putnbr_fd]] ✅ sin memoria dinámica, ❌ solo sirve para escribir.
- **Cuidado:** Caso común a ambas: **`INT_MIN` (-2147483648)**. `-INT_MIN` no cabe en `int`: trabaja con `long` o trata el caso aparte.

## Salida por *file descriptor*

[[ft_putchar_fd]] · [[ft_putstr_fd]] · [[ft_putendl_fd]] · [[ft_putnbr_fd]]

| Función | Escribe | Llamadas a `write` |
|---|---|---|
| [[ft_putchar_fd]] | 1 carácter | 1 |
| [[ft_putstr_fd]] | cadena | 1 (si usas `ft_strlen`) o n (carácter a carácter) |
| [[ft_putendl_fd]] | cadena + `'\n'` | 2 |
| [[ft_putnbr_fd]] | entero | 1 por dígito (recursiva típica) |
| `printf` *(libc)* | formato | buffer interno (pocas) |

**Comparativa**

- `write` es una *syscall* y **no tiene buffer**: escribir carácter a carácter es mucho más lento que `write(fd, s, ft_strlen(s))`.
- vs `printf`: ✅ las `put*_fd` eligen el fd (`2` para errores), ✅ escriben al instante, ❌ sin formato. **Cuidado:** mezclar `printf` y `write` en el mismo fd puede desordenar la salida (por el buffer de `printf`).

## Listas enlazadas

### Crear e insertar

| Función | Posición | Coste | Notas |
|---|---|---|---|
| [[ft_lstnew]] | — | O(1) | Reserva el nodo, **no** copia `content` (solo guarda el puntero) |
| [[ft_lstadd_front]] | principio | O(1) | Cambia `*lst` → por eso recibe `t_list **` |
| [[ft_lstadd_back]] | final | O(N) | Usa [[ft_lstlast]]; si la lista está vacía, `*lst = new` |

- Si insertas muchos elementos y el orden no importa, [[ft_lstadd_front]] es mucho más barata. Para mantener orden de llegada con `add_back` en O(1) habría que guardar un puntero al último (no lo pide libft).

### Liberar

| Función | Libera | Reenlaza | Deja `*lst` |
|---|---|---|---|
| [[ft_lstdelone]] | **un** nodo (`del(content)` + `free(nodo)`) | No | — |
| [[ft_lstclear]] | **todos** desde `*lst` | — | `NULL` |

- **Cuidado:** [[ft_lstdelone]] no arregla el `next` del nodo anterior: si borras uno del medio, enlaza tú antes los vecinos.
- `del` existe porque la lista no sabe qué es `content`: puede ser un `malloc` (→ `free`), un literal (→ función que no hace nada) o una estructura con más punteros dentro.

### Aplicar funciones

| Función | Resultado | Reserva | Original |
|---|---|---|---|
| [[ft_lstiter]] | — (modifica en el sitio) | No | se modifica |
| [[ft_lstmap]] | lista nueva | Sí | intacta |

- Es la misma pareja que [[ft_striteri]] / [[ft_strmapi]] para cadenas.
- [[ft_lstmap]] ❌ más compleja: si falla un `malloc` a mitad, debe liberar la lista nueva con [[ft_lstclear]] **y** el `content` recién creado por `f` que no llegó a meterse en un nodo (si no, leak).

---

## Resumen: quién reserva memoria

| Reservan (hay que hacer `free`) | No reservan |
|---|---|
| [[ft_calloc]], [[ft_strdup]], [[ft_substr]], [[ft_strjoin]], [[ft_strtrim]], [[ft_split]], [[ft_itoa]], [[ft_strmapi]], [[ft_lstnew]], [[ft_lstmap]] | Todas las demás |

## Resumen: pares «en el sitio vs copia»

| En el sitio (sin `malloc`) | Copia nueva (con `malloc`) |
|---|---|
| [[ft_strlcpy]] | [[ft_strdup]] / [[ft_substr]] |
| [[ft_strlcat]] | [[ft_strjoin]] |
| [[ft_striteri]] | [[ft_strmapi]] |
| [[ft_lstiter]] | [[ft_lstmap]] |
| [[ft_putnbr_fd]] | [[ft_itoa]] |
| [[ft_bzero]] / [[ft_memset]] | [[ft_calloc]] |

> [!summary] Criterio general
> **En el sitio** cuando el buffer ya existe y no necesitas el original (más rápido, sin leaks posibles); **copia** cuando el original debe conservarse, es un literal, o no sabes el tamaño final de antemano.

## Relacionadas

[[libft - Índice]] · [[Punteros en C]] · [[Segmentos de memoria en C]] · [[Carácter nulo y puntero NULL]] · [[Tipos enteros y conversiones]] · [[Listas enlazadas]] · [[Descriptores de fichero y read]] · [[Valgrind y sanitizers]] · [[Algoritmos de ordenación y complejidad]]

## Referencias

Anexo de elaboración propia. Para las citas literales, ver la nota de cada función.

- Linux man-pages 5.10 y libbsd (Ubuntu 22.04): `man 3 memset`, `man 3 memmove`, `man 3 strlcpy` (`3bsd`), etc. — comportamiento de las funciones originales.
- [cppreference: Null-terminated byte strings](https://en.cppreference.com/w/c/string/byte) — `strcpy`, `strncpy`, `strcat`, `strstr`, `strtok`, `memcmp` y compañía.
- [cppreference: strncpy](https://en.cppreference.com/w/c/string/byte/strncpy) — no termina en `'\0'` si trunca y rellena con ceros.
- [man7.org: bzero(3)](https://man7.org/linux/man-pages/man3/bzero.3.html) — `bzero` marcada LEGACY en POSIX.1-2001 y eliminada en POSIX.1-2008.
- [man7.org: isalpha(3)](https://man7.org/linux/man-pages/man3/isalpha.3.html) — retorno «distinto de cero» y argumento `unsigned char` o `EOF`.
- [man7.org: calloc(3)](https://man7.org/linux/man-pages/man3/calloc.3.html) — `calloc` comprueba el desbordamiento de `nmemb * size`.
- [man7.org: strtol(3)](https://man7.org/linux/man-pages/man3/strtol.3.html) y [strtok(3)](https://man7.org/linux/man-pages/man3/strtok.3.html) — alternativas de la libc citadas.
- [man7.org: write(2)](https://man7.org/linux/man-pages/man2/write.2.html) — `write` es una llamada al sistema sin buffer propio.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — comportamiento de las funciones de la Parte 2 y la Parte 3.
