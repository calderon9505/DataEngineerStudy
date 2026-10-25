# AWS Glue

Es el servicio de ETL (Extract, Transform, Load) serverless de AWS, pero con el tiempo se ha convertido en una plataforma de integración de datos completa. 

## Qué es Glue

Glue es un servicio serverless para descubrir, catalogar, limpiar, transformar y mover datos entre fuentes. "Serverless" es clave: no provisionas ni gestionas infraestructura; AWS levanta los recursos de cómputo cuando un job corre y los apaga al terminar. Pagas solo por el tiempo de ejecución.

El propósito es ser el pegamento ("glue") entre todas las fuentes y destinos de datos: tomar datos de S3, RDS, DynamoDB, streams, etc., transformarlos, y cargarlos en un data lake (S3), un warehouse (Redshift), u otro destino.

> Glue no es un solo producto, sino un conjunto de componentes.

## 1. AWS Glue Data Catalog ⭐ (el componente central)

El Data Catalog es un repositorio de metadatos centralizado y persistente. No almacena los datos en sí — almacena información sobre los datos (metadata): dónde están, su esquema (columnas y tipos), formatos, particiones, etc.

Estructura:
- **Databases**: agrupaciones lógicas de tablas.
- **Tables**: definiciones de metadatos de un dataset. Cada tabla describe el esquema, la ubicación (ej. una ruta en S3), el formato (Parquet, CSV, JSON...) y las particiones. La tabla apunta a los datos reales (que viven en S3, por ejemplo), pero no los contiene.

Por qué es tan importante: el Data Catalog es la fuente única de verdad del esquema para todo el ecosistema analítico de AWS. Es compatible con el Hive Metastore, y lo consumen:
- Athena (para saber qué consultar en S3),
- Redshift Spectrum (tablas externas),
- EMR (Spark/Hive),
- Glue ETL jobs,
- Lake Formation (gobernanza sobre el catálogo).

> Es decir, catalogas una vez y todos esos servicios usan la misma definición. Esto convierte a *S3 + Glue Data Catalog* en la base del data lake.

## 2. Glue Crawlers ⭐

Un Crawler es un proceso que escanea automáticamente una fuente de datos (típicamente S3, pero también JDBC, DynamoDB, etc.), infiere el esquema (descubre columnas, tipos, formato) y crea o actualiza las tablas en el Data Catalog.

Cómo funciona:
- Apuntas el crawler a una ubicación (ej. s3://mi-lake/ventas/).
- Usa classifiers para detectar el formato y estructura de los datos (hay classifiers integrados para CSV, JSON, Parquet, Avro, ORC, XML, logs, etc.; puedes crear custom classifiers con Grok, regex, etc.).
- Detecta particiones automáticamente (ej. la estructura year=2025/month=10/ la reconoce como particiones).
- Crea/actualiza la tabla en el catálogo con todo eso.
- Puede ejecutarse on-demand o programado (schedule), o dispararse por eventos.

> Punto importante: el crawler es la forma de mantener el catálogo sincronizado cuando llegan datos nuevos o el esquema cambia. Pero no siempre es necesario: si ya conoces el esquema, puedes crear las tablas manualmente o con los jobs, evitando el costo del crawler.

## 3. Glue ETL Jobs ⭐ (el motor de transformación)

El componente de ejecución de transformaciones. Un Glue job toma datos de una o varias fuentes, los transforma, y los escribe en un destino. Hay varios tipos de jobs, y esta distinción es muy preguntada:

- Spark jobs
    - Corren sobre Apache Spark (procesamiento distribuido en memoria).
    - Para transformaciones de grandes volúmenes en paralelo.
    - Puedes escribirlos en Python (PySpark) o Scala.

- Python Shell jobs
    - Ejecutan un script de Python simple (no Spark), en un solo nodo.
    - Para tareas ligeras que no necesitan procesamiento distribuido (pequeñas transformaciones, llamar APIs, orquestar cosas pequeñas).
    - Más baratos que levantar un cluster Spark.

- Streaming ETL jobs
    - Procesan datos en streaming (micro-batches) desde Kinesis Data Streams o MSK/Kafka, usando *Spark Structured Streaming*.
    - Para transformación casi en tiempo real.

- Ray jobs
    - Para cargas de cómputo en Python distribuido (más nuevo, menos central en el examen).

## 4. DynamicFrames (concepto propio de Glue)

Dentro de los Spark jobs, Glue introduce el DynamicFrame, su propia abstracción de datos (análoga al DataFrame de Spark, pero con diferencias clave):

- Un DataFrame de Spark requiere un esquema fijo conocido de antemano.
- Un DynamicFrame no requiere esquema previo: maneja datos semiestructurados y esquemas que cambian o son inconsistentes. Cada registro puede autodescribirse.
- Maneja ambigüedades de tipo con las "choice" types (ej. una columna que a veces es int y a veces string) sin romperse.
- Tiene transformaciones propias como ResolveChoice (resolver tipos ambiguos), DropNullFields, ApplyMapping (renombrar/retipar columnas), Relationalize (aplanar estructuras anidadas JSON en tablas relacionales).
- Se puede convertir a/desde DataFrame de Spark cuando necesitas la potencia de Spark SQL.

> La idea: el DynamicFrame es ideal para la realidad "sucia" de los datos de un data lake (esquemas inconsistentes), mientras que el DataFrame es mejor cuando el esquema es estable y quieres usar Spark SQL puro.

## 5. Glue Studio y las interfaces de desarrollo

Glue ofrece varias formas de crear jobs según tu perfil:

- Glue Studio: editor visual (drag-and-drop) para construir pipelines ETL sin escribir mucho código. Genera el código Spark por debajo. Bueno para construir visualmente y para quienes no son expertos en Spark.
- Notebooks: desarrollo interactivo (Jupyter) para construir y probar jobs.
- Script editor: escribir el código PySpark/Scala directamente.

## 6. AWS Glue DataBrew

DataBrew es una herramienta visual de preparación de datos orientada a analistas (sin código). Permite limpiar y normalizar datos con una interfaz point-and-click:

- Ofrece 250+ transformaciones predefinidas (eliminar nulos, estandarizar formatos, corregir valores, etc.).
- Genera "recipes" (recetas): conjuntos de transformaciones reutilizables.
- Hace profiling de datos (estadísticas, calidad, detección de anomalías).
- Diferencia con Glue ETL: DataBrew es no-code, visual, para preparación exploratoria por analistas; Glue ETL jobs son para pipelines productivos programáticos.

## 7. Glue Data Quality ⭐

Una capacidad cada vez más preguntada. Glue Data Quality permite definir y evaluar reglas de calidad sobre tus datos.

- Usa DQDL (Data Quality Definition Language) para expresar reglas (ej. "esta columna no debe tener nulos", "los valores deben estar en este rango", "debe ser única").
- Puede recomendar reglas automáticamente analizando los datos.
- Se integra en los pipelines: evalúa la calidad y puede fallar el job o alertar si los datos no cumplen.
- Funciona sobre el Data Catalog o dentro de los jobs ETL.
- Esencial para el concepto de gobernanza y confianza en los datos del data lake.

## 8. Glue Schema Registry

Gestiona y valida el esquema de datos en streaming. Permite registrar esquemas (Avro, JSON Schema, Protobuf) y garantizar que productores y consumidores de streams (Kinesis, MSK, Kafka, Flink) usen esquemas compatibles, controlando la evolución del esquema (que un cambio no rompa a los consumidores).

## 9. Orquestación: Workflows y Triggers

Glue tiene su propia orquestación interna:

- **Triggers**: inician jobs/crawlers. Pueden ser on-demand, scheduled (cron), o event-based/conditional (cuando otro job termina, con éxito/fallo).
- **Workflows**: orquestan múltiples crawlers y jobs como un pipeline con dependencias (ejecutar crawler → job de transformación → job de carga, en orden).

> Nota: para orquestación más compleja o multi-servicio, el examen suele preferir Step Functions o MWAA (Airflow), pero los workflows de Glue sirven para pipelines contenidos dentro de Glue.

## 10. Glue Connections

Definiciones reutilizables de conexión a fuentes de datos (credenciales, parámetros de red). Permiten que los jobs/crawlers accedan a RDS, Redshift, JDBC, Kafka, etc. Para fuentes en una VPC, Glue usa estas conexiones para acceder de forma privada.

## Concepto clave de costos: DPUs

Glue factura su cómputo en DPUs (Data Processing Units). Una DPU es una unidad de capacidad (una combinación de CPU y memoria — 4 vCPU y 16 GB RAM). Pagas por DPU-hora mientras el job corre (facturado por segundo, con un mínimo).

- Más DPUs = más paralelismo = más rápido, pero más costo.
- Auto Scaling: Glue puede ajustar el número de workers dinámicamente según la carga del job.

## Glue Flex

Una opción de ejecución de menor costo para jobs no urgentes/no sensibles al tiempo (ETL batch que puede tolerar tiempos de inicio variables). Usa capacidad de cómputo "sobrante" de AWS a cambio de un precio menor. Para jobs donde la latencia de ejecución no importa.

## 11. Glue Job Bookmarks ⭐

Los Job Bookmarks son un mecanismo para procesar solo datos nuevos en ejecuciones sucesivas, evitando reprocesar lo ya procesado.

- Glue "recuerda" (marca) qué datos ya procesó en la última ejecución (basándose en timestamps, keys, etc.).
- En la siguiente ejecución, procesa solo lo nuevo/cambiado desde el último bookmark.
- Esto habilita procesamiento incremental eficiente: por ejemplo, si cada día llegan archivos nuevos a S3, el job solo procesa los del día, no todo el histórico.
- Evita duplicados y ahorra tiempo/costo.

> Es el equivalente conceptual a lo que CDC hace en migraciones: solo lo incremental.

## Cómo encaja todo (flujo típico)

Un pipeline de data lake clásico con Glue:

1. Datos llegan a S3 (raw)
2. CRAWLER escanea → crea/actualiza tabla en el DATA CATALOG
3. GLUE ETL JOB (Spark) lee desde el catálogo, transforma (limpia, convierte a Parquet, particiona, aplica Data Quality) → con JOB BOOKMARKS procesa solo lo nuevo
4. Escribe resultado en S3 (curated/processed) o Redshift
5. Otro CRAWLER cataloga la salida
6. ATHENA / REDSHIFT SPECTRUM consultan vía el mismo catálogo (orquestado por WORKFLOWS, Step Functions o Airflow)

## Glue vs otras opciones de procesamiento (criterio de examen)

- **Glue vs EMR**: Glue es serverless, más simple, sin gestionar clusters, ideal para ETL que no requiere control fino del entorno Spark. EMR da control total del cluster (Spark, Hive, Presto, HBase...), mejor para cargas muy grandes/personalizadas o si ya tienes expertise en Hadoop/Spark y quieres optimizar costos con instancias. `Glue = conveniencia`; `EMR = control y flexibilidad`.
- **Glue vs Lambda**: para transformaciones muy ligeras y rápidas event-driven, Lambda puede bastar; para ETL real con volumen y Spark, Glue.
- **Glue Python Shell vs Spark job**: tareas ligeras de un nodo → Python Shell (más barato); volumen distribuido → Spark.

## Seguridad e integración

- IAM roles para que los jobs accedan a las fuentes (el patrón de roles que hemos visto).
- Lake Formation se integra encima del Data Catalog para control de acceso granular (column/row-level).
- Cifrado con KMS, conexiones privadas vía VPC.
- Integración nativa con S3, Redshift, RDS, DynamoDB, Kinesis, MSK, Athena, EMR.




# Hive y el Hive Metastore

## ¿Qué es Apache Hive?

Hive es una herramienta del ecosistema Hadoop, creada originalmente por Facebook, que resolvió un problema concreto: en los primeros días del big data, para procesar datos en Hadoop tenías que escribir programas MapReduce en Java — complejo y tedioso.

Hive introdujo la idea de poder consultar esos datos con SQL (o algo muy parecido, llamado HiveQL) en lugar de programar MapReduce. Es decir, Hive te deja tratar archivos que viven en un sistema de archivos distribuido (HDFS, o S3) como si fueran tablas de una base de datos, y consultarlos con SQL.

La clave conceptual: los datos siguen siendo archivos (CSV, Parquet, etc.) en el almacenamiento. Hive solo pone una "capa de tabla" por encima para poder consultarlos con SQL. Esto se conoce como "schema-on-read": el archivo no cambia; le aplicas una estructura de tabla al momento de leerlo.

## ¿Qué es el Hive Metastore?

Aquí está el punto central. Para que Hive pueda tratar un archivo como una tabla, necesita saber:
- ¿Qué columnas tiene y de qué tipo?
- ¿Dónde están los archivos (qué ruta en HDFS/S3)?
- ¿En qué formato están (CSV, Parquet...)?
- ¿Cómo están particionados?

Toda esa información es metadata. El Hive Metastore es el repositorio donde se guarda esa metadata. Es, esencialmente, un catálogo que mapea "nombre de tabla → esquema + ubicación + formato de los archivos reales".

```
Hive Metastore (metadata)              Datos reales (archivos)
─────────────────────────              ──────────────────────
tabla "ventas":                        s3://lake/ventas/
- columnas: fecha, monto        ───►   ventas_2025.parquet
- ubicación: s3://lake/ventas/         ventas_2024.parquet
- formato: Parquet    
```

El Metastore no guarda los datos, solo la descripción de cómo interpretarlos. ¿Te suena familiar? Es exactamente lo que hace el Glue Data Catalog.

El Hive Metastore se volvió un estándar de facto

Aquí está lo importante: con el tiempo, el Hive Metastore dejó de ser "solo de Hive". Se convirtió en el estándar de la industria para catálogos de metadata en big data. Muchísimas herramientas lo adoptaron como la forma estándar de saber "qué tablas existen y dónde están los datos":

- Apache Spark puede usar un Hive Metastore.
- Presto / Trino (motores de consulta) lo usan.
- Apache Hive mismo, obviamente.
- Herramientas en EMR, etc.

### Qué significa "el Glue Data Catalog es compatible con el Hive Metastore"

Ahora la frase cobra sentido. Significa que el Glue Data Catalog puede funcionar como un Hive Metastore — habla ese "idioma estándar". Las implicaciones prácticas:

1. Drop-in replacement: cualquier herramienta que espere un Hive Metastore (Spark, Presto, Hive en EMR, etc.) puede usar el Glue Data Catalog en su lugar, sin cambios significativos. Glue se presenta como si fuera un Hive Metastore.

2. Managed y serverless: en vez de tener que instalar, operar y mantener tu propio Hive Metastore (que tradicionalmente corre sobre una base de datos relacional que tú administras, normalmente en un cluster Hadoop/EMR), AWS te lo da managed y serverless con el Glue Data Catalog. Un dolor de cabeza operativo menos.

3. Migración fácil: si vienes de un entorno Hadoop on-premise con un Hive Metastore, puedes migrar esa metadata al Glue Data Catalog.

4. Interoperabilidad total en AWS: como EMR (que corre Spark/Hive/Presto) entiende Hive Metastore, puede usar directamente el Glue Data Catalog — por eso Athena, Redshift Spectrum, EMR y Glue ETL comparten el mismo catálogo. Todos hablan el mismo idioma de metadata.

Por qué esto importa para el examen

El mensaje de fondo: el Glue Data Catalog es un Hive Metastore managed y serverless, lo que lo convierte en el catálogo universal del data lake en AWS. Esa compatibilidad es la razón técnica por la que un solo catálogo sirve a tantos servicios distintos. Cuando el examen menciona migrar un Hive Metastore, o compartir metadata entre EMR y Athena, la respuesta suele girar en torno al Glue Data Catalog.