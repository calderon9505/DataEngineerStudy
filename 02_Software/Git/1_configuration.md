# Configuration

you need to do this only once if you pass the `--global` option, because then Git will always use that information for anything you do on that system. If you want to override this with a different name or email address for specific projects, you can run the command without the `--global` option when you’re in that project.

Git tiene tres archivos de configuración en tres ubicaciones distintas
* `[path]/etc/gitconfig` son valores aplicados a todos los usuarios del sistema y todos sus repositorios. `--system`
* `~/.gitconfig` o `~/.config/git/config` son valores generales de mi usuario. Afecta todos mis repositorios. `--global`
* `.git/config` es específico de repositorio que se está usando. Es el que se usa por defecto. `--local`

Each level overrides values in the previous level, so values in `.git/config` trump those in `[path]/etc/gitconfig`.

```sh
# set settings
git config --global user.name "Sebastian Calderon"
git config --global user.email "calderon950527@gmail.com"
git config --global core.editor "code --wait"

# check settings
git config --list 
git config --list --show-origin
git config user.name
```

# Help

```sh
# getting help
git help <verb>     # comprehensive manual page (manpage)
git <verb> -h       # simplified helper
```

