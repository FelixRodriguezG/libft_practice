---
tags: [libft, libft/parte2]
funcion: ft_striteri
original: ninguna
externas: "Ninguna"
estado: pendiente
---
# ft_striteri

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Recorre una cadena y llama a una función `f` por cada carácter, pasándole su índice y su **dirección**, para que `f` pueda modificarlo en el sitio. No reserva memoria ni devuelve nada.

## Explicación sencilla

Tú no decides qué se hace con cada carácter: lo decide la función `f` que te pasan (un **puntero a función**, ver [[Punteros en C]]). Tu trabajo es solo recorrer y llamar.

```c
void	mayus_si_par(unsigned int i, char *c)
{
	if (i % 2 == 0)
		*c = ft_toupper(*c);
}

char	s[] = "hola";              /* array modificable, no un literal */
ft_striteri(s, mayus_si_par);
/* s ahora vale "HoLa" */
```

```text
 i:      0      1      2      3
       ┌─────┬─────┬─────┬─────┬────┐
 s ──► │ 'h' │ 'o' │ 'l' │ 'a' │ \0 │
       └─────┴─────┴─────┴─────┴────┘
          ▲
          └── f(0, &s[0])  →  f escribe 'H' en esa dirección
              f(1, &s[1])  →  no toca
              f(2, &s[2])  →  escribe 'L'
              f(3, &s[3])  →  no toca
```

Cómo leer el tipo del parámetro `f`:

```text
void (*f)(unsigned int, char *)
 │     │        │          └── 2º argumento: dirección del carácter
 │     │        └───────────── 1º argumento: índice
 │     └────────────────────── f es un puntero a función
 └──────────────────────────── la función no devuelve nada
```

## Prototipo

```c
void ft_striteri(char *s, void (*f)(unsigned int, char*));
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> No usa funciones externas, así que no hay citas de `man`.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Aplica la función ‘f’ a cada carácter de la string ‘s’, pasando como parámetros el índice de cada carácter dentro de ‘s’ y la dirección del propio carácter, que puede modificarse si es necesario.

| | |
|---|---|
| **Parámetros** | `s`: La cadena sobre la que iterar.<br>`f`: La función a aplicar sobre cada carácter. |
| **Valor devuelto** | Nada |
| **Funciones autorizadas** | Ninguna |

## Cómo implementarla

```text
1. Si s o f son NULL → sal.
2. i = 0
3. Mientras s[i] no sea '\0':
       llama f(i, dirección de s[i])
       i = i + 1
```

## Puntos clave y casos límite

- Diferencia con `ft_strmapi`: modifica `s` directamente (recibe `&s[i]`), sin reservar memoria.

> [!warning] Errores típicos
> - **Pasar `s[i]` en vez de `&s[i]`**: `f` espera un `char *`; el compilador avisa y, si fuerzas el tipo, `f` escribirá en una dirección absurda → *segfault*.
> - **Probarla con un literal**: `ft_striteri("hola", f)` intenta modificar memoria de solo lectura → *segfault*. Usa `char s[] = "hola";` (ver [[Segmentos de memoria en C]]).
> - **Llamar a `f` sin comprobar NULL**: llamar a un puntero a función NULL es un salto a la dirección 0 → *segfault*.
> - **Usar `int` para el índice**: el prototipo de `f` pide `unsigned int`; mantén el tipo para evitar avisos de conversión ([[Tipos enteros y conversiones]]).

## Relacionadas

[[ft_strmapi]] · [[ft_lstiter]] · [[Punteros en C]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
