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
git stash drop  stash@{n}   # Remove a specific stash entry from the list
git stash pop               # apply the stash and then immediately drop it
git stash -u                # --include-untracked
git stash branch <branch>   # create a new branach with the stash changes and drops the stash
```

> You can save a stash on one branch, switch to another branch later, and try to reapply the changes.

## Squashing Commits

It’s also possible to take a series of commits and squash them down into a single commit with the interactive rebasing tool.

```sh
git rebase -i HEAD~n
```

debo dejar el commit más reciente en **pick** y los demás en **squash**
