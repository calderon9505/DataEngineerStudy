# Elastic Container Registry (ECR)

Guarda imagenes de contenedores. Es igual que DockerHub administrado por AWS.


# Elastic Container Service (ECS)

Servicio propio de AWS para orquestar los contenedores

* Organiza la ejecución de los contenedores
* Mantiene (tolerancia a errores) y escala (horizontalmente) la flota de nodos
* Elimina la complejidad de poner en marcha la infra

Se integra con

* Grupos de seguridad de EC2
* Volúmenes de EBS
* Roles de IAM
* Elastic Load Balancing

Formas de lanzas ECS

1. **Manual**: Se crea un cluster de ECS respaldado por EC2 y en él se administran los nodos(máquinas EC2, O.S., Motor Docker, etc). Es decir, administro manualmente la infraestructura.

2. **Fargate**: Se crea un cluster de ECS respaldado por Fargate y no me encargo de la infraestructura. Esto permite centrarse en las aplicaciones.


# Elastic Kubernetes Service (EKS)

Servicio famoso para orquestar los contenedores