# API

Application Programming Interface

Una interfaz de programación de aplicaciones API es un **conjunto de reglas** que define cómo se comunican dos máquinas entre sí. Las API permiten que las aplicaciones intercambien datos y funcionalidades de manera fácil y segura.

* Las APIs de tipo **locales** son, por ejemplo, Python. Python tiene su API (con métodos) para realizar tareas predefinidas como la escritura en disco

* Las APIs de tipo **remotas** usan servicios web que pueden ser SOAP o REST. Cuando se crea un sitio web usando REST se dice que es RESTful

## REST API

Una API REST (API de transferencia de estado representacional) es una interfaz de programación de aplicaciones que se ajusta a los principios de diseño del estilo arquitectónico de transferencia de estado representacional (REST). Las API REST permiten que dos sistemas de computación intercambien información de manera segura a través de **Internet**. Las API REST permiten crear aplicaciones web o móviles en un servidor para que los clientes se conecten usando dicha interfaz

> REST es la arquitectura, HTTP es el protocolo. La arquitectura se basa en el protocolo para poder ejecutarse

> http se basa en comunicación cliente-servidor, donde un cliente realiza un **request** al servidor y recibe un **response**

## Propiedades REST

Todo en la web es un **recurso** y debe:
* Tener un identificador único (URI)
* Estar representado por un formato (XML, JSON, JPEG)
* Poderse representar con diferentes formatos

> cada imagen, cada archivo (html, css, js), cada video, etc. son recursos

> **Las comunicaciones no tienen estado**. es decir, cada petición es completamente indepentiende de las otras.

### URI vs URL vs URN

![](https://www.researchgate.net/profile/Harri-Valkonen-2/publication/346585530/figure/fig4/AS:987488491417601@1612447011264/The-illustration-of-the-URL-URN-and-URI-26.png)

Las URL son los localizadores de los recursos. Las URN son los nombres de los recursos.

* la dirección `https://ed.team/cursos/conceptos-de-api` es la que me identifica el recurso en la web.
* la url tambien podría tener subdominios como `https://mySubdomain.ed.team/cursos`
* todo lo que viene despues del dominio se le llama la ruta (path)
* el primer `/` despues de la ruta es la raiz
* el signo `?` identifica los parámetros de consulta, los cuales sirven para darle filtros. `https://ed.team/cursos?nombre=conceptos+de+api`

Una URI (Uniform Resource Identifier) es una cadena de caracteres que identifica un recurso particular, ya sea físico o abstracto, de manera única en un sistema. En otras palabras, una URI es una secuencia de caracteres que proporciona un identificador universal para localizar un recurso en la web o en cualquier otro sistema de información.

Una URI puede identificar varios tipos de recursos, incluyendo:

* Recursos web, como páginas HTML, imágenes, archivos de audio o video, servicios web, etc.
* Recursos en sistemas de archivos, como archivos locales en un sistema operativo.
* Recursos en bases de datos, como registros individuales o consultas específicas.
* Recursos abstractos, como identificadores de objetos en sistemas de software.

Un **endpoint** es un punto de acceso específico en la API. Este punto de acceso es utilizado para realizar operaciones específicas, como obtener datos, enviar datos, actualizar recursos, eliminar recursos, entre otras acciones. un endpoint suele representar una URL única que corresponde a una función o conjunto de funciones específicas proporcionadas por la API. Cada endpoint está asociado con un método HTTP (como GET, POST, PUT, DELETE, etc.) que determina la acción que se realizará en el recurso identificado por esa URL.

Por ejemplo, en una API de gestión de usuarios, podrías tener los siguientes endpoints:

* **GET /usuarios**: Para obtener una lista de usuarios.
* **GET /usuarios/{id}**: Para obtener los detalles de un usuario específico.
* **POST /usuarios**: Para crear un nuevo usuario.
* **PUT /usuarios/{id}**: Para actualizar los datos de un usuario existente.
* **DELETE /usuarios/{id}**: Para eliminar un usuario existente.

Cada uno de estos endpoints representa una operación específica que puede realizarse en el sistema a través de la API, y cada uno está asociado con una URL única y un método HTTP específico.

### CONTENT TYPES

* text/plain
* text/html
* text/xml
* application/json
* image/jpeg
* image/png

### Cookies y Tokens

Forma de hacer que las comunicaciones sin estado como API REST HTTP, mantengan un estado. Son cadenas de caracteres que sirven para verificar un estado, por ejemplo, un inicio de sesion. El token o cookie que recibe el cliente, debe usarlo posteriormente en cada petición que realice al servidor.

las cookies se usan principalmente en navegadores. Los tokens se usan tanto en navegadores como en aplicaciones backend.

> JWT es el formato más común para tokens. Json Web Token

### Idempotencia

La idempotencia es una propiedad de ciertas operaciones o solicitudes de API que garantiza que realizar la operación varias veces arrojará el mismo resultado que si se ejecutara solo una vez.

* GET, PUT Y DELETE son idempotentes
* POST no es idempotente

### HATEOAS

HATEOAS (Hypertext As The Engine Of Application State) es un principio de diseño de arquitectura de aplicaciones web, especialmente en el contexto de servicios web RESTful. Este principio establece que la interacción entre clientes y servidores debe ser conducida principalmente a través de hipervínculos (enlaces), permitiendo que el estado de la aplicación sea descubierto y navegado dinámicamente por el cliente.

En otras palabras, en una arquitectura HATEOAS, el servidor **NO solo proporciona datos al cliente**, sino también información sobre qué acciones o recursos están disponibles y cómo interactuar con ellos. Esto se logra mediante la inclusión de enlaces hipertexto en las respuestas del servidor, que guían al cliente a través de la aplicación web de manera dinámica.

Por ejemplo, en una API RESTful que implementa HATEOAS, una respuesta que devuelve información sobre un recurso podría incluir enlaces a otros recursos relacionados o acciones que el cliente puede realizar en ese contexto. Estos enlaces proporcionan al cliente la capacidad de descubrir y navegar dinámicamente por la aplicación, sin necesidad de tener un conocimiento previo de la estructura de la API.

El principio de HATEOAS promueve una arquitectura de API más flexible, escalable y autodescriptiva, lo que facilita la evolución y el mantenimiento de las aplicaciones a lo largo del tiempo. Además, permite a los clientes adaptarse dinámicamente a los cambios en la aplicación sin necesidad de una lógica de negocio rígida o predefinida

```json
{
  "nombre": "Producto 1",
  "descripcion": "Descripción del Producto 1",
  "precio": 20.00,
  "_links": {
    "self": {
      "href": "/productos/1"
    },
    "comprar": {
      "href": "/productos/1/comprar"
    },
    "similar": [
      { "href": "/productos/2", "titulo": "Producto 2" },
      { "href": "/productos/3", "titulo": "Producto 3" }
    ]
  }
}
```

* "**nombre**", "**descripcion**" y "**precio**" son datos básicos del producto.
* "**_links**" es una sección especial que contiene enlaces relevantes.
* "**self**" es un enlace a la misma URL que representa este producto.
* "**comprar**" es un enlace que indica cómo el cliente puede comprar este producto.
* "**similar**" es un arreglo de objetos que proporciona enlaces a productos similares, cada uno con su respectiva URL y título.