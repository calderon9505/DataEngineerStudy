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

### Short Status

* **left-hand column** indicates the status of the **staging area**
* **right-hand column** indicates the status of the **working tree**
* **A** indicates new files that have been added to the staging area
* **M** indicates files that have been modified
* **??** indicates new files that aren’t tracked


## Commit Area

```sh
git commit
git commit -m "commit message"
git commit -am "commit message"     # 
```

Cada commit me indica 


## Ignoring files

El archivo `.gitignore` indica a Git los archivos que no debe rastrear. The rules for the patterns you can put in the .gitignore file are as follows:

* Blank lines or lines starting with `#` are ignored.
* Standard glob patterns (simplified regular expressions) work, and will be applied recursively throughout the entire working tree.
* Start patterns with a forward slash (`/`) to avoid recursivity.
* End patterns with a forward slash (`/`) to specify a directory.
* Negate a pattern by starting it with an exclamation point (`!`).
* Use two asterisks to match nested directories; `a/**/z` would match a/z, a/b/z, a/b/c/z, and so on.

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

