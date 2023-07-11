# Revision Selection

## show

```sh
git show                    # Resumen de cambios introducidos en cada commit
git show <branch>           # Cambios del último commit de la rama especificada
git show <commit SHA>       # Cambios del commit especificado
```

## reflog

A log of where your HEAD and branch references have been for the last few months. Muestra los commits, amends, merges, rebases, switches, pulls, pushs, etc. Es un historial de las cosas que han pasado en el repositorio y que son relevantes para una revisión. No es que guarde cada comando que ejecuté, sino aquellos que son relevantes para git y que de alguna u otra manera han modificado el repositorio.


```sh
git reflog
git show HEAD@{5}   # historial de las últimas 5 cosas que han pasado
```

> You can think of the reflog as **Git’s version of shell history**, which emphasizes that what’s there is clearly relevant only for you and your “session”, and has nothing to do with anyone else who might be working on the same machine.

> It’s important to note that `reflog` information is strictly local — it’s a log only of what **you’ve** done in **your** repository. The references won’t be the same on someone else’s copy of the repository;

## Staging Patches

Para pasar al Staging zone solo una parte de un archivo y en lugar del archivo completo

```sh
git add -p      # --patch
```


## Stashing

Stashing takes the dirty state of your working directory — that is, your modified **tracked files** and staged changes — and saves it on a stack of unfinished changes that you can reapply at any time (even on a different branch).

```sh
git stash                   # Stashear mi WIP - work in progress
git stash list              # Listar mi stack de stash
git stash apply             # Aplicar stash más reciente
git stash apply stash@{n}   # aplicar stash específico
git stash apply --index     # Lo que estaba en stage vuelve a stage
git stash drop              # Remove a single stash entry from the list
git stash drop stash@{n}   # Remove a specific stash entry from the list
git stash pop               # apply the stash and then immediately drop it
git stash -u                # --include-untracked
git stash branch <branch>   # create a new branch with the stash changes and drops the stash
```

> You can save a stash on one branch, switch to another branch later, and try to reapply the changes.

## Squashing Commits

It’s also possible to take a series of commits and squash them down into a single commit with the interactive rebasing tool.

```sh
git rebase -i HEAD~n
```

debo dejar el commit más reciente en **pick** y los demás en **squash**, esto lo que hará es aplastar los demás commits en uno solo, conservando el mensaje del commit que tiene el pick. Si tambien quiero cambiar el mensaje de commit, debo escoger **reword**.


## Reset

En resumen, no es tan facil como creía, tampoco es que sea algo complicadísimo.

no considero que sea relevante aprenderlo de momento, igual puedo repasarlo en [Reset Demystified](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified).

Tambien es cierto que espero nunca tener que usarlo, y por el contrario usar `checkout` para revisar commits anteriores.

## Checkout

Si quiero revisar el estado de los archivos de un commit específico puedo usar el `checkout`.

```sh
git checkout <commit>           # ir a commit específico
git checkout master             # Volver al commit más reciente de la rama

git switch --detach <commit>    # ir a commit específico
git switch -                    # Volver a donde estaba
```

Ahora, puedo tambien restaurar un archivo a la forma que tenía en un commit específico

```sh
git checkout <commit> <file>    # "Revisar" archivo específico
git checkout master <file>      # Volverlo a dejar como estaba según la rama indicada
```

No es como tal un "revisar", sino un restaurar, ya que al hacerlo el archivo me queda como estaba en el commit indicado y tambien me queda en el staging zone listo para hacer el commit. Si se trata de revisar, siempre será mejor hacer el cambio completo al commit requerido con `switch`.


# GITFLOW

[Gitflow Workflow Tutorial](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow#:~:text=What%20is%20Gitflow%3F,lived%20branches%20and%20larger%20commits.)