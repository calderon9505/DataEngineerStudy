# AWS DMS (Database Migration Service)

DMS es el servicio managed para migrar y replicar bases de datos (y otros almacenes) hacia AWS, o entre fuentes y destinos, con mínimo downtime.

Qué problema resuelve: Migrar una base de datos en producción es difícil: copiar todo toma tiempo y, mientras tanto, la base original sigue recibiendo cambios. DMS copia los datos existentes y mantiene sincronizados los cambios continuos, de modo que el corte final (cutover) dura minutos y la aplicación casi no se detiene.

## Componentes

- **Replication instance**: instancia EC2 managed donde corre la tarea de migración. Lee del origen, transforma ligeramente y escribe al destino. Se dimensiona según volumen (CPU, memoria, almacenamiento). Puede ser Multi-AZ para alta disponibilidad.
- **Source endpoint y target endpoint**: definen la conexión (host, credenciales, parámetros) al origen y al destino. Las credenciales pueden venir de Secrets Manager.
- **Replication task (migration task)**: define qué migrar y cómo, con su tipo de migración y reglas.
- **DMS Serverless**: variante sin instancia que gestionar; escala la capacidad (DCUs) automáticamente. Útil para cargas variables.

## Tipos de migración

| Tipo            | Qué hace                                                                                  |
| --------------- | ----------------------------------------------------------------------------------------- |
| Full load       | Copia todos los datos existentes una sola vez                                             |
| CDC only        | Solo captura y replica cambios continuos (cuando la carga inicial se hizo por otro medio) |
| Full load + CDC | Copia lo existente y luego sigue replicando cambios. Es el patrón para mínimo downtime    |

## CDC (Change Data Capture)

CDC es una técnica para detectar y capturar solo los cambios (inserts, updates y deletes) que ocurren en una base de datos, y enviarlos a otro lugar, en vez de copiar toda la base una y otra vez.

El problema que resuelve: Supón una tabla de 500 millones de filas en producción y quieres mantener una copia en S3 o Redshift.

- **Opción ingenua**: cada hora copias las 500 millones de filas. Es lento, caro y carga la base de producción.
- **Con CDC**: copias todo una vez (full load) y después solo transmites lo que cambió, quizás son unos miles de cambios por hora.

Cómo funciona: Las bases de datos ya registran cada cambio en un log de transacciones (para poder recuperarse ante fallos). CDC lee ese log en vez de consultar las tablas:

| Motor      | Log que se lee               |
| ---------- | ---------------------------- |
| MySQL      | binlog                       |
| PostgreSQL | WAL (write-ahead log)        |
| Oracle     | redo logs                    |
| SQL Server | transaction log / CDC tables |

Ventajas de leer el log:
- Casi no carga la base, porque no ejecuta consultas pesadas sobre las tablas.
- Captura deletes, algo que una consulta normal no ve (una fila borrada simplemente ya no está).
- Mantiene el orden de los cambios.
- Latencia baja, de segundos.

Por eso hay que habilitar el logging en el origen (binlog en formato ROW, wal_level=logical, etc.). Cada evento indica qué operación fue y los datos:

| Op | id  | nombre | saldo | timestamp |
| -- | --- | ------ | ----- | --------- |
| I  | 101 | Ana    | 500   | 10:00:01  |
| U  | 57  | Luis   | 900   | 10:00:03  |
| D  | 12  | Carlos | NULL  | 10:00:05  |

En el destino se aplican para reconstruir el estado actual:
- En otra base de datos: DMS aplica insert/update/delete directamente.
- En S3 (data lake): los archivos son inmutables, así que guardas el historial de cambios y luego haces un merge con Glue/Spark o con tablas Iceberg/Hudi (MERGE INTO) para obtener el estado vigente.
- En streaming: los cambios van a Kinesis o MSK como eventos para que otros sistemas reaccionen.

### CDC vs otras formas de obtener cambios

| Método                                     | Detecta deletes      | Carga en origen | Comentario                                                                                    |
| ------------------------------------------ | -------------------- | --------------- | --------------------------------------------------------------------------------------------- |
| Full reload periódico                      | Sí (por comparación) | Alta            | Simple, pero ineficiente                                                                      |
| Consulta incremental (WHERE updated_at > último) | No             | Media           | Es lo que hacen los Glue job bookmarks con JDBC. Falla si no hay columna fiable               |
| Triggers en la base                        | Sí                   | Media-alta      | Intrusivo                                                                                     |
| CDC por log                                | Sí                   | Baja            | Lo más robusto                                                                                |

Esto conecta con lo que dije de los Job Bookmarks: rastrean datos nuevos, pero no capturan updates ni deletes reales; para eso se usa CDC.

### CDC en AWS

- **DMS**: full load + CDC, el caso estándar.
- **DynamoDB Streams y Kinesis Data Streams for DynamoDB**: CDC nativo de DynamoDB (vimos que dura 24 horas en Streams).
- **Aurora/RDS Zero-ETL**: replica cambios de forma continua a Redshift.
- **MSK Connect con Debezium**: CDC de bases hacia Kafka.
- **Iceberg/Hudi**: aplican los cambios capturados con merge o incremental queries.

## Orígenes y destinos

- **Orígenes**: Oracle, SQL Server, MySQL, PostgreSQL, MariaDB, MongoDB, SAP ASE, Db2, y servicios AWS como RDS, Aurora, S3, DocumentDB.
- **Destinos**: lo anterior más S3, Redshift, DynamoDB, Kinesis Data Streams, MSK/Kafka, OpenSearch, Neptune, etc.
- **Migración homogénea**: mismo motor (MySQL → Aurora MySQL). DMS basta.
- **Migración heterogénea**: motores distintos (Oracle → PostgreSQL). Requiere convertir el esquema con SCT o DMS Schema Conversion.

## SCT y Schema Conversion

DMS migra datos y esquema básico de tablas, pero no convierte bien objetos complejos (stored procedures, funciones, tipos específicos del motor). Para eso:
- **AWS Schema Conversion Tool (SCT)**: aplicación de escritorio que convierte esquema y código de un motor a otro y genera un reporte de lo que no se pudo convertir automáticamente.
- **DMS Schema Conversion**: versión integrada en la consola.

> Patrón heterogéneo: SCT convierte el esquema → DMS migra los datos.

## DMS hacia data lakes y analytics

Usos muy frecuentes en data engineering:

- **Hacia S3**: DMS escribe archivos en CSV o Parquet. Con CDC, agrega una columna Op (I/U/D) que indica el tipo de operación, y opcionalmente un timestamp. Después se procesan con Glue o se aplican con Iceberg/Hudi (merge) para reconstruir el estado actual.
- **Hacia Redshift**: DMS usa S3 como staging y carga con COPY.
- **Hacia Kinesis o MSK**: para streaming de cambios en tiempo real.
- **Hacia DynamoDB**: con object mapping, como vimos.

> Comparado con Zero-ETL: cuando origen y destino están soportados (Aurora/RDS → Redshift), Zero-ETL es más simple; DMS cubre más fuentes y destinos.

## Transformaciones: table mappings

Reglas en JSON:
- **Selection rules**: qué esquemas y tablas incluir o excluir.
- **Transformation rules**: renombrar esquemas, tablas o columnas, agregar o quitar columnas, cambiar mayúsculas.
- Son transformaciones ligeras; para lógica compleja se usa Glue después.

## Validación y monitoreo

- **Data validation**: DMS compara origen y destino para verificar que los datos migrados coinciden.
- **CloudWatch**: métricas como CDCLatencySource y CDCLatencyTarget (retraso de la replicación). Es la métrica clave para saber si CDC se está quedando atrás.
- Logs de tareas en CloudWatch Logs y eventos vía SNS/EventBridge.
- **Premigration assessment**: evalúa problemas potenciales antes de ejecutar.

## Seguridad y red

- Cifrado at rest con KMS y in transit con SSL/TLS hacia los endpoints.
- La replication instance vive en una VPC y necesita conectividad al origen y destino (VPN, Direct Connect, peering, security groups). Es la causa más común de fallos de conexión.
- IAM roles para que DMS acceda a S3, Kinesis, Redshift, etc. Los roles dms-vpc-role y dms-cloudwatch-logs-role son requisitos clásicos, y el destino S3 necesita un service role con permisos de escritura (trust policy para dms.amazonaws.com).

## Limitaciones a tener presentes

- No es un ETL completo: transformaciones limitadas.
- Migra datos y objetos básicos, no todos los objetos de esquema (índices secundarios, procedures, triggers pueden requerir SCT o manejo manual).
- LOBs (objetos grandes): tienen modos específicos (limited, full, inline) con impacto en rendimiento.
- Para un origen sin clave primaria, las actualizaciones y deletes en CDC pueden ser problemáticos.
- Para migraciones muy grandes o con red lenta, se combina con Snowball (carga inicial física) más CDC.

## Servicios cercanos

| Necesidad                              | Servicio                    |
| -------------------------------------- | --------------------------- |
| Migrar/replicar bases de datos con CDC | DMS                         |
| Convertir esquema entre motores        | SCT / DMS Schema Conversion |
| Aurora/RDS → Redshift sin pipeline     | Zero-ETL                    |
| Transferir archivos                    | DataSync / Transfer Family  |
| Datos de aplicaciones SaaS             | AppFlow                     |
| Streaming de eventos de aplicación     | Kinesis / MSK               |
