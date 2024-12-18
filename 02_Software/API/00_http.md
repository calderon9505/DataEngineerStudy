# HTTP

Es un protocolo de la capa de aplicación para la transmisión de documentos hipermedia, como HTML.

Existen otros protocolos como:
* **smtp**: (Simple Mail Transfer Protocol) es un protocolo de red estándar que permite enviar y recibir correos electrónicos a través de Internet
* **ssh**: (Secure Shell) es un protocolo de red que permite conexiones encriptadas para iniciar sesión de forma remota y transferir archivos entre ordenadores. SSH también permite la ejecución de comandos, el control de acceso y el reenvío de TCP/IP.

## METODOS (VERBOS) HTTP

* **GET**: Obtener información
* **POST**: Enviar informacion. Crear nuevos recursos
* **PUT**: Actualizar un recurso (Actualiza todo el recurso)
* **DELETE**: Borrar un recurso
* **PATCH**: Actualizar un recurso (Actualiza parte del recurso)
* **HEADER**: Consultar la existencia de un recurso
* **OPTIONS**: Validar peticiones entre dominios.

Las peticiones OPTIONS son utilizadas para permitir que un cliente determine qué métodos HTTP son soportados por el servidor para un recurso en particular. Cuando un cliente envía una petición OPTIONS a un recurso en el servidor, el servidor responde con una lista de métodos HTTP y opciones permitidas para ese recurso. 

Además, las peticiones OPTIONS también son útiles para permitir el acceso CORS (Cross-Origin Resource Sharing) en aplicaciones web. El servidor puede incluir encabezados CORS en la respuesta a la petición OPTIONS para indicar qué **origenes externos** tienen permiso para acceder al recurso.

Las peticiones OPTIONS no son exclusivas de los navegadores. Aunque son comúnmente utilizadas en el contexto de aplicaciones web y navegadores, pueden ser empleadas por cualquier tipo de cliente que interactúe con un servidor HTTP, esto puede incluir clientes programáticos, herramientas de desarrollo, aplicaciones móviles, servicios web y muchos otros tipos de aplicaciones que se comunican a través de HTTP.

## CORS

CORS (Cross-Origin Resource Sharing) es un **mecanismo de seguridad** implementado en los navegadores web para controlar las solicitudes de recursos (como datos, scripts, estilos, etc.) entre diferentes orígenes en la web.

Un "origen" en el contexto de CORS se define como una *combinación de protocolo, dominio y puerto*. Por ejemplo, http://ejemplo.com:80 es un origen diferente de https://ejemplo.com:443. Si una solicitud proviene de un origen diferente al del recurso al que intenta acceder, se considera una solicitud de "origen cruzado" y puede estar sujeta a restricciones de seguridad.

CORS permite que los servidores indiquen de manera explícita a los navegadores si una solicitud de origen cruzado debería ser permitida. Esto se logra mediante el uso de encabezados HTTP especiales en las respuestas del servidor, como "Access-Control-Allow-Origin", que especifica qué orígenes tienen permiso para acceder al recurso.

Las peticiones OPTIONS son relevantes en el contexto de CORS porque se utilizan para realizar "preflights" (o pre-vuelos), que son solicitudes de prueba enviadas automáticamente por el navegador antes de realizar solicitudes más complejas (como POST, PUT, DELETE) de origen cruzado. El servidor puede responder a estas solicitudes OPTIONS incluyendo encabezados CORS en la respuesta, lo que permite al navegador determinar si la solicitud principal de origen cruzado debe ser permitida o denegada.

En resumen, CORS es un mecanismo que permite a los servidores controlar el acceso a recursos desde orígenes diferentes en la web, y las peticiones OPTIONS son parte del proceso mediante el cual los navegadores y servidores negocian y establecen permisos para solicitudes de origen cruzado.

## CÓDIGOS DE RESPUESTA

* **1xx**: Informativos (suelen venir configurados en las librerías)
* **2xx**: Correcto
* **3xx**: Redirección
* **4xx**: Error del cliente (consulta a dirección inexistente, peticion mal hecha, ...)
* **5xx**: Error del servidor (bases de datos caidas, error del gateway, ...)

