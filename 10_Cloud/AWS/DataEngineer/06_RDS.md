# Amazon RDS (Relational Database Service)

RDS es el servicio **managed** de bases de datos relacionales. AWS gestiona por ti:

- Provisioning del hardware y la instalación del motor de base de datos.
- Patching del sistema operativo y del motor.
- Backups automáticos y point-in-time recovery.
- Alta disponibilidad (Multi-AZ) y réplicas.
- Monitoreo (CloudWatch).

> Lo que tú NO controlas: acceso al sistema operativo, SSH a la máquina. Si necesitas ese control total, tendrías que montar la DB en EC2 tú mismo (self-managed) — pero pierdes todo lo managed.

Soporta 6 motores (engines):

- MySQL
- PostgreSQL
- MariaDB
- Oracle
- SQL Server
- Amazon Aurora (el motor propio de AWS, compatible con MySQL y PostgreSQL — suele tratarse como producto aparte por sus capacidades extra)

## qué es y qué no es

✅ RDS es para cargas OLTP (Online Transaction Processing): muchas transacciones pequeñas, lecturas/escrituras de aplicaciones, integridad transaccional.

⚠️ No es para analytics a gran escala (OLAP) — para data warehouse / queries analíticas masivas, el examen espera Redshift. Confundir RDS con Redshift es un error clásico.

|            | RDS (OLTP)            | Redshift (OLAP)            |
| ---------- | --------------------- | -------------------------- |
| Uso        | Transacciones de apps | Analytics / data warehouse |
| Queries    | Muchas, pequeñas      | Pocas, complejas, masivas  |
| Estructura | Row-based             | Columnar                   |


## Alta Disponibilidad

|                     | Multi-AZ               | Read Replicas                  |
| ------------------- | ---------------------- | ------------------------------ |
| Propósito           | Disponibilidad (HA/DR) | Escalar lecturas (performance) |
| Replicación         | Síncrona               | Asíncrona                      |
| ¿Sirve tráfico?     | No (standby pasiva)    | Sí (lecturas)                  |
| Failover automático | Sí                     | No (promoción manual)          |
| Misma/otra región   | Otra AZ (misma región) | Misma u otra región            |


### Multi-AZ deployment

¿Qué pasa si se cae la base de datos? RDS mantiene una réplica standby síncrona en otra Availability Zone.

- La replicación es síncrona → la standby está siempre al día.
- Si la primary falla (o hay mantenimiento), RDS hace failover automático a la standby (cambia el DNS endpoint). Sin intervención manual. (60-120 segundos de interrupción del servicio)
- Propósito: alta disponibilidad y DR, NO escalar lecturas.
- La standby no sirve tráfico (no la consultas) — solo espera para el failover.

### Read Replicas

¿Qué pasa si recibe demasiadas lecturas y se satura? RDS mantiene réplicas de solo lectura de la base de datos.

- Replicación asíncrona.
- Sirven para escalar lecturas (offload de queries de lectura de la primaria) → mejora performance en apps read-heavy.
- Puedes tener varias, incluso en otras regiones (cross-region read replica → ayuda a DR y a latencia global).
- Las apps leen de las réplicas y escriben en la primaria.
- Puedes promover una read replica a base independiente.

## Backups y recuperación

- Automated backups: RDS respalda automáticamente; retención configurable (1–35 días). Permiten Point-in-Time Recovery (PITR) — restaurar a cualquier segundo dentro de la ventana.
- Manual snapshots: los creas tú; persisten hasta que los borres (no expiran con la retención). Se pueden copiar a otra región (DR) y compartir entre cuentas.
- Restaurar un backup/snapshot crea una nueva instancia (no sobrescribe la existente).

## Seguridad

- Encryption at rest con KMS (se habilita al crear; para cifrar una existente, hay que restaurar un snapshot cifrado).
- Encryption in transit con SSL/TLS.
- Despliegue dentro de una VPC, control de acceso por Security Groups.
- IAM database authentication: autenticarse a la DB con credenciales IAM temporales (en vez de password) — para MySQL/PostgreSQL.
- Integración con Secrets Manager para rotar credenciales automáticamente.

## Costos / escalado

- Vertical scaling: cambiando a un tipo de instancia mayor. Es la forma de escalar la capacidad de escritura (writes) y la potencia general del DB. También puedes escalar manualmente el storage (no recomendado).
- Storage Auto Scaling: aumenta el storage automáticamente al llenarse.
- Escalado horizontal limitado con Read Replicas (solo lecturas, no escrituras).

¿Y si necesito escalar escrituras horizontalmente? Aquí es donde RDS tradicional se queda corto y empiezan a aparecer servicios como Aurora Serverless v2 o DynamoDB

## Amazon RDS Proxy

RDS Proxy es un connection pooler (administrador de conexiones) fully managed que se sitúa entre tu aplicación y la base de datos RDS/Aurora. Su trabajo es gestionar y reutilizar las conexiones a la base de forma eficiente.

El problema que resuelve: Abrir una conexión a una base de datos es caro: consume CPU y memoria, y cada base tiene un límite de conexiones simultáneas. Esto se vuelve crítico en dos escenarios:

1. Muchas conexiones concurrentes: aplicaciones con mucho tráfico abren miles de conexiones y agotan la memoria/límite de la base → errores de "too many connections".
2. Aplicaciones serverless (Lambda): este es el caso estrella. Lambda escala a cientos o miles de invocaciones concurrentes, y cada una intenta abrir su propia conexión a la base → la saturan al instante. Además, las conexiones se abren y cierran constantemente, lo cual es muy ineficiente.

Cómo funciona

```
App / Lambda  ──►  RDS Proxy  ──►  RDS / Aurora
   (muchas          (pool de         (pocas conexiones
  conexiones)      conexiones        reales reutilizadas)
                  reutilizables)
```

- El proxy mantiene un pool de conexiones ya establecidas a la base.
- Las aplicaciones se conectan al proxy, y este reutiliza (multiplexa) un número reducido de conexiones reales hacia la base.
- Así, miles de conexiones de app se traducen en pocas conexiones reales a la base de datos.

Beneficios clave:

1. Connection pooling → evita agotar las conexiones de la base; ideal para Lambda y apps con picos de concurrencia.
2. Mejora la resiliencia / failover más rápido → durante un failover de Multi-AZ, el proxy reduce el tiempo de failover (hasta ~66% más rápido) porque mantiene las conexiones y reenruta a la nueva primary sin propagar el error a la app. La app no tiene que reconectar manualmente.
3. Seguridad → se integra con IAM authentication (te autenticas al proxy con IAM, sin password) y con AWS Secrets Manager para gestionar las credenciales. También fuerza TLS.
4. Totalmente managed → sin administrar infraestructura; escala automáticamente.

## Relevancia para DEA-C01

- RDS suele ser una fuente de datos (source) para pipelines: se extraen datos con AWS DMS (Database Migration Service), Glue, o federated queries.
- DMS se usa mucho para migrar o replicar RDS → S3 / Redshift (con CDC – Change Data Capture para cambios incrementales).
- Zero-ETL (Aurora → Redshift) es una tendencia que el examen ya incluye: replicar datos transaccionales a Redshift sin construir pipeline ETL.
- RDS como fuente para Athena federated queries o Redshift federated queries.
