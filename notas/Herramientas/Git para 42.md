---
tags: [herramientas, git, entrega, vogsphere]
aliases: ["Git", "Vogsphere"]
---
# Git para 42

← Inicio · Herramientas

> **Git** es un programa que guarda «fotos» (versiones) de los ficheros de un proyecto y permite enviarlas a otro ordenador. En 42 se usa para **entregar**: lo que el evaluador corrige es exactamente lo que hay en el repositorio de entrega del intra (Vogsphere), no lo que tienes en tu carpeta. Si un fichero no está en el último `push`, para la evaluación no existe.

## Vocabulario

| Término | Qué significa |
|---|---|
| **Repositorio** (*repo*) | Carpeta controlada por Git. Tiene una subcarpeta oculta `.git` con todo el historial |
| **Commit** (confirmación) | Una foto de los ficheros en un momento dado, con un mensaje y un identificador (`6424f00…`) |
| **Staging area** (área de preparación) | Lista de cambios que entrarán en el próximo commit. Se llena con `git add` |
| **Remoto** | Copia del repo en otro ordenador. El de entrega se llama `origin` |
| **Push** | Enviar tus commits al remoto |
| **Clone** | Descargar una copia de un remoto |
| **Rama** (*branch*) | Línea de commits. Para entregar basta con la rama principal (`master` o `main`) |
| **Vogsphere** | El servidor Git de 42 donde se entregan los proyectos |

## Los tres sitios de un fichero

```text
 carpeta de trabajo         staging            repositorio local         remoto (Vogsphere)
 (lo que editas)      →    (git add)    →      (git commit)       →      (git push)
   ft_strlen.c             ft_strlen.c          commit 6424f00            lo que se evalúa
```

Hasta que no haces los tres pasos, el evaluador no ve tu cambio.

## Paso 1: clonar el repositorio de entrega

En la página del proyecto en el intra aparece la URL del repositorio (empieza por `git@vogsphere…`). Para poder usarla, tu **clave SSH pública** (`~/.ssh/id_ed25519.pub` o `id_rsa.pub`) tiene que estar añadida en los ajustes de tu perfil del intra.

```bash
ssh-keygen -t ed25519           # solo si no tienes clave; acepta las opciones por defecto
cat ~/.ssh/id_ed25519.pub       # copia esto en el intra
git clone <URL-del-intra> libft
cd libft
```

> [!warning] Comprueba el subject y el intra
> El flujo exacto (dónde aparece la URL, si el repo se crea al inscribirte, cuándo se cierra) depende del campus y cambia con el tiempo. Lo que manda es lo que veas en tu intra y el PDF del proyecto.

Si ya tenías el proyecto en otra carpeta, copia los ficheros dentro de la carpeta clonada (sin copiar otra carpeta `.git`).

## Paso 2: el ciclo de trabajo

```bash
git status                      # ¿qué ha cambiado?
git add ft_strlen.c libft.h     # preparar ficheros concretos
git commit -m "Añade ft_strlen"
git push                        # enviar al remoto
```

Pon tu nombre una vez por ordenador para que los commits salgan firmados:

```bash
git config --global user.name "tu_login"
git config --global user.email "tu_login@student.42barcelona.com"
```

> [!tip] Commits pequeños y a menudo
> Haz commit cada vez que algo funcione («ft_split pasa los tests»). Si luego lo rompes, puedes volver atrás. Y haz `push` a menudo: si el ordenador del clúster se reinicia, tu trabajo está a salvo.

## Ver qué pasa: `status`, `log`, `diff`

`git status` es el comando que más vas a usar. Ejemplo real con ficheros que **no** deben entregarse:

```text
$ git status
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.ft_suma.c.swp
	Makefile
	a.out
	ft_suma.c
	ft_suma.o

nothing added to commit but untracked files present (use "git add" to track)
```

`git log --oneline` enseña el historial, un commit por línea:

```text
$ git log --oneline
2399699 Quita ft_suma.o del repo
4d4d25d oops
6424f00 Añade ft_suma y Makefile
```

`git diff` enseña qué has cambiado y aún no has preparado (`-` línea quitada, `+` línea añadida):

```text
$ git diff
diff --git a/ft_suma.c b/ft_suma.c
--- a/ft_suma.c
+++ b/ft_suma.c
@@ -1,4 +1,4 @@
 int	ft_suma(int a, int b)
 {
-	return (a + b);
+	return (a - b);
 }
```

`git diff --staged` hace lo mismo con lo que ya está en staging.

## `.gitignore`: no entregar basura

El subject pide entregar solo los ficheros fuente, el header y el Makefile. Los `.o`, `.a`, ejecutables y ficheros temporales de Vim (`.swp`) **no** deben estar en el repo. El fichero `.gitignore` le dice a Git qué ignorar:

```text
# .gitignore
*.o
*.a
a.out
*.swp
*.swo
.DS_Store
```

Con ese `.gitignore`, el mismo `git status` queda limpio:

```text
$ git status --short
?? .gitignore
?? Makefile
?? ft_suma.c
```

> [!info] ¿Se puede entregar el `.gitignore`?
> Es un fichero más del repo. La mayoría de evaluadores lo aceptan, pero algunos subjects son estrictos con «solo los ficheros pedidos». Si dudas, pregunta o léete el apartado de entrega del PDF.

> [!warning] `git add .` sin `.gitignore`
> `git add .` añade **todo** lo de la carpeta, incluidos `a.out`, el `main.c` de pruebas y la carpeta de tests. Revisa siempre `git status` antes de hacer commit.

## Deshacer errores comunes

| Situación | Comando |
|---|---|
| Quiero descartar los cambios de un fichero (volver a como estaba en el último commit) | `git restore ft_split.c` ⚠️ se pierden |
| Hice `git add` de un fichero que no quería | `git restore --staged a.out` |
| Ya hice commit de un `.o` y quiero quitarlo del repo (sin borrarlo del disco) | `git rm --cached ft_suma.o` y luego commit |
| El mensaje del último commit está mal (y aún no hice push) | `git commit --amend -m "Mensaje bueno"` |
| Olvidé un fichero en el último commit (sin push) | `git add olvido.c` y `git commit --amend --no-edit` |
| Quiero deshacer el último commit pero conservar los cambios | `git reset --soft HEAD~1` |
| Quiero ver un fichero como estaba en un commit antiguo | `git show 6424f00:ft_suma.c` |

Ejemplo real de quitar un `.o` que se coló:

```text
$ git ls-files
.gitignore
Makefile
ft_suma.c
ft_suma.o
$ git rm --cached ft_suma.o
rm 'ft_suma.o'
$ git commit -m "Quita ft_suma.o del repo"
$ git ls-files
.gitignore
Makefile
ft_suma.c
```

> [!danger] No reescribas lo que ya has enviado
> `--amend` y `reset` cambian commits. Si ya hiciste `push`, Git rechazará el siguiente `push` y tendrías que forzarlo. No lo hagas: crea un commit nuevo que arregle el anterior.

## Comprobar qué se entrega

Antes de pedir evaluación, haz estas dos comprobaciones.

### `git ls-files`

Lista los ficheros que **están en el repositorio** (no los que hay en la carpeta). Es lo que verá el evaluador:

```bash
git ls-files
git status          # debe decir "nothing to commit, working tree clean"
git log origin/master --oneline -1   # el último commit que tiene el remoto
```

Si `git status` dice `Your branch is ahead of 'origin/master' by 2 commits`, te falta un `push`.

### Clonar de nuevo en otra carpeta

Es la prueba definitiva: simula exactamente lo que hará el evaluador.

```bash
cd /tmp
rm -rf prueba_entrega
git clone <URL-del-intra> prueba_entrega
cd prueba_entrega
ls -a
make && make clean && make fclean && make re
norminette
```

Así detectas los fallos clásicos:

- Un `.c` que existe en tu carpeta pero nunca añadiste (el Makefile falla con `No rule to make target`).
- El header en una ruta distinta a la que espera el Makefile.
- Un `.o` o un `a.out` entregado por error.
- Ficheros con nombres distintos a los del subject (mayúsculas, carpetas).

> [!summary] Checklist antes de la evaluación
> 1. `git status` limpio y sin commits pendientes de `push`.
> 2. `git ls-files` solo enseña lo que pide el subject.
> 3. Clon nuevo en otra carpeta: compila con `make`, sin relink, y pasa la [[La Norma|norminette]].
> 4. Nombres de ficheros y de la librería exactamente como en el subject.

## Relacionadas

[[Makefile y librerías estáticas]] · [[La Norma]] · Vim · Cómo compila C · [[libft - Índice]] · Exam Rank 02

## Referencias

- [Pro Git (es) — Obteniendo un repositorio Git](https://git-scm.com/book/es/v2/Fundamentos-de-Git-Obteniendo-un-repositorio-Git) — `git init` y `git clone`.
- [Pro Git (es) — Guardando cambios en el Repositorio](https://git-scm.com/book/es/v2/Fundamentos-de-Git-Guardando-cambios-en-el-Repositorio) — ciclo de vida de un fichero, `status`, `add`, `diff`, `commit`, `.gitignore`, `git rm --cached`.
- [Pro Git (es) — Ver el Historial de Confirmaciones](https://git-scm.com/book/es/v2/Fundamentos-de-Git-Ver-el-Historial-de-Confirmaciones) — `git log` y sus opciones.
- [Pro Git (es) — Deshacer Cosas](https://git-scm.com/book/es/v2/Fundamentos-de-Git-Deshacer-Cosas) — `commit --amend`, sacar ficheros del staging, descartar cambios.
- [Pro Git (es) — Trabajar con Remotos](https://git-scm.com/book/es/v2/Fundamentos-de-Git-Trabajar-con-Remotos) — `origin`, `push`, `fetch`.
- [git-scm — gitignore](https://git-scm.com/docs/gitignore) — sintaxis de patrones del `.gitignore`.
- [git-scm — git-ls-files](https://git-scm.com/docs/git-ls-files) — listar los ficheros del índice.
- [git-scm — git-restore](https://git-scm.com/docs/git-restore) — `git restore` y `--staged`.
- [github/gitignore — C.gitignore](https://github.com/github/gitignore/blob/main/C.gitignore) — plantilla de patrones habituales para proyectos en C.
- Salidas reales generadas con git 2.34.1 en Ubuntu 22.04.
