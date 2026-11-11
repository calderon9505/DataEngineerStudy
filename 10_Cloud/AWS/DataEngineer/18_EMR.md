# Amazon EMR (Elastic MapReduce)

EMR es la plataforma managed de AWS para ejecutar frameworks de big data (Spark, Hadoop, Hive, Presto/Trino, HBase, Flink, etc.) a gran escala. Es el "primo con control total" de Glue: más flexibilidad y potencia, a cambio de más configuración. 

Contexto: Procesar volúmenes enormes de datos requiere computación distribuida: repartir el trabajo entre muchas máquinas. Hadoop fue el primer ecosistema masivo para eso, y Spark lo superó en velocidad (procesa en memoria). Montar y operar un cluster Hadoop/Spark por tu cuenta es complejo (instalación, configuración, versiones, escalado, fallos). EMR lo aprovisiona y gestiona por ti, manteniendo acceso a los frameworks open-source con sus configuraciones.

## Modos de despliegue:

1. EMR on EC2 (el clásico)

    Un cluster de instancias EC2 con los frameworks instalados. Tú eliges tipos de instancia, tamaño, aplicaciones y configuración. Máximo control.

2. EMR on EKS

    Ejecuta trabajos de Spark sobre un cluster de Kubernetes (EKS) existente, compartiendo infraestructura con otras cargas en contenedores. Útil si ya estandarizaste en Kubernetes y quieres consolidar recursos.

3. EMR Serverless

    Sin clusters que gestionar: envías un job (Spark o Hive) y EMR asigna y escala la capacidad automáticamente. Pagas por vCPU, memoria y storage usados mientras corre. Es la opción cuando quieres el ecosistema Spark sin administrar infraestructura.

## Arquitectura de un cluster (EMR on EC2)

Un cluster tiene tres tipos de nodos (node types), pregunta clásica:

- **Primary node (master)**: coordina el cluster, gestiona la distribución de tareas, ejecuta servicios como el YARN ResourceManager y el HDFS NameNode. Uno por cluster (se pueden usar 3 para alta disponibilidad). Si cae sin HA, el cluster falla.
- **Core nodes**: ejecutan tareas y almacenan datos en HDFS. Si los eliminas, puedes perder datos HDFS, por eso son más delicados de reducir.
- **Task nodes** (opcionales): solo ejecutan tareas, sin almacenar HDFS. Perfectos para escalar cómputo y para usar Spot instances porque perderlos no pierde datos.

```
Primary (coordina)
    ├── Core nodes  (cómputo + HDFS)
    └── Task nodes  (solo cómputo, ideales para Spot)

```

## Almacenamiento: HDFS, EMRFS y local

- **HDFS**: sistema de archivos distribuido del cluster, en los discos de los nodos core. Rápido (local), pero efímero: desaparece al terminar el cluster.
- **EMRFS**: permite que EMR use S3 como sistema de archivos (s3://). Es el patrón recomendado: datos persistentes en S3, el cluster solo computa. Así se desacopla cómputo y almacenamiento.
- **Instance store / EBS**: discos locales de cada nodo para datos temporales o intermedios.

> El patrón moderno es S3 como data lake y clusters efímeros: lees de S3, procesas, escribes a S3 y apagas el cluster. Pagas solo mientras procesas.

## Tipos de cluster

- **Transient**: se crea para un trabajo y se termina al acabar (auto-terminate). Ideal para ETL batch programado. Minimiza costos.
- **Long-running**: queda encendido, sirve consultas interactivas, notebooks o aplicaciones como HBase. Más caro, útil para uso continuo.

## Escalado

- **Managed Scaling**: EMR ajusta automáticamente el número de nodos según la carga (recomendado, más simple).
- **Custom Auto Scaling**: reglas propias basadas en métricas de CloudWatch.
- Resize manual de core/task nodes.

## Modelos de compra y ahorro de costos

- **On-Demand**: sin compromiso, más caro.
- **Reserved / Savings Plans**: para clusters persistentes y predecibles.
- **Spot Instances**: hasta ~90% más baratas, pero pueden ser interrumpidas. Ideal para task nodes y trabajos tolerantes a fallos.
- **Instance Fleets**: mezcla tipos de instancia y opciones de compra (Spot + On-Demand) con mayor flexibilidad y mejor disponibilidad de Spot.
- **Instance Groups**: un solo tipo de instancia por grupo, más simple.

> Patrón recomendado: primary y core en On-Demand, task nodes en Spot.

## Aplicaciones y frameworks

- **Apache Spark**: el más usado; procesamiento distribuido en memoria (batch, SQL, streaming, ML).
- **Apache Hive**: SQL sobre datos (usa Hive Metastore o el Glue Data Catalog).
- **Presto / Trino**: consultas SQL interactivas rápidas (motor similar al de Athena).
- **Apache HBase**: base NoSQL wide-column sobre HDFS/S3.
- **Apache Flink**: procesamiento de streaming.
- Hadoop/MapReduce, Pig, Sqoop, Oozie, Hudi/Iceberg/Delta, Livy, Hue, Zeppelin / Jupyter (aquí reaparecen los notebooks).
- TensorFlow, MXNet y otros para ML.

## Integración con el ecosistema

- Glue Data Catalog como metastore compartido con Athena, Glue y Redshift Spectrum.
- Lake Formation para permisos granulares sobre el catálogo.
- S3 como almacenamiento principal (EMRFS).
- Kinesis / MSK como fuentes de streaming.
- DynamoDB, Redshift, RDS como fuentes/destinos.
- Step Functions / MWAA / EventBridge para orquestar clusters y steps.

## Steps y ejecución de trabajos

Un step es una unidad de trabajo enviada al cluster (un job de Spark, un script Hive, etc.), que se ejecuta en secuencia. Puedes enviar steps al crear el cluster o después. Los clusters transitorios suelen definirse como "ejecuta estos steps y termina".

## EMR Studio y notebooks

EMR Studio es un IDE web basado en Jupyter para desarrollar y depurar aplicaciones Spark sobre EMR (on EC2, EKS o Serverless), con colaboración y control de versiones con Git. Reemplaza a los EMR Notebooks clásicos.

## Seguridad

- IAM con tres roles clave:
    - Service role: el que EMR usa para aprovisionar recursos.
    - EC2 instance profile (EMR_EC2_DefaultRole): el que usan las instancias para acceder a S3, DynamoDB, etc.
    - Auto Scaling role.
- Cifrado: at rest (S3 con SSE/KMS, discos locales con LUKS/EBS, HDFS transparent encryption) e in transit (TLS).
- Security configurations para definir cifrado y autenticación de forma reutilizable.
- Red: el cluster vive en una VPC; control con security groups y subnets privadas.
- Kerberos y LDAP para autenticación de usuarios.
- Lake Formation y Apache Ranger para control de acceso granular.
- Runtime roles para dar permisos distintos por job.

## Monitoreo

- CloudWatch (métricas del cluster, ej. YARNMemoryAvailablePercentage, HDFSUtilization).
- Logs de steps y cluster archivados en S3.
- Interfaces web: Spark History Server, YARN ResourceManager, Ganglia.
- CloudTrail para llamadas a la API.

## EMR vs Glue (comparación clave)

|            | Glue                         | EMR                                                                                      |
| ---------- | ---------------------------- | ---------------------------------------------------------------------------------------- |
| Modelo     | Serverless puro              | Cluster (o Serverless/EKS)                                                               |
| Control    | Limitado                     | Total (versiones, configuración, instancias)                                             |
| Frameworks | Spark, Python Shell, Ray     | Spark, Hive, Presto, HBase, Flink, etc.                                                  |
| Operación  | Mínima                       | Mayor                                                                                    |
| Costos     | DPU-hora                     | Instancia-hora (con Spot, Reserved)                                                      |
| Mejor para | ETL estándar sin administrar | Cargas muy grandes o personalizadas, optimización de costos, ecosistema Hadoop existente |

> Criterio del examen: ETL simple y sin gestionar infraestructura → Glue. Control fino, frameworks específicos (HBase, Presto), migrar Hadoop/Spark existente u optimizar costos a gran escala con Spot → EMR. Spark sin administrar clusters pero con el ecosistema EMR → EMR Serverless.

## Casos de uso típicos

- ETL y transformación masiva de datos en el data lake.
- Migración de cargas Hadoop on-premise a AWS.
- Análisis interactivo con Presto/Trino o Spark SQL.
- Procesamiento de streaming con Spark Structured Streaming o Flink.
- Machine learning distribuido sobre grandes datasets.
- Cargas con HBase como base de baja latencia sobre datos masivos.



# HDFS (Hadoop Distributed File System)

HDFS es el sistema de archivos distribuido de Hadoop. Reparte archivos muy grandes entre muchas máquinas y los replica, de modo que se puedan procesar en paralelo y sobrevivan a fallos de nodos. Es lo que EMR llama el almacenamiento "local" del cluster.

El problema que resuelve: Un archivo de varios TB no cabe en un solo disco, y leerlo desde una sola máquina sería lentísimo. HDFS lo divide en bloques, los distribuye entre los nodos y permite que cada nodo procese el bloque que tiene localmente.

Cómo funciona

- **Blocks**: los archivos se parten en bloques grandes (128 MB por defecto). Un archivo es una colección de bloques repartidos por el cluster.
- **NameNode**: el "índice" del sistema. Guarda la metadata (qué archivos existen, de qué bloques se componen y en qué nodos está cada bloque). No guarda los datos. En EMR corre en el primary node.
- **DataNodes**: almacenan los bloques reales. En EMR son los core nodes, y por eso los task nodes no tienen HDFS.
- **Replicación**: cada bloque se copia en varios DataNodes (factor de replicación 3 por defecto, aunque en EMR depende del tamaño del cluster). Si un nodo cae, los bloques siguen disponibles en otros, y HDFS re-replica automáticamente los que quedaron con menos copias.

```
Archivo grande → [Bloque A][Bloque B][Bloque C]

Core 1: A, C     Core 2: A, B     Core 3: B, C
(cada bloque en 2+ nodos; el NameNode sabe dónde está cada uno)
```
## Data locality

Una idea clave de Hadoop: llevar el cómputo a los datos, no los datos al cómputo. YARN intenta ejecutar cada tarea en el nodo que ya tiene el bloque, evitando mover datos por la red. Es una de las razones de su velocidad.

## Características

- Optimizado para lecturas secuenciales de archivos grandes (batch), no para muchos archivos pequeños ni acceso aleatorio de baja latencia.
- Modelo write-once, read-many: los archivos se escriben y se leen, pero no se editan en medio (solo append).
- Alto throughput, escalable horizontalmente.

## HDFS en EMR vs S3 (EMRFS)

|              | HDFS                                          | S3 vía EMRFS                         |
| ------------ | --------------------------------------------- | ------------------------------------ |
| Ubicación    | Discos de los core nodes                      | Servicio S3                          |
| Persistencia | Efímero: se pierde al terminar el cluster     | Durable (11 nueves)                  |
| Latencia     | Baja (local)                                  | Mayor (red)                          |
| Costo        | Pagas los discos del cluster                  | Barato, pagas por uso                |
| Compartible  | Solo dentro del cluster                       | Cualquier servicio (Athena, Glue...) |
| Uso ideal    | Datos intermedios, caché, trabajos iterativos | Data lake, datos de entrada y salida |


Por eso el patrón recomendado es datos persistentes en S3 y HDFS solo para temporales o datos que se leen repetidamente y necesitan baja latencia.

### Usar EMR sin depender de HDFS
- Es el patrón recomendado: datos en S3 (vía EMRFS) y el cluster solo como cómputo. Esto desacopla cómputo y almacenamiento.
- Habilita clusters transitorios (se crean, procesan y se terminan) y que otros servicios (Athena, Glue, Spectrum) lean los mismos datos. EMR Serverless no usa HDFS para tus datos.
- HDFS sigue existiendo en segundo plano para datos intermedios, shuffle, spill y cachés. Por eso se necesitan core nodes aunque los datos estén en S3.
- HDFS aún conviene en trabajos iterativos (ML, grafos) o de muy baja latencia.
- Al usar solo S3: mayor latencia que HDFS, cuidado con el small files problem y uso de committers optimizados para S3. El problema de consistencia eventual ya no aplica.

### Cargar datos en HDFS al arrancar
- HDFS es efímero: un cluster nuevo arranca con HDFS vacío, así que hay que copiar los datos desde S3.
- Se hace con s3-dist-cp (o hadoop distcp), normalmente como steps del cluster.
- Flujo típico: crear cluster → s3-dist-cp S3→HDFS → job de Spark/Hive sobre HDFS → s3-dist-cp HDFS→S3 → terminar cluster. Si no copias los resultados de vuelta a S3, se pierden al terminar el cluster.
- Costos: tiempo de carga, capacidad limitada a los discos de los core nodes (y multiplicada por el factor de replicación; con 3, 1 TB ocupa 3 TB) y pagar cómputo solo para almacenar.
- Solo compensa si los mismos datos se leen muchas veces. En clusters long-running la carga se hace una vez, pero S3 sigue siendo la fuente de verdad.
- Excepción: HBase en EMR puede almacenar sus datos en S3.