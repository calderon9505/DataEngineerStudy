# Amazon Athena

Athena es un servicio de consultas serverless e interactivo que te deja analizar datos directamente en S3 usando SQL estándar, sin cargarlos antes en ningún sistema ni gestionar infraestructura.

## Qué es y cómo funciona

- **Serverless**: no hay clusters, nodos ni capacidad que provisionar. Escribes SQL y Athena asigna el cómputo.
- **Schema-on-read**: los datos siguen siendo archivos en S3. Athena aplica un esquema (tabla) al momento de leer. Las definiciones de tablas viven en el Glue Data Catalog.
- Motores por debajo:
    - Trino/Presto para consultas SQL (el motor clásico de Athena).
    - Apache Spark para notebooks (Athena for Apache Spark), con PySpark interactivo.
- El resultado de cada consulta se escribe en un bucket de S3 (query results location), que debes configurar.
- Usa DDL tipo Hive para crear tablas (CREATE EXTERNAL TABLE) y SQL ANSI (Trino) para consultar.

> Athena es OLAP ad-hoc: ideal para consultas exploratorias y puntuales sobre el lake. No es una base de datos transaccional ni reemplaza a Redshift en cargas de BI intensivas y concurrentes.

## Modelo de costos

Por defecto Athena cobra por TB de datos escaneados (~5 USD por TB). Lo importante: pagas por lo que se lee de S3, no por el tiempo de la consulta. Además:

- Las consultas fallidas no se cobran, y las instrucciones DDL (CREATE/ALTER/DROP) son gratuitas.
- Hay un mínimo de 10 MB por consulta.
- Pagas aparte el almacenamiento en S3 y los resultados.

> De esto se deriva el principio central de optimización: reducir los datos escaneados.

## Optimización de costo y rendimiento ⭐

1. **Formato columnar (Parquet u ORC)**: Athena lee solo las columnas necesarias. Puede reducir el escaneo en un 90% o más frente a CSV/JSON.
2. **Compresión (Snappy, GZIP, ZSTD, etc.)**: menos bytes leídos. Ojo con que algunos formatos (como GZIP sobre CSV) no son splittable, lo que limita el paralelismo.
3. **Particionamiento**: organizar en S3 por columnas de filtro habituales (ej. year=/month=/day=), de modo que Athena haga partition pruning y lea solo las particiones necesarias. Se usa WHERE sobre la columna de partición.
4. **Partition projection**: en vez de almacenar millones de particiones en el catálogo, Athena calcula las particiones desde un patrón definido en las propiedades de la tabla. Acelera consultas y elimina MSCK REPAIR TABLE/crawlers para particiones predecibles (fechas).
5. **Bucketing**: agrupar datos por una columna de alta cardinalidad en un número fijo de archivos (buckets), útil para joins y filtros por esa columna.
6. **Archivos de tamaño adecuado**: evitar el small files problem. Lo ideal es archivos de 128 MB a 1 GB. Demasiados archivos pequeños elevan la sobrecarga (listados y requests a S3). Se corrige con compactación (Glue, CTAS, o OPTIMIZE en Iceberg).
7. **Seleccionar solo las columnas necesarias**: evita `SELECT *`.
8. **LIMIT y filtros tempranos**; en ORDER BY evitar ordenar todo si no hace falta.
9. **Joins**: poner la tabla más grande a la izquierda y la más pequeña a la derecha (Athena envía la derecha a los nodos).
10. Column statistics en el Glue Data Catalog para el optimizador basado en costos.

## CTAS e INSERT INTO

- **CTAS (CREATE TABLE AS SELECT)**: crea una tabla nueva a partir del resultado de una consulta, escribiendo los datos en S3 en el formato que elijas. Es la forma estándar de convertir CSV/JSON a Parquet, particionar y comprimir sin un job de Glue.
- **INSERT INTO**: agrega resultados a una tabla existente.
- **Limitación**: una CTAS puede escribir hasta 100 particiones por consulta; para más, se encadenan varios INSERT INTO.
- **UNLOAD**: exporta el resultado de una consulta a S3 en un formato como Parquet, sin crear una tabla.

## Views

Athena soporta vistas (consultas guardadas, no materializadas) almacenadas en el catálogo. Útiles para simplificar consultas o restringir columnas.

## Workgroups ⭐ (gobernanza y control de costos)

Un workgroup agrupa usuarios, consultas y configuración, permitiendo separar cargas de trabajo (equipos, entornos, aplicaciones). Con ellos puedes:

- Establecer la ubicación y cifrado de los resultados y forzarlos para todos los usuarios del grupo.
- Definir límites de datos escaneados: por consulta (se cancela si excede) y por workgroup en un período (con alarma/acción).
- Separar costos: etiquetar y ver métricas por workgroup, publicadas en CloudWatch.
- Controlar acceso con IAM a nivel de workgroup.
- Elegir la versión del motor.

> Es la respuesta típica a "controlar o limitar costos de consultas por equipo".

## Capacity Reservations (Provisioned Capacity)

Además del modelo on-demand, Athena ofrece capacidad provisionada: reservas DPUs dedicadas, y pagas por DPU-hora en vez de por TB escaneado. Útil para cargas predecibles y críticas que requieren rendimiento consistente. Se asignan a workgroups.

## Federated Query ⭐

Athena puede consultar fuentes que no son S3, directamente y en una sola consulta SQL (incluso con joins entre fuentes), mediante **data source connectors**:

- Los conectores son funciones Lambda (desplegables desde el Serverless Application Repository).
- Fuentes soportadas: DynamoDB, RDS/Aurora, Redshift, DocumentDB, OpenSearch, CloudWatch Logs, ElastiCache/Redis, Timestream, bases on-premise vía JDBC, etc.
- También se puede definir un conector propio con el Athena Query Federation SDK.
- Las credenciales suelen guardarse en Secrets Manager.

Ya lo mencionamos al ver las federated queries de Redshift. Permite análisis ad-hoc sobre datos operacionales sin ETL, aunque no es la opción para cargas masivas recurrentes (rendimiento limitado por la fuente).

## Athena for Apache Spark

Permite ejecutar notebooks de PySpark de forma interactiva, sin gestionar clusters, para análisis más complejos que SQL puro (ML, transformaciones, librerías Python). Se factura por DPU-hora de sesión. Es conceptualmente cercano a las Glue Interactive Sessions.

## Soporte para tablas Iceberg (y otros formatos)

Athena trabaja con Apache Iceberg con capacidades completas:

- INSERT, UPDATE, DELETE, MERGE INTO con SQL.
- Time travel (FOR TIMESTAMP AS OF / FOR VERSION AS OF).
- Schema evolution.
- OPTIMIZE (compactación de archivos) y VACUUM (limpieza de snapshots y archivos huérfanos).

También soporta Hudi y Delta Lake (principalmente lectura). Es la ruta moderna para ACID y upserts en el lake, como vimos.

## Seguridad y gobernanza

- IAM: permisos sobre acciones de Athena, Glue y S3.
- Lake Formation: permisos granulares (columna, fila, celda) que Athena respeta. Es lo recomendado para gobernanza centralizada.
- Cifrado: resultados y datos con SSE-S3, SSE-KMS o CSE-KMS. In transit con TLS.
- VPC endpoint (PrivateLink) para acceso privado a Athena.
- Auditoría con CloudTrail y logs de consultas.
- Cross-account: acceso a datos de otra cuenta vía catálogo compartido (Lake Formation/RAM) o bucket policies.

## Integraciones frecuentes

- **Glue Data Catalog / Crawlers**: definen las tablas.
- **QuickSight**: dashboards BI sobre Athena (con SPICE opcional).
- **Conectores JDBC/ODBC**: Tableau, Power BI, clientes SQL.
- **Logs**: patrón clásico de analizar ALB logs, CloudTrail, VPC Flow Logs, S3 access logs, CloudFront directamente con Athena.
- **Step Functions**: tiene integración directa para ejecutar consultas Athena como paso de un workflow.
- **EventBridge / CloudWatch**: para alertas y monitoreo.
- **Redshift Spectrum y Athena son hermanos**: ambos consultan S3 con el Glue Catalog.

## Cuotas y comportamiento a tener en cuenta

- Límite de tiempo de consulta (30 min por defecto en consultas DML; ampliable) y cuotas de consultas concurrentes por cuenta/región.
- Los resultados quedan en S3 y se pueden reutilizar con query result reuse (caché), lo que evita reejecutar y cobrar consultas repetidas.
- Idempotencia: se puede enviar un ClientRequestToken para evitar duplicar ejecuciones.
- Prepared statements y parameterized queries para reutilizar y reducir riesgo de inyección SQL.

## Athena vs otras herramientas

|            | Athena                    | Redshift                                                     | Redshift Spectrum          | EMR                               |
| ---------- | ------------------------- | ------------------------------------------------------------ | -------------------------- | --------------------------------- |
| Modelo     | Serverless                | Cluster/Serverless warehouse                                 | Extensión de Redshift      | Cluster (o Serverless)            |
| Datos      | En S3 (sin cargar)        | Cargados en el warehouse                                     | En S3 + tablas Redshift    | En S3/HDFS                        |
| Mejor para | Ad-hoc, exploración, logs | BI intensivo, muchas consultas concurrentes, joins complejos | Unir warehouse con lake    | Procesamiento Spark/Hadoop custom |
| Costo      | Por TB escaneado          | Por nodo/hora o RPU                                          | Por TB escaneado + cluster | Por instancia/hora                |
| Gestión    | Ninguna                   | Alguna                                                       | Alguna                     | Más                               |

> Regla práctica: consultas ocasionales/ad-hoc sobre S3 → Athena; BI continuo con alta concurrencia y rendimiento predecible → Redshift; unir warehouse y lake → Spectrum.