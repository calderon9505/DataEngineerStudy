# Aplicaciones Web Serverless

## Amazon Lightsail

Entorno para crear aplicaciones y sitios web rápidamente con recursos preconfigurados


## AWS Elastic Beanstalk

> Es un PaaS.

Ya teniendo un código listo se crea una aplicación web en Beanstalk para ejecutar dicho código.

Se crea toda la infraestructura pero yo no me preocupo de ello. Me crea una URL para acceder a la página web.

Se tiene sistema de versiones.


# Balanceadores de carga

Si lo que quiero es Alta disponibilidad lo que debo hacer es que mi sistema esté implementado en más de una zona. 

Si lo que quiero es Eficiencia lo que debo hacer es dotar mi sistema con la capacidad de escalar, ya sea vertical (scale up and down) u horizontalmente (scale out and in).

Tanto para la Alta disponibilidad como para la Eficiencia lo que requiero es un Balanceador que me permita gestionar el tráfico de la manera adecuada.

Tipos de balanceadores

* Application Load Balancer
    * Capa 7 nivel OSI
    * protocolo HTTP, HTTPS, etc
* Network Load Balancer
    * Capa 4 nivel OSI
    * Protocolo TCP y UDP
* Gateway Load Balancer
    * Gateway de capa 3
    * Balanceo de carga de capa 4
    
## Auto Scaling Group (ASG)

An Auto Scaling group contains a collection of EC2 instances that are treated as a logical grouping for the purposes of automatic scaling and management. An Auto Scaling group also lets you use Amazon EC2 Auto Scaling features such as **health check replacements** and **scaling policies**. Both maintaining the number of instances in an Auto Scaling group and automatic scaling are the core functionality of the Amazon EC2 Auto Scaling service.

* Manual
* Dynamic
* Predictive

# AWS Elastic Load Balancing (ELB)

Elastic Load Balancing (ELB) automatically distributes incoming application traffic across multiple targets and virtual appliances in one or more Availability Zones (AZs).

Puede funcionar con cualquiera de los tres tipos de balanceadores.