# Getting a Git Repository

```sh
git init        # creates a Git repository skeletonnew (subdirectory named .git)
git clone <url> # creates a directory and initializes a .git directory inside it
```



# Recording Changes to the Repository

Each file in the working directory can be in one of two states: tracked or untracked. Tracked files are files that were in the last snapshot, as well as any **newly staged files**; they can be unmodified, modified, or staged. In short, tracked files are files that Git knows about.

![](https://git-scm.com/book/en/v2/images/lifecycle.png)

## Staging Area

```sh
git status          # estado de los archivos
git status -s       # estado de los archivos simplificado (--short)
git add <file>      # pasar a estado Staged
```

### Short status

* **left-hand column** indicates the status of the **staging area**
* **right-hand column** indicates the status of the **working tree**
* **A** indicates new files that have been added to the staging area
* **M** indicates files that have been modified
* **??** indicates new files that aren’t tracked


## Commit Area

```sh
git commit
git commit -m "commit message"
git commit -a
git commit -am "commit message"     # 
```

Adding the `-a` option makes Git automatically stage every file that is **already tracked** before doing the commit, letting you skip the git add part.


## Comparations

```sh
git diff
```

Compares *working directory* VS *staging area*. The result shows the changes haven’t yet staged. It’s important to note that git diff by itself doesn’t show all changes made since your last commit — only changes that are still unstaged. If you’ve staged all of your changes, `git diff` will give you no output.

```sh
git diff --staged
```

Compares *staging area* VS *last commit*. The result shows the changes you’ve staged that will go into your next commit. (`--staged` and `--cached` are synonyms)

> Git Diff in an External Tool. `git difftool`




## Removing Files

```sh
rm <file>
git rm <file>
```

Al remover el archivo sin usar git será puesto en la zona **Modified**, al removerlo usando git será puesto en la zona **Staged**.


## Ignoring Files

El archivo `.gitignore` indica a Git los archivos que no debe rastrear. The rules for the patterns you can put in the .gitignore file are as follows:

* Blank lines or lines starting with `#` are ignored.
* Standard glob patterns (simplified regular expressions) work, and will be applied recursively throughout the entire working tree.
* Start patterns with a forward slash (`/`) to avoid recursivity.
* End patterns with a forward slash (`/`) to specify a directory.
* Negate a pattern by starting it with an exclamation point (`!`).
* Use two asterisks to match nested directories; `a/**/z` would match a/z, a/b/z, a/b/c/z, and so on.





# Viewing the Commit History

```sh
git log             # commit history
git log -p          # shows the differences (--patch)
git log -2          # number of log entries
git log --stat      # statistics of logs
git log --oneline   # checksum and commit message
git log -- <path/to/file> # commits that introduced changes to that file
```

`git log` tiene muchas caracteristicas útiles como `--pretty` que permite dar formato al historial de commits.

> `git log` only show commit history below the branch you’ve checked out. To show commit history for the desired branch you have to explicitly specify it: `git log testing`. To show all of the branches, add `--all` to your git log command.


# Undoing Things

## Amend commit

```sh
git commit --amend
```

`--amend` es un corrector del último commit, el cual adicionará lo que tenga en el **staging area** al commit. Tambien me sirve si lo que quiero es corregir el mensaje del commit. Al ejecutarlo me permite *editar* el mensaje de commit incorrecto.

> Only amend commits that are still local and have not been pushed somewhere.


## Discarding changes

```sh
git restore <file>          # to discard changes in working directory
git restore --staged <file> # to unstage
```



# Working with Remotes

A cloned repository has **origin** as the default remote server name.

```sh
git remote
git remote -v
git remote add <shortname> <url>
```

Ahora puedo traer los cambios del servidor remoto añadido usando el `shortname`, el cual ahora llamaré `remote`.

```sh
git fetch <remote>
```

Con `fetch` me traigo la rama master del remoto y queda accesible como `<remote>/master`. Importante notar que `fetch` solo descarga los datos a mi repositorio local, pero no hace merge ni modifica mi trabajo actual. El merge lo debo hacer manualmente.

```sh
git pull <remote> <branch>
```

Se puede configurar una rama para **rastrear** una rama remota, y así usar `git pull` para traer los datos de una rama y hacer merge a la vez. Al clonar un repositorio se estableceme la rama master local para que rastree la rama master remota automáticamente.

```sh
git push <remote> <branch>
```

`push` command works only if you cloned from a server to which you have write access and if nobody has pushed in the meantime.


```sh
git remote show origin
```

To see more information about a particular remote. Muestra las ramas e indica si está rastreada, si la rama es nueva y yo no la tengo en mi local, si la tengo en local pero ya no existe en el remoto, etc. Tambien indica hacia donde conectan los push y pull.



# Aliases

```sh
git config --global alias.<alias> <command>
```

Se usa para crear atajos a comandos que puedan resultar útiles. por ejemplo, un alias para abrir el entorno visual de git (`gitk`) con un nombre más intuitivo `git visual`: `git config --global alias.visual '!gitk'`
