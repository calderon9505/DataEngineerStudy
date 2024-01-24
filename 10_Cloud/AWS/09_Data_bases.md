# RDS

Servicio de base de datos relacional administrado por AWS. AWS se encarga de:
* Instalación y parches del sistema operativo
* Copias de seguridad
* Alta disponibilidad
* Escalado
* Mantenimiento del sevidor

Motores de bases de datos disponibles:
* MySQL
* MariaDB
* PostreSQL
* Oracle
* Amazon Aurora
* Microsoft SQL Server

### Replicas de Lectura

AWS ofrece réplicas de lectura para aumentar el rendimiento cuando se tienen muchas solicitudes de lectura o consultas muy complejas. Si se tienen problemas con la base de datos principal, se puede promover una copia a **principal**


# Dynamo DB

Servicio de base de datos no relacional administrado por AWS

* Almacenamiento prácticamente ilimitado
* Consultas con latencia de milisegundos de un solo dígito (por más grande que sea la base de datos, las consulas responden en menos de 10 milisegundos)
* Rendimiento escalable de lectura o escritura
* Se ejecuta exclusivamente en SSD
* Compatible con modelos de almacenamiento de documentos y clave-valor
* Las réplicas de tablas en las *regiones* de AWS se hacen de manera automática


# Redshift

Servicio de base de datos relacional que proporciona análisis rápido y escalable a big data.
* Funciona mediante el uso de **clusters**
* Datos almacenados de forma columnar
* Almacenamiento de datos con compresión
* Compatible con SQL standar y proporciona conectores JDBC y ODBC


# Amazon Aurora

Servicio de base de datos relacional compatible con MySQL y PostgreSQL creado especialmente para la nube de AWS.

* Escalabilidad, durabilidad, disponibilidad, lantecia ......  mejoradas
* Almacenamiento distribuido en bloques SSD con recuperación automática de fallos
* Réplicas en otras regiones para reducir latencia de aplicaciones globales


---
---
---

# Amazon ElastiCache

Servicio para mejora en las base de datos. Se obtienen tiempos de respuesta de microsegundos.