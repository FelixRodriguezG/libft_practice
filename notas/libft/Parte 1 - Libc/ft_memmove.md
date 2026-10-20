---
tags: [libft, libft/parte1, libft/memoria]
funcion: ft_memmove
original: "memmove(3)"
cabecera: "<string.h>"
estado: hecho
---
# ft_memmove

[[libft - Índice|← Índice]] · Parte 1 · Memoria

> Copia n bytes (permite solapamiento): como [[ft_memcpy]], pero funciona aunque `src` y `dest` compartan bytes.

## Explicación sencilla

Dos zonas se **solapan** cuando comparten bytes, por ejemplo al desplazar parte de una cadena dentro de sí misma.

```c
char	s[] = "0123456789";

ft_memmove(s + 2, s, 5);    /* dest está DESPUÉS de src */
```

```text
 índice:      0 1 2 3 4 5 6 7 8 9
 antes:       0 1 2 3 4 5 6 7 8 9
              └ src ──┘
                  └ dest ─┘
 correcto:    0 1 0 1 2 3 4 7 8 9     ← "0101234789"
 copiando desde el principio, como memcpy (mal):
              0 1 0 1 0 1 0 7 8 9     ← "0101010789"
```

¿Por qué falla la copia hacia delante? Al escribir `s[2]` se pisa un byte de `src` que todavía no se había leído. Si copias **desde el final**, lees cada byte antes de pisarlo.

En el caso contrario (`ft_memmove(s, s + 2, 5)`, `dest` antes que `src`) la copia normal hacia delante funciona: resultado `"2345656789"`.

## Prototipo

```c
// Original — memmove(3)
#include <string.h>
void *memmove(void *dest, const void *src, size_t n);

// libft
void *ft_memmove(void *dest, const void *src, size_t n);
```

Consultar: `man 3 memmove`

## Requisitos del subject

> [!quote] Subject v19.3 — Parte 1
> Tus funciones tendrán los mismos prototipos y comportamientos que las funciones originales, siguiendo fielmente las definiciones indicadas en la página del man de cada función. La única diferencia será el nombre: todas deberán comenzar con el prefijo “ft_”.
> 
> Deberás escribir tus propias versiones de las siguientes funciones originales. No deben depender de ninguna función externa.

## Comportamiento según el manual

> [!quote] man 3 memmove — DESCRIPTION
> The memmove() function copies n bytes from memory area src to memory area dest.  The memory areas may overlap: copying takes place as though the bytes in src are first copied into a temporary array that does not overlap src or dest, and the bytes are then copied from the temporary array to dest.

> [!note] Traducción
> La función memmove() copia n bytes de la zona de memoria src a la zona de memoria dest. Las zonas pueden solaparse: la copia se hace como si los bytes de src se copiaran primero a un array temporal que no se solapa ni con src ni con dest, y después se copiaran de ese array a dest.

> [!quote] man 3 memmove — RETURN VALUE
> The memmove() function returns a pointer to dest.

> [!note] Traducción
> La función memmove() devuelve un puntero a dest.

## Cómo implementarla

```text
d = dest como puntero a unsigned char
s = src  como puntero a const unsigned char
si d está antes que s:
    copiar de i = 0 hasta i = n - 1          (hacia delante, como memcpy)
si d está después que s:
    copiar de i = n - 1 hasta i = 0          (hacia atrás)
devolver dest
```

> [!tip] Bucle hacia atrás con `size_t`
> Decrementa antes de usar: «mientras n > 0: n = n − 1; d[n] = s[n]». Así nunca necesitas que el índice sea negativo.

## Puntos clave y casos límite

- No se puede usar un buffer temporal con malloc. El truco: si `dest > src`, copiar **de atrás hacia delante**; si no, de delante hacia atrás.
- Caso de prueba típico: `ft_memmove(s + 2, s, 5)` y `ft_memmove(s, s + 2, 5)`.

### Errores típicos

- **`while (i >= 0)` con `size_t i`**: un `size_t` nunca es negativo; al pasar de 0 «da la vuelta» a un número enorme y el bucle no termina (o segfault). Ver [[Tipos enteros y conversiones]].
- **Reservar un buffer temporal con `malloc`**: es lo que «parece» decir el man, pero no puedes usar funciones externas aquí y además sería lento. Basta con elegir el sentido de la copia.
- **Llamar a `ft_memcpy` para el caso «hacia delante»** solo es correcto si tu `ft_memcpy` copia de verdad hacia delante; si un día la optimizas, `memmove` se rompe.
- **Probar solo sin solapamiento**: los dos casos de prueba de arriba son obligatorios en tus tests.

## Relacionadas

[[ft_memcpy]] · [[Punteros en C]] · [[Tipos enteros y conversiones]]

## Referencias

- `man 3 memmove` — Linux man-pages 5.10 (Ubuntu 22.04): las citas en inglés están copiadas literalmente del manual; la traducción es propia.
- [memmove(3) — man7.org](https://man7.org/linux/man-pages/man3/memmove.3.html) — versión en línea del manual de Linux (puede ser más reciente que la de Ubuntu 22.04).
- Subject de libft v19.3 (`es.subject_libft.pdf`) — requisitos copiados literalmente.
- En los Mac de 42 (man de BSD/macOS) la redacción del manual puede variar.
