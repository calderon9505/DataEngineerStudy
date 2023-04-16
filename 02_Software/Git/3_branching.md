[Learn Git Branching](https://learngitbranching.js.org/)

# Branch Basic

En Git se pueden entender las ramas como punteros a los commit. 

> Existe un puntero especial **HEAD** el cual apunta a la rama sobre la que estoy parado.

```sh
git branch <branchname>         # create branch

git checkout <branchname>       # switch to branch
git checkout -b <branchname>    # create and switch

# from Git version 2.23 onwards 
git switch <branchname>         # switch to branch
git switch -c <branchname>      # create and switch (--create)
git switch -                    # switch to previous branch
```

![](https://git-scm.com/book/en/v2/images/advance-master.png)



# Merging

Ubicandome sobre la rama que va a recibir los cambios (la principal), realizo el `merge` con la rama tiene los cambios.

```sh
git merge <branchname>
```


## fast-forward

Git simply moves the pointer forward because there is no divergent work to merge together.

![](https://git-scm.com/book/en/v2/images/basic-branching-4.png)
![](https://git-scm.com/book/en/v2/images/basic-branching-5.png)

## recursive

Git creates a new commit that has two parents. This is a **merge commit**.

![](https://git-scm.com/book/en/v2/images/basic-merging-2.png)



# management

```sh
git branch                          # list current branches
git branch --merged                 # branches already merged into the branch you’re on
git branch --no-merged              # branches already NOT merged into the branch you’re on
git branch --merged <branchname>    # branches already merged into the branch selected
git branch -d <branchname>          # delete fully merged branch (--delete)
git branch -D <branchname>          # delete branch (even if not merged)
git branch -a                       # list both remote-tracking and local branches (--all)
```

Para cambiar nombre a una rama tanto en local como remoto

```sh
git branch --move <old-branch-name> <new-branch-name>   # en local
git push --set-upstream origin new-branch-name          # en remoto
git push origin --delete old-branch-name                # la rama old remota se debe borrar manualmente
```

# Remote Branches

Cuando clono un repositorios, automáticamente se crea un "remoto" nombrado **origin**, y la rama master del remoto será nombrada **origin/master**.

![](https://git-scm.com/book/en/v2/images/remote-branches-1.png)

As long as you stay out of contact with your origin server, your **origin/master** pointer doesn’t move.

![](https://git-scm.com/book/en/v2/images/remote-branches-2.png)

Al clonar un repositorio, se crea un rastreo de todas las ramas de dicho repositorio. Sin embargo, localmente solamente tengo creada la rama **master**. Al cambiarme a alguna de las ramas `git switch develop` se crea en mi repositorio local la rama **develop**, a la cual ya puedo hacerle modificaciones y queda lista para hacer `push` u `pull`.

Si tengo commits en alguna rama local que no se han subido (push) al remoto, se dice que mi rama está **ahead**. Por el contrario si la rama remota tiene cambios que no he bajado (pull) al local, se dice que mi rama está **behind**. Es perfectamente posible que mi rama esté ahead y behind a la vez, por lo que debo actualizar mi rama local (merge) para que mis cambios esten al día con los últimos cambios del remoto. El número de aheads y behinds que me muestra git corresponde a la última vez que bajé cambios (bajardos con fetch, porque con pull siempre se hace merge y por tanto nunca estaría behind).

> Generally it’s better to simply use the `fetch` and `merge` commands explicitly as the magic of `git pull` can often be confusing.

