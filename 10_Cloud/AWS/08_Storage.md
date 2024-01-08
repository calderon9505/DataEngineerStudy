# Elastic Block Store (EBS)

* Permite crear volúmenes y asociarlos a una instancia de EC2 (como las particiones C, D, ...)
* Almacenamiento a nivel de bloques (lo contrario es almacenamiento a nivel de objeto)
* Los volúmenes se replican automáticamente dentro de su zona de disponibilidad
* Se pueden hacer copias de seguridad automáticas en S3 a través de instantáneas
* Permite cifrado de datos
* Ofrece elasticidad

Se puede implementar en:

* **SSD**: recomendado para arranque de sitemas, aplicaciones de baja latencia, etc
* **HDD**: recomendado para Big data, almacenes de datos, etc

Costos

* Se cobra por cantidad de espacio aprovisionado por mes
* La transferencia entrante es gratuita pero la transferencia de datos salientes entre regiones tiene costo
* IOPS

# Elastic File System (EFS)

Almacenamiento orientado a la red

* Almacenamiento compartido
* Compatibilidad con NFS
* Sistema de archivos de baja latencia a escala de petabytes
* Se puede escalar y así pagar por lo que se utiliza
* Compatibilidad con todas las AMI en Linux


# Simple Storage Service (S3)

Almacenamiento genérico

* Almacenamiento a nivel de objetos
* Se asocia a una región y se replica de forma automática dentro de ella
* Almacenamiento ilimitado
* maximo 5 TB por objeto
* Acceso detallado a buckets y objetos (es decir, cada bucket y objeto tiene una URL única)

Costos ([Amazon S3 pricing](https://aws.amazon.com/s3/pricing/))

* GB/Month
* Transferencias salientes de datos a otras regiones
* solicitudes PUT, COPY, POST, LIST y GET

![](https://d1.awsstatic.com/reInvent/reinvent-2023/s3/s3-storage-classes.80b54ee6539a2116307230017700596a282f471b.png)

### S3 Standard

* General purpose storage for frequently accessed data
* Low latency and high throughput performance


### S3 Standard - IA

S3 Standard Infrequent Access is for data that is accessed less frequently, but requires rapid access when needed

* Infrequently accessed data that needs millisecond access
* Low latency and high throughput performance (just like S3 standard)

### S3 One zone Express

* Stores data in a single AZ
* High performance storage for your **most frequently** accessed data
* single-digit millisecond request latency
* Improve access speeds by 10x and reduce request costs by 50% (compared to S3 Standard)
* Scale to handle millions of requests per minute
* Optimized for large datasets with many small objects



### S3 One zone - IA

* Infrequently accessed data 
* Stores data in a single AZ
* Low latency and high throughput performance (just like S3 standard)
* costs 20% less than S3 Standard-IA
* less availability compared with S3 Standard

### S3 Glacier Instant Retrieval

* Long-lived data that is accessed a **few times per year**
* Data retrieval in milliseconds with the same performance as S3 Standard
* save up to 68% on storage costs compared to S3-IA when your data is accessed once per quarter. 

### S3 Glacier (Flexible Retrieval)

* Long-lived data that is accessed a **few times per year**
* Configurable retrieval times
    * **Expedited**: 1-5 minutes
    * **Standard**: 3-5 hours
    * **Bulk**: 5-12 hours
* save up to 10% compared to S3 Glacier Instant Retrival

### S3 Glacier Deep Archive

* Long-lived data that is accessed a **few times per year**
* Configurable retrieval times
    * **Standard**: within 12 hours
    * **Bulk**: within 48 hours

### S3 Intelligent - Tiering

Automatic cost savings for data with unknown or changing access patterns
* Use S3 standard by default
* Move objects to Infrequent access if have not been accessed for **30** consecutive days. 40% lower-cost.
* Move objects to Archive Instant Access if have not been accessed for **90** consecutive days. 68% lower-cost.
* Move objects to Deep Archive Access if have not been accessed for **180** consecutive days. up to 95% lower-cost. (optional)

## Lifecycle Rules

To manage your objects so that they are stored cost effectively throughout their lifecycle.
* **Transition actions** – These actions define when objects transition to another storage class.
* **Expiration actions** – These actions define when objects expire. Amazon S3 deletes expired objects on your behalf.


# AWS Snow Family

Llevar datos a los servidores de AWS de forma distintas a la red. Son equipos de almacenamiento con capacidades de cómputo, que deben ser enviados a las instalaciones de AWS de forma física.

* **Snowcone**: 8 TB
* **Snowball**: 80 TB
* **snowmobile**: 100 PB (es un camión xd)

# Storage Gateway

Almacenamiento para nubes híbridas.