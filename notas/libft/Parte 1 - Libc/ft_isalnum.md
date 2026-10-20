---
tags: [libft, libft/parte1, libft/caracteres]
funcion: ft_isalnum
original: "isalnum(3)"
cabecera: "<ctype.h>"
estado: hecho
---
# ft_isalnum

[[libft - Índice|← Índice]] · Parte 1 · Caracteres

> ¿Es letra o dígito? Devuelve 1 si `c` es una letra (`A`–`Z`, `a`–`z`) o un dígito (`0`–`9`) y 0 si no.

## Explicación sencilla

«Alfanumérico» = alfabético **o** numérico. Es la unión de [[ft_isalpha]] y [[ft_isdigit]].

| Entrada | Salida | Por qué |
|---|---|---|
| `'a'` | 1 | letra |
| `'Z'` | 1 | letra |
| `'4'` | 1 | dígito |
| `'_'` | 0 | símbolo |
| `' '` | 0 | espacio |

```text
 '0'..'9'   '['..'`'   'A'..'Z'   'a'..'z'    resto
 48 .. 57   91 .. 96   65 .. 90   97 .. 122
    1           0          1          1          0
```

## Prototipo

```c
// Original — isalnum(3)
#include <ctype.h>
int isalnum(int c);

// libft
int ft_isalnum(int c);
```

Consultar: `man 3 isalnum`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.
> 
> Para las funciones de clasificación de caracteres (isalpha, isdigit, isalnum, isascii, isprint), el valor de retorno debe ser:
> • 1 si el carácter cumple la condición comprobada.
> • 0 si el carácter no la cumple.

## Comportamiento según el manual

> [!quote] man 3 isalnum — DESCRIPTION
> These functions check whether c, which must have the value of an unsigned char or EOF, falls into a certain character class according to the specified locale.  The functions without the "_l" suffix perform the check based on the current locale.

> [!note] Traducción
> Estas funciones comprueban si c, que debe tener el valor de un unsigned char o EOF, pertenece a una determinada clase de caracteres según el locale especificado. Las funciones sin el sufijo "_l" hacen la comprobación según el locale actual.

> [!quote] man 3 isalnum — DESCRIPTION
> isalnum()
>        checks for an alphanumeric character; it is equivalent to (isalpha(c) || isdigit(c)).

> [!note] Traducción
> isalnum()
>        comprueba si es un carácter alfanumérico; equivale a (isalpha(c) || isdigit(c)).

> [!quote] man 3 isalnum — RETURN VALUE
> The values returned are nonzero if the character c falls into the tested class, and zero if not.

> [!note] Traducción
> Los valores devueltos son distintos de cero si el carácter c pertenece a la clase comprobada, y cero si no.

> [!quote] man 3 isalnum — NOTES
> The standards require that the argument c for these functions is either EOF or a value that is representable in the type unsigned char.  If the argument c is of type char, it must be cast to unsigned char

> [!note] Traducción
> Los estándares exigen que el argumento c de estas funciones sea EOF o un valor representable en el tipo unsigned char. Si el argumento c es de tipo char, debe convertirse (cast) a unsigned char

## Cómo implementarla

```text
si ft_isalpha(c) es verdadero o ft_isdigit(c) es verdadero → devolver 1
si no                                                     → devolver 0
```

> [!tip] Reutiliza tus funciones
> Llamar a tus `ft_isalpha` y `ft_isdigit` está permitido (son tuyas, no externas). Recuerda que el operador `||` de C ya da exactamente 0 o 1.

## Puntos clave y casos límite

- Se puede implementar reutilizando `ft_isalpha` y `ft_isdigit`.

### Errores típicos

- **Llamar a `isalpha`/`isdigit` de la libc**: son funciones externas y el subject lo prohíbe en la Parte 1.
- **Pensar que `'_'` es alfanumérico**: se permite en nombres de variables, pero no es letra ni dígito.
- **No declarar `ft_isalpha` y `ft_isdigit` en `libft.h`**: sin prototipo visible, la llamada es una «declaración implícita» y con `-Werror` no compila.

## Relacionadas

[[ft_isalpha]] · [[ft_isdigit]]

## Referencias

- `man 3 isalnum` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [isalnum(3) — man7.org](https://man7.org/linux/man-pages/man3/isalnum.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- [ascii(7) — man7.org](https://man7.org/linux/man-pages/man7/ascii.7.html) — tabla ASCII con los códigos de cada carácter.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
