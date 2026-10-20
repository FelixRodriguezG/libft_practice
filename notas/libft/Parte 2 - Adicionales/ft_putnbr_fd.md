---
tags: [libft, libft/parte2]
funcion: ft_putnbr_fd
original: ninguna
externas: "write"
estado: pendiente
---
# ft_putnbr_fd

[[libft - Índice|← Índice]] · Parte 2 · Funciones adicionales

> Escribe un número entero, en base 10 y con su signo, en el descriptor de fichero indicado. A diferencia de [[ft_itoa]], no reserva memoria: escribe los dígitos directamente con `write`.

## Explicación sencilla

```c
ft_putnbr_fd(-305, 1);
```

```text
$ ./a.out
-305
```

`write` solo sabe escribir **bytes** (caracteres), no números. Para escribir `305` hay que mandar `'3'`, `'0'` y `'5'`, en ese orden. Pero `305 % 10` te da primero el **último** dígito (`5`). La [[Recursión]] arregla el orden: «escribe primero todo menos la última cifra, y luego la última».

```text
putnbr(305)
 ├─ putnbr(30)
 │   ├─ putnbr(3)
 │   │   └─ escribe '3'      ← 3 < 10: caso base
 │   └─ escribe '0'          (30 % 10)
 └─ escribe '5'              (305 % 10)
Salida: 3 0 5
```

Para convertir un dígito (0–9) en su carácter: `digito + '0'` (en ASCII `'0'` vale 48, `'5'` vale 53).

## Prototipo

```c
void ft_putnbr_fd(int n, int fd);
```

> [!info] Sin función original
> No existe en la libc, así que no tiene página `man 3`. El comportamiento lo define el **subject** de libft.
> Las citas de `man` de abajo son de las funciones externas que usa.

## Comportamiento según el subject

> [!quote] Subject v19.3 — Descripción
> Escribe el número entero ‘n’ en el descriptor de archivo dado.

| | |
|---|---|
| **Parámetros** | `n`: El número entero que se envía.<br>`fd`: El descriptor de archivo sobre el que escribir. |
| **Valor devuelto** | Nada |
| **Funciones autorizadas** | write |

## Funciones externas (man)

> [!quote] man 2 write — DESCRIPTION / RETURN VALUE
> write() writes up to count bytes from the buffer starting at buf to the file referred to by the file descriptor fd.
>
> On success, the number of bytes written is returned.  On error, -1 is returned, and errno is set to indicate the cause of the error.

> [!note] Traducción
> write() escribe hasta count bytes del buffer que empieza en buf en el fichero al que hace referencia el descriptor de fichero fd.
>
> Si tiene éxito, devuelve el número de bytes escritos. En caso de error, devuelve -1 y pone en errno la causa del error.

## Cómo implementarla

```text
1. Copia n en un long nb (para que -INT_MIN quepa).
2. Si nb < 0: escribe '-' y haz nb = -nb.
3. Si nb >= 10: llámate a ti misma con nb / 10   (escribe todas las cifras menos la última).
4. Escribe el carácter (nb % 10) + '0'            (la última cifra).
```

Alternativa sin `long`: si `n == INT_MIN`, escribe la cadena `"-2147483648"` y sal.

> [!note] Recursión con `long`
> El prototipo recibe `int`, así que para recurrir con un `long` necesitas una función auxiliar `static` que reciba `long`, o tratar `INT_MIN` aparte al principio.

## Puntos clave y casos límite

- Recursivo: `ft_putnbr_fd(n / 10, fd)` y luego `ft_putchar_fd(n % 10 + '0', fd)`.
- Trata `INT_MIN` aparte o usa `long`.

> [!danger] El caso `INT_MIN`
> `-2147483648` no tiene opuesto en `int` (el máximo es 2147483647). Hacer `n = -n` con ese valor es desbordamiento con signo: comportamiento indefinido, y en la práctica `n` sigue siendo negativo y se imprimen caracteres basura. Ver [[Tipos enteros y conversiones]].

> [!warning] Errores típicos
> - **Olvidar el caso `0`**: con un bucle `while (n > 0)` no se escribe nada. La versión recursiva de arriba sí lo cubre (escribe `'0'`).
> - **Escribir el `'-'` en cada llamada recursiva**: compruébalo solo una vez, antes de recurrir (o deja que solo entre en la rama negativa la primera vez, porque después `nb` ya es positivo).
> - **Escribir el número directamente**: `write(fd, &n, 4)` manda los 4 bytes binarios del `int`, no los dígitos en texto.
> - **Caso base mal puesto**: sin `if (nb >= 10)`, la recursión no termina (`0 / 10` es `0` para siempre) → *stack overflow*.

## Relacionadas

[[ft_putchar_fd]] · [[ft_itoa]] · [[Recursión]] · [[Tipos enteros y conversiones]] · [[Descriptores de fichero y read]]

## Referencias

- Subject de libft v19.3 (`es.subject_libft.pdf`) — descripción, parámetros y valor devuelto, copiados literalmente.
- `man 2 write` (Linux man-pages 5.10, Ubuntu 22.04), con traducción propia — versión en línea: [write(2) en man7.org](https://man7.org/linux/man-pages/man2/write.2.html).
