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