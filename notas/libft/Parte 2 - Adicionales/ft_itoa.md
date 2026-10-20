---
tags: [libft, libft/parte2]
funcion: ft_itoa
original: ninguna
externas: "malloc"
estado: pendiente
---
# ft_itoa

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Convierte un `int` en una cadena nueva (reservada con `malloc`) que lo escribe en base 10. Es la operación inversa de [[ft_atoi]]: «integer to ASCII».

## Explicación sencilla

Recibes un número y devuelves el **texto** que lo escribe:

| Entrada `n` | Salida (cadena) | Bytes a reservar |
|---|---|---|
| `42` | `"42"` | 3 (`'4' '2' '\0'`) |
| `-7` | `"-7"` | 3 (`'-' '7' '\0'`) |
| `0` | `"0"` | 2 |
| `-2147483648` (`INT_MIN`) | `"-2147483648"` | 12 |

Cómo queda `ft_itoa(-42)` en memoria (en el *heap*, ver [[Segmentos de memoria en C]]):

```text
 puntero devuelto
      │
      ▼
    ┌─────┬─────┬─────┬──────┐
    │ '-' │ '4' │ '2' │ '\0' │
    └─────┴─────┴─────┴──────┘
      [0]   [1]   [2]   [3]
```

El truco: los dígitos salen **del último al primero** (`42 % 10` da `2`; luego `42 / 10` da `4`…). Por eso conviene saber la longitud antes y rellenar la cadena de derecha a izquierda.

## Prototipo

```c
char *ft_itoa(int n);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Reserva memoria (utilizando malloc(3)) y devuelve una cadena que represente el valor del número entero recibido como argumento. Debe ser capaz de manejar números negativos.

| | |
|---|---|
| **Parámetros** | `n`: el entero a convertir. |
| **Valor devuelto** | La cadena que represente el número.<br>NULL si falla la reserva de memoria. |
| **Funciones autorizadas** | malloc |

## Funciones externas (man)

> [!quote] man 3 malloc — RETURN VALUE
> The malloc() and calloc() functions return a pointer to the allocated memory, which is suitably aligned for any built-in type.  On error, these functions return NULL.

> [!note] Traducción
> malloc() y calloc() devuelven un puntero a la memoria reservada, alineada adecuadamente para cualquier tipo predefinido. En caso de error, devuelven NULL.

## Cómo implementarla

```text
1. Copia n en una variable long nb (así -INT_MIN cabe sin desbordar).
2. Cuenta la longitud:
     len = 0
     si nb <= 0: len = 1            (hueco para el '-' o para el único '0')
     mientras nb != 0: nb = nb / 10; len = len + 1
3. Reserva len + 1 bytes. Si malloc devuelve NULL → devuelve NULL.
4. Pon '\0' en la posición len.
5. Vuelve a cargar nb = n. Si es 0 → pon '0' en la posición 0.
6. Si nb < 0 → pon '-' en la posición 0 y haz nb = -nb (ya positivo).
7. Mientras nb > 0:
     len = len - 1
     cadena[len] = (nb % 10) + '0'
     nb = nb / 10
8. Devuelve la cadena.
```

Separa el conteo de dígitos en una función auxiliar `static`: así cada función cabe en las 25 líneas de [[La Norma]].

## Puntos clave y casos límite

- `INT_MIN` (-2147483648) no se puede negar en `int`: usa `long` o trátalo aparte.
- `0` → `"0"` (cuidado con el bucle que cuenta dígitos).

> [!danger] Por qué `-n` falla con `INT_MIN`
> Un `int` de 32 bits va de -2147483648 a 2147483647: el positivo 2147483648 **no existe**. Calcular `-INT_MIN` en `int` es desbordamiento con signo, que en C es comportamiento indefinido (en la práctica suele quedarse en un valor negativo y tu bucle de dígitos no hace lo esperado). Copia antes a `long`: `long nb = n;` y entonces `-nb` vale 2147483648 sin problema. Más en [[Tipos enteros y conversiones]].

> [!warning] Errores típicos
> - **Olvidar el byte del `'\0'`** o el del `'-'` al reservar: escribes fuera del bloque. Valgrind lo marca como *Invalid write* ([[Valgrind y sanitizers]]).
> - **No comprobar el `malloc`**: si devuelve NULL y escribes en él, *segfault*. El subject pide devolver NULL ([[Control de errores en C]]).
> - **Contar mal los dígitos de `0`**: `while (n != 0)` no entra nunca, la longitud sale 0, reservas 1 byte y escribes 2.
> - **Usar `%` sobre negativos**: en C `-7 % 10` vale `-7`, no `3` (el resto lleva el signo del dividendo). Si no pasas a positivo antes, `'0' + (-7)` no es un dígito.

> [!question] Pregunta típica de evaluación
> «¿Qué devuelve tu `ft_itoa(INT_MIN)`?» Debe ser exactamente `"-2147483648"`, sin leaks.

## Relacionadas

[[ft_atoi]] · [[ft_putnbr_fd]] · [[Tipos enteros y conversiones]] · [[Control de errores en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 3 malloc` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [malloc(3) en man7.org](https://man7.org/linux/man-pages/man3/malloc.3.html).
