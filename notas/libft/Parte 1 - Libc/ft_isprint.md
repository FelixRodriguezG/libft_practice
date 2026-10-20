---
tags: [libft, libft/parte1, libft/caracteres]
funcion: ft_isprint
original: "isprint(3)"
cabecera: "<ctype.h>"
estado: hecho
---
# ft_isprint

[[libft - Índice|← Índice]] · Parte 1 · Caracteres

> ¿Es imprimible (espacio incluido)? Devuelve 1 si `c` es un carácter visible o el espacio (32–126) y 0 si no.

## Explicación sencilla

«Imprimible» significa que, al escribirlo en la terminal, ocupa una posición: letras, dígitos, signos y el espacio. Los caracteres de control (salto de línea, tabulador, `'\0'`…) no lo son.

| Entrada | Código | Salida |
|---|---|---|
| `' '` | 32 | 1 |
| `'A'` | 65 | 1 |
| `'~'` | 126 | 1 |
| `'\n'` | 10 | 0 |
| `'\t'` | 9 | 0 |
| DEL | 127 | 0 |

```text
 0 .......... 31 | 32 .............. 126 | 127
   control       | ' ' ... 'A' ... '~'   | DEL
      0          |          1            |  0
```

## Prototipo

```c
// Original — isprint(3)
#include <ctype.h>
int isprint(int c);

// libft
int ft_isprint(int c);
```

Consultar: `man 3 isprint`

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

> [!quote] man 3 isprint — DESCRIPTION
> These functions check whether c, which must have the value of an unsigned char or EOF, falls into a certain character class according to the specified locale.  The functions without the "_l" suffix perform the check based on the current locale.

> [!note] Traducción
> Estas funciones comprueban si c, que debe tener el valor de un unsigned char o EOF, pertenece a una determinada clase de caracteres según el locale especificado. Las funciones sin el sufijo "_l" hacen la comprobación según el locale actual.

> [!quote] man 3 isprint — DESCRIPTION
> isprint()
>        checks for any printable character including space.

> [!note] Traducción
> isprint()
>        comprueba si es cualquier carácter imprimible, espacio incluido.

> [!quote] man 3 isprint — RETURN VALUE
> The values returned are nonzero if the character c falls into the tested class, and zero if not.

> [!note] Traducción
> Los valores devueltos son distintos de cero si el carácter c pertenece a la clase comprobada, y cero si no.

> [!quote] man 3 isprint — NOTES
> The standards require that the argument c for these functions is either EOF or a value that is representable in the type unsigned char.  If the argument c is of type char, it must be cast to unsigned char

> [!note] Traducción
> Los estándares exigen que el argumento c de estas funciones sea EOF o un valor representable en el tipo unsigned char. Si el argumento c es de tipo char, debe convertirse (cast) a unsigned char

## Cómo implementarla

```text
si c está entre 32 (' ') y 126 ('~'), ambos incluidos → devolver 1
si no                                                 → devolver 0
```

## Puntos clave y casos límite

- En el locale "C": 32 (`' '`) a 126 (`'~'`). El 127 (DEL) **no** es imprimible.

### Errores típicos

- **Empezar en 33**: eso es `isgraph` (imprimible **sin** espacio). El espacio sí cuenta para `isprint`.
- **Incluir el 127**: DEL es un carácter de control.
- **Creer que `'\t'` es imprimible**: es «espacio en blanco» (`isspace`), pero no imprimible.

## Relacionadas

[[ft_isascii]]

## Referencias

- `man 3 isprint` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [isprint(3) — man7.org](https://man7.org/linux/man-pages/man3/isprint.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- [ascii(7) — man7.org](https://man7.org/linux/man-pages/man7/ascii.7.html) — tabla ASCII con los códigos de cada carácter.
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
