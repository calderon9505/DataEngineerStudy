# Docker

Docker es un programa de código abierto que permite que una aplicación Linux y sus dependencias se empaqueten como un contenedor.

> Docker te permite **construir**, **distribuir** y **ejecutar** cualquier aplicacion en cualquier lado.

Las VM tienen el problema de que son pesadas, se repiten los archivos del OS, el arranque es lento, necesitan mantenimiento y pueden venir en muchos formatos. Docker usa **contenedores**.

![](https://raw.githubusercontent.com/philipz/docker_practice/master/_images/cmd_logic.png)

Los componentes de Docker son:
- **container**: El corazón de Docker
- **image**: Artefactos para empaquetar código
- **data volumes**: Acceso al sistema de archivos de la máquina anfitriona
- **network**: Comunicación entre contenedores o a internet.

# Intro

El **hello world** de Docker es correr un contenedor llamado "hello-world".

```sh
docker run hello-world
```

para ver los contenedores

```sh
docker ps       # running
docker ps -a    # all
```

para crear un contenedor de Ubuntu

```sh
docker run -it ubuntu
# docker run -it ubuntu bash
# -i interactive
# -t TTY (terminal)

# if I am using WSL then there is
# Ubuntu inside of Docker inside of Ubuntu inside of Windows

cat etc/lsb-release
# linux stardard base
# información de la distribución GNU/Linux
apt update
apt install lsb-release
lsb_release -a
```

Manipulando contenedores

```sh
docker run --name my-first-container hello-world
docker rename my-first-container my-first-container_old
docker rm <CONTAINER ID>
docker rm <NAME>
docker container prune # prune all containers
```

## Constrains


```
docker run --memory="100m" --cpus=0.5 <image>
```
[Runtime constraints on resources](https://docs.docker.com/engine/reference/run/#runtime-constraints-on-resources)

