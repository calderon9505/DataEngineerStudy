# DATOS

El usuario es responsable de activar el cifrado de los datos (almacenados y en tránsito). Todos los servicios de AWS ofrecen la capacidad de cifrar datos.

Los servicios AWS usan datos cifrados en tránsito tanto para la comunicación con el cliente, como para el intercambio de información entre los propios servicios.


## AWS Key Management Services (KMS)

Key Management Service. servicio de gestión de claves. KMS es compatible con los principales servicios de almacenamiento: S3, EBS, EFS, RDS


## AWS Certificate Manager (ACM)

Servicio para generar, implementar y renovar certificados digitales, los cuales son necesarios para implementar TLS (Transport Layer Security)(anteriormente SSL)


# MONITOREO Y CONFORMIDAD


## AWS CloudWatch

Recopila **datos operativos y de monitoreo** (logs)

* Permite visualización mediante paneles automatizados
* Permite establecer alarmas (costos, cpu, discos, etc)
* Permite toma de decisiones de acuerdo a límites establecidos (escalados...)


## AWS CloudTrail

Monitorea y registra la **actividad de la cuenta**

* Permite ver las acciones tomadas en almacenamiento, análisis y reparación
* Permite ver las acciones tomadas desde cualquier lugar (consola, CLI, SDK y API)

El *historial de eventos* se registra hasta por **90 días**


## AWS Config

Servicio para auditar las **configuraciones** de los recursos AWS 

* Monitoreo de las configuraciones para garantizar que cumplan con la norma seleccionada (AWS Compliance) o con póliticas de la empresa.
* Es un servicio **regional**, pero se puede aplicar a varias regiones de forma independiente (distintas regiones pueden tener distintas normativas)
* Se establecen reglas sobre servicios (evitar buckets publicos...)

Se tienen **paquetes de conformidad** que puedo implementar. Estos paquetes no son necesariamente paquetes de terceros como HIPAA, sino que tambien hay paquete como Best Practices for EC2.


## AWS Artifact

Servicio para generar informes de seguridad y conformidad


# IAM










----

> **AWS compliance**: Requerimientos de conformidad, es decir, leyes y controles para cumplir ciertas normativas de acuerdo a las normativas de los paises
