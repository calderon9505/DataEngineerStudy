# AWS VPN

Connect your on-premises networks and remote workers to the cloud

### AWS Client VPN

Service used by remote workforce to securely access resources both on AWS and within on-premises networks.

### AWS Site-to-Site VPN

Service to create encrypted connections between own data centers and AWS resources.


# AWS Direct Connect

Dedicated network connection to AWS

Conexión Física a AWS (infraestructura, redes, tráfico, dispositivos) sin pasar por infraestructuras públicas. Require a Delivery Partner.

* Improve application performance because the connection to AWS is direct, bypassing the public internet
* Secure data as it moves betweeen my network and AWS with encryption


# VPC

Servicio para crear redes privadas virtuales, esto es, redes lógicamente aisladas.

* Pertenecen a una región
* Contiene una o varias subredes
    * Las subredes pertencen a una única Availability zone
    * Las subredes pueden ser públicas o privadas

![](https://docs.aws.amazon.com/images/vpc/latest/userguide/images/how-it-works.png)

### Elastic IP

An Elastic IP address is a static and public IPv4 address, which is reachable from the internet. Es la forma de salir a internet.

* An Elastic IP address is allocated to your AWS account, and is yours until you release it.
* By using an Elastic IP address, you can mask the failure of an instance or software by rapidly remapping the address to another instance in your account.
* Small hourly charge if an Elastic IP address is not associated with a running instance

> Starting on February 1, 2024, AWS will charge for all public IPv4 addresses, including public IPv4 addresses associated with running instances and Elastic IP addresses.

### Route tables

Cada subred debe estar asociada con una única tabla de enrutamiento, la cual se usa para saber hacia donde redigirir el tráfico.
* Por defecto las subredes traen una ruta que permite la comunicación interna en dicha subred
* Las redes públicas usan un gateway para conectarse a internet
* Las redes privadas usan un NAT gateway para conectarse a internet. You can use a NAT gateway so that instances in a private subnet can connect to services outside your VPC but external services cannot initiate a connection with those instances.
* Para comunicar distintas VPCs será necesario que sus tablas de enrutamiento estén correctamente configuradas mediante un punto de interconexión


### AWS Transit Gateway

Cuando se tiene muchas VPCs y se quire interconectarlas


# Security

Grupos de Seguridad Vs ACL de red. Ambos son tablas en que se indican origenes y destinos con números de puertos para indicar si las comunicaciones se aceptan o no.

| | Grupos de Segudidad | ACL de red 
| --- | --- | --- 
| Alcance | Nivel de instancia | Nivel de subred 
| Reglas admitidas | solo reglas de permiso | reglas de permiso y denegación 
| Estado | Con estado (el tráfico de retorno se permite automáticamente, es decir, si permito la conexión es para poder contestar) | Sin estado (se debe permitir tanto la regla de entrada como de salida)
| orden de las reglas | Se evaluan todas las reglas antes de decidir si se permite el tráfico | Las reglas se evalúan según el orden, si encuentra una regla que cumpla no se evaluan el resto


# Route 53 (DNS)

Servicio de DNS de AWS. El puerto que se usa para conectarse a los DNS es el 53. El direccionamiento puede ser sencillo (un solo servidor), basado en latencia, geolocalización o geoproximidad, por turnos rotativos ponderados, tras conmutación por errores o en respuesta a varios valores. 