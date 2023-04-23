# Contributing to a Project

## Forking Projects

If you want to contribute to an existing project to which you don’t have push access, you can “fork” the project. When you “fork” a project, GitHub will make a copy of the project that is entirely yours; it lives in your namespace, and you can push to it.

People can fork a project, push to it, and contribute their changes back to the original repository by creating what’s called a **Pull Request**.

Here’s how it generally works:
1. Fork the project.
1. Create a topic branch from master.
1. Make some commits to improve the project.
1. Push this branch to your GitHub project.
1. Open a Pull Request on GitHub.
1. Discuss, and optionally continue committing.
1. The project owner merges or closes the Pull Request.
1. Sync the updated master back to your fork.

	
> Though **Pull Requests** are used commonly for public projects like this when the contributor has a complete change ready to be made, it’s also often used in internal projects at the beginning of the development cycle. Since you can keep pushing to the topic branch even after the Pull Request is opened, it’s often opened early and used as a way to iterate on work as a team within a context, rather than opened at the very end of the process.

## Keeping up with Upstream

Si por alguna razón mi PR está desactualizado de la rama a la que quiero hacer merge, debo primero traerme los cambios de la rama principal a mi rama. Para ello debo:
1. Pasarme a la rama principal y hacer `pull`
1. Pasarme a mi rama y hacer merge con la rama principal
1. Solucionar cualquier posible conflicto.
1. Hacer un nuevo `push`

# Special Files

## README

If GitHub sees a `README` or `README.md` file in your source, it will render it on the landing page of the project.

Many teams use this file to hold all the relevant project information for someone who might be new to the repository or project. This generally includes things like:

* What the project is for
* How to configure and install it
* An example of how to use it or get it running
* The license that the project is offered under
* How to contribute to it

## CONTRIBUTING

if you have a file named `CONTRIBUTING` with any file extension, GitHub will show a message when anyone starts opening a Pull Request.

The idea here is that you can specify specific things you want or don’t want in a Pull Request sent to your project. This way people may actually read the guidelines before opening the Pull Request.

## VERSION

A file that indicate the version of repository on the landing page of the project.