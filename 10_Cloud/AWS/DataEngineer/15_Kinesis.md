# Amazon Kinesis

Kinesis es la familia de servicios de AWS para streaming de datos en tiempo real — ingerir y procesar datos que llegan continuamente (en lugar de por lotes). "Kinesis" no es un solo servicio sino una familia:

| Servicio                                                        | Propósito                                                                         |
| --------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Kinesis Data Streams (KDS)                                      | Ingesta de streams en tiempo real, con control fino y reprocesamiento. El "core". |
| Kinesis Data Firehose                                           | Entrega (load) de streams a destinos, serverless y sin gestión.                   |
| Managed Service for Apache Flink (antes Kinesis Data Analytics) | Procesar/analizar streams en tiempo real (SQL o Flink).                           |
| Kinesis Video Streams                                           | Streaming de video (poco relevante para el DEA-C01).                              |


La distinción Data Streams vs Firehose es de las más preguntadas del examen, así que ponles atención especial.

El contexto: streaming vs batch

Antes de entrar, el porqué. El procesamiento batch (lotes) toma datos acumulados y los procesa periódicamente (lo que hace Glue, por ejemplo). El streaming procesa los datos a medida que llegan, continuamente, con baja latencia. Casos: telemetría IoT, logs de aplicaciones, clickstreams, métricas en vivo, detección de fraude en tiempo real. Kinesis es la base de esos pipelines en AWS.

---
---

# Kinesis Data Streams (KDS)

Es el servicio core de streaming: un "tubo" de datos en tiempo real, duradero y de alto rendimiento, donde productores escriben datos y consumidores los leen, con capacidad de reprocesar porque los datos se retienen un tiempo.

## Shards 
Un stream se compone de **shards** (fragmentos). El shard es la unidad de capacidad y paralelismo de KDS. Entender los shards es entender KDS.

Cada shard provee una capacidad fija:
- Escritura (ingesta): 1 MB/s o 1,000 registros/s.
- Lectura: 2 MB/s (compartidos entre los consumidores en modo estándar).

La capacidad total del stream = suma de sus shards. Si necesitas más throughput, agregas shards (esto se llama resharding: shard splitting para aumentar, shard merging para reducir).

```
Productores → [ Shard 1 ]
            → [ Shard 2 ]  → Consumidores
            → [ Shard 3 ]
(cada shard = 1 MB/s in, 2 MB/s out)
```

## Partition Key y ordenamiento

Cuando un productor envía un registro, incluye una **partition key**. Kinesis aplica un hash sobre esa key para decidir a qué shard va el registro (igual idea que la partition key de DynamoDB).

Esto tiene una consecuencia clave sobre el orden:
- KDS garantiza el orden DENTRO de un shard, no a través de todo el stream.
- Todos los registros con la misma partition key van al mismo shard → se mantienen ordenados entre sí.
- Por eso, si necesitas orden por cierta entidad (ej. todos los eventos de un mismo cliente_id en orden), usas esa entidad como partition key.
- Cuidado: una partition key mal elegida (poca cardinalidad) crea un hot shard (un shard sobrecargado), igual que las hot partitions de DynamoDB.

Cada registro recibe además un **sequence number** (número de secuencia) único y creciente dentro del shard, que marca su posición.

## Retención de datos

Los datos en KDS se retienen un tiempo configurable, durante el cual pueden leerse y releerse múltiples veces:
- Por defecto: 24 horas (1 día).
- configuración estándar: 7 días
- long-term retention: hasta 365 días

Esto habilita:
- Múltiples consumidores leyendo el mismo stream independientemente.
- Reprocesamiento: volver a leer datos pasados (ej. si un consumidor falló o quieres recalcular). Esta capacidad de "rebobinar" es una diferencia fundamental con Firehose (que no retiene).

## Producers

Formas de escribir a KDS:
- **Kinesis Producer Library (KPL)**: librería optimizada (batching, agregación de registros, reintentos) para alto rendimiento.
- **AWS SDK**: `PutRecord` / `PutRecords` (envío básico).
- **Kinesis Agent**: agente que monitorea archivos de log y los envía automáticamente.

## Consumers

Formas de leer:
- **Kinesis Client Library (KCL)**: librería que gestiona la lectura, el checkpoint (dónde te quedaste) y el reparto de shards entre instancias consumidoras.
- **AWS SDK**: `GetRecords`.
- **AWS Lambda**: se integra nativamente (Lambda consume del stream y procesa cada batch).
- **Firehose, Managed Service for Apache Flink**: pueden consumir de KDS.

Hay dos modos de consumo:

- **Shared (estándar)**: todos los consumidores comparten los 2 MB/s de lectura de cada shard. Con muchos consumidores, se saturan entre sí y aumenta la latencia. Usa pull (GetRecords).
- **Enhanced Fan-Out (EFO)**: cada consumidor obtiene su propio canal dedicado de 2 MB/s por shard (no comparte). Usa push (Kinesis empuja los datos al consumidor) con menor latencia (~70 ms). Ideal cuando tienes múltiples consumidores que necesitan todo el throughput sin estorbarse. Cuesta más. (SubscribeToShard)

## Capacity Modes

Como DynamoDB, KDS tiene dos modos:

- **Provisioned**: tú defines el número de shards. Pagas por shard-hora. Controlas y predices la capacidad. Si el tráfico supera lo provisionado → throttling (ProvisionedThroughputExceededException) → reintentar con exponential backoff.
- **On-Demand**: Kinesis gestiona y escala los shards automáticamente según el tráfico. Pagas por datos. Ideal para cargas impredecibles/variables, sin gestionar shards.

## Seguridad
- Encryption at rest con KMS, in transit con TLS.
- Acceso con IAM.
- VPC endpoints (PrivateLink) para acceso privado.

## Kinesis Data Streams vs Amazon SQS

Ambos son para desacoplar/mover mensajes, pero son diferentes:
- KDS: streaming, múltiples consumidores leen los mismos datos, retención y reproceso, orden por shard, ideal para analytics en tiempo real de alto volumen.
- SQS: cola de mensajes; típicamente un mensaje se consume y se borra (un solo "equipo" de consumidores), sin reproceso, enfocado en desacoplar componentes.

## Comandos básicos de Kinesis Data Streams KDS

### Gestión del stream

```bash
aws kinesis create-stream --stream-name mi-stream --shard-count 2 # (modo provisioned)
aws kinesis create-stream --stream-name mi-stream --stream-mode-details StreamMode=ON_DEMAND
aws kinesis list-streams
aws kinesis describe-stream --stream-name mi-stream
```

### Escribir datos (producers)

Un solo registro
```bash
aws kinesis put-record \
--stream-name mi-stream \
--partition-key cliente-42 \
--data "hola mundo" \
--cli-binary-format raw-in-base64-out
```

Varios registros en una llamada (hasta 500)
```bash
aws kinesis put-records \
--stream-name mi-stream \
--records Data=ZXZlbnRvMQ==,PartitionKey=cliente-42 \
            Data=ZXZlbnRvMg==,PartitionKey=cliente-43
```

>Los datos se envían en base64 si no usas --cli-binary-format raw-in-base64-out. 

> put-records puede tener fallos parciales, así que hay que revisar FailedRecordCount en la respuesta y reintentar.

### Leer datos (consumers)

La lectura con la CLI es en dos pasos: obtener un shard iterator y luego leer con él.

1. Obtener iterator
```
aws kinesis get-shard-iterator \
--stream-name mi-stream \
--shard-id shardId-000000000000 \
--shard-iterator-type TRIM_HORIZON
```

2. Leer registros con el iterator obtenido
```
aws kinesis get-records --shard-iterator <ITERATOR>
```

### Tipos de `--shard-iterator-type`:
- **TRIM_HORIZON**: desde el registro más antiguo disponible.
- **LATEST**: solo registros nuevos a partir de ahora.
- **AT_TIMESTAMP**: desde un momento específico (con --timestamp).
- **AT_SEQUENCE_NUMBER** / AFTER_SEQUENCE_NUMBER: desde/después de un sequence number concreto.

---
---

# Kinesis Data Firehose

Firehose es el servicio de entrega (delivery/load) de streams. Su propósito es tomar datos de streaming y cargarlos de forma confiable en un destino, sin que gestiones nada de infraestructura. Es la vía más fácil para llevar streaming a un data lake/warehouse.

Características fundamentales

- **Totalmente serverless y managed**: no hay shards que gestionar, escala automáticamente. Esta es la gran diferencia operativa con KDS.
- **Near real-time NRT, no real-time puro**: entrega en micro-batches según un buffer. Hay una latencia mínima (segundos), no es milisegundos.
- **No retiene datos / no permite reprocesamiento**: una vez entregados al destino, Firehose no los guarda. No puedes "rebobinar" como en KDS.

## Destinations

Firehose entrega a un conjunto de destinos predefinidos:
- Amazon S3 (el más común — para el data lake).
- Amazon Redshift (vía S3 + COPY automático).
- Amazon OpenSearch Service.
- Destinos de terceros (Splunk, Datadog, New Relic, mongoDB) 
- Destinos personalizados con HTTP endpoints.
- Más recientemente, tablas Apache Iceberg.

## Buffering

Firehose acumula los datos en un buffer antes de entregarlos, y los envía cuando se cumple lo que ocurra primero de dos condiciones:
- **Buffer size**: un tamaño (ej. 5 MB) → cuando el buffer llena, entrega.
- **Buffer interval**: un tiempo (ej. 300 segundos) → cuando pasa el tiempo, entrega lo acumulado.

Este buffering es lo que hace que Firehose sea Near real-time NRT: ajustas el equilibrio entre latencia (buffer pequeño/corto = más rápido) y eficiencia (buffer grande = archivos más grandes, menos operaciones). Conecta con lo que vimos de cargar Redshift en microlotes.

## Transformación y conversión de formato

Firehose puede transformar los datos en vuelo antes de entregarlos:

- **Transformación con Lambda**: invoca una función Lambda para transformar/enriquecer/filtrar cada batch (ej. limpiar, reformatear, agregar campos).
- **Conversión de formato nativa**: puede convertir JSON → Parquet u ORC automáticamente (formatos columnares), usando el esquema del Glue Data Catalog. Esto es muy útil: ingieres JSON y aterriza en el lake como Parquet optimizado, sin un job aparte.
- Compresión (GZIP, Snappy, etc.) y cifrado.
- **dynamic partitioning**: particionar los datos al escribir en S3 según valores de los registros (ej. por fecha o por cliente) → genera la estructura de particiones Hive-style automáticamente.

---
---

|                       | Data Streams (KDS)                                 | Firehose                                            |
| --------------------- | -------------------------------------------------- | --------------------------------------------------- |
| Propósito             | Ingesta de stream con control y reprocesamiento    | Entrega/carga a destinos                            |
| Gestión               | Gestionas shards (o On-Demand)                     | Serverless, sin gestión                             |
| Latencia              | Real-time (~200 ms, o ~70 ms con EFO)              | Near real-time NRT (buffering, segundos)                |
| Retención / reproceso | Sí (1–365 días), múltiples consumidores            | No retiene, no reprocesa                            |
| Destinos              | Código/consumidores custom (Lambda, KCL, Flink...) | Destinos predefinidos (S3, Redshift, OpenSearch...) |
| Transformación        | La haces tú (consumidor)                           | Lambda + conversión a Parquet/ORC integrada         |
| Escalado              | Manual (shards) o On-Demand                        | Automático                                          |


---
---

# Managed Service for Apache Flink (antes Kinesis Data Analytics)

Es el servicio para procesar y analizar streams en tiempo real. Permite ejecutar lógica de procesamiento continuo sobre los datos mientras fluyen:

- Basado en Apache Flink (framework líder de stream processing). Escribes aplicaciones en Java/Scala/Python, o usas Flink SQL.
- También existe el modo SQL más simple (histórico de Kinesis Data Analytics) para consultas sobre streams.
- Capacidades típicas de streaming: windowing (agregaciones por ventanas de tiempo), joins de streams, detección de patrones, agregaciones continuas.
- Lee de KDS o MSK, procesa, y escribe a destinos (KDS, Firehose, S3, etc.).
- Casos: analytics en vivo, métricas en tiempo real, detección de anomalías/fraude, ETL de streaming.

> Es la pieza de procesamiento del stream (mientras KDS ingiere y Firehose entrega).



---
---

# Formatos de datos en streaming

En streaming, a diferencia del batch, los datos llegan registro por registro (o en micro-lotes pequeños). Por eso se prefieren formatos row-based (por filas), no columnares como Parquet, que necesitan acumular muchos registros para ser eficientes.

JSON
- El más común: legible, flexible, soportado en todo.
- Ineficiente: es texto, repite los nombres de campo en cada registro, no tiene schema forzado.
- Típico en logs de aplicaciones, eventos web y APIs.

CSV
- Simple y compacto para datos planos.
- Sin tipos ni estructuras anidadas, frágil ante cambios de columnas.

Avro
- Binario, row-based, compacto, y el schema viaja o se referencia con los datos.
- Soporta bien la schema evolution (agregar o quitar campos sin romper consumidores).
- Es el formato estándar en ecosistemas Kafka/MSK. Se combina con el Glue Schema Registry.

Protobuf (Protocol Buffers)
- Binario, muy compacto y rápido, con schema definido (.proto).
- Común en sistemas de alto rendimiento y microservicios.
- Soportado por Glue Schema Registry.

Parquet / ORC
- Columnares, no se usan en el stream como tal. Aparecen al aterrizar el dato en el data lake.
- Ejemplo: Firehose convierte JSON → Parquet/ORC al entregar a S3.

> El patrón habitual es formato row-based en tránsito (JSON/Avro/Protobuf) y columnar en reposo (Parquet/ORC en S3).

# Otros conceptos de streaming

1. Delivery semantics (garantías de entrega)
    - **At-most-once**: puede perder mensajes, nunca duplica.
    - **At-least-once**: no pierde, pero puede duplicar. Es lo habitual en Kinesis.
    - **Exactly-once**: ni pierde ni duplica; es difícil y suele lograrse con procesamiento idempotente o con Flink (checkpoints).

2. Windowing (ventanas de tiempo)

    Un stream es infinito, así que para agregar (sumas, conteos) se agrupa por ventanas:
    - **Tumbling window**: ventanas fijas que no se solapan (ej. cada 5 min).
    - **Sliding window**: ventanas de tamaño fijo que se solapan y se desplazan (ej. últimos 5 min, recalculado cada minuto).
    - **Session window**: se agrupa por períodos de actividad, cerrándose tras un tiempo de inactividad (ej. sesión de un usuario).

3. Event time vs Processing time
    - **Event time**: cuándo ocurrió el evento realmente.
    - **Processing time**: cuándo lo procesa el sistema.

    > Pueden diferir por latencia de red o fallos.

4. Late data y watermarks

    Los eventos pueden llegar tarde o desordenados. Un watermark es un mecanismo (Flink y similares) que define hasta cuándo esperar eventos tardíos antes de cerrar una ventana.

5. Checkpointing / offsets

    Los consumidores registran hasta dónde han leído para retomar tras un fallo.
    - En Kinesis lo gestiona KCL, guardando el estado en DynamoDB.
    - En Kafka se llama offset.

6. Backpressure

    Ocurre cuando el consumidor no da abasto con la velocidad del productor. El sistema debe absorberlo con buffers, escalando o limitando el flujo. En Kinesis se manifiesta como throttling o lag creciente.

7. Consumer lag

    La diferencia entre lo último escrito en el stream y lo último procesado. Es una métrica clave de monitoreo. En Kinesis: GetRecords.IteratorAgeMilliseconds en CloudWatch. Si crece, tus consumidores se están quedando atrás.

8. Stateful vs stateless processing
    - **Stateless**: cada evento se procesa solo (filtrar, transformar).
    - **Stateful**: requiere recordar información previa (agregaciones, joins, conteos). Flink gestiona ese estado y lo respalda con checkpoints.

9. Lambda architecture vs Kappa architecture
    - **Lambda**: dos caminos paralelos, batch (preciso) y speed/streaming (rápido).
    - **Kappa**: un solo camino de streaming, reprocesando desde el log cuando hace falta.

10. Schema evolution y Schema Registry

    Los productores cambian sus esquemas con el tiempo. El Glue Schema Registry valida la compatibilidad (backward/forward) para no romper a los consumidores.

11. Dead-letter queue (DLQ)

    Los registros que fallan al procesarse repetidamente se desvían a una cola aparte (SQS o SNS) para no bloquear el stream. Es muy relevante con Lambda consumiendo de Kinesis, donde un registro "venenoso" puede bloquear el shard si no se maneja.

## Parquet VS ORC

Qué tienen en común

- Almacenamiento columnar: guardan cada columna junta, así que una consulta lee solo las columnas que necesita (menos I/O).
- Compresión eficiente, porque los datos de una misma columna son homogéneos.
- Schema embebido en el archivo y soporte de tipos complejos (structs, arrays, maps).
- Predicate pushdown: guardan estadísticas (min/max, etc.) por bloque para saltarse datos que no cumplen el filtro.
- Son splittable, es decir, se pueden procesar en paralelo.
- Los soportan Athena, Redshift Spectrum, Glue, EMR y Firehose (conversión JSON → Parquet/ORC).

Diferencias

|                      | Parquet                                         | ORC                                                                  |
| -------------------- | ----------------------------------------------- | -------------------------------------------------------------------- |
| Origen               | Twitter + Cloudera (ecosistema Hadoop genérico) | Hortonworks + Facebook (nació para Hive)                             |
| Ecosistema ideal     | Spark, Athena, Redshift Spectrum, casi todo     | Hive y Presto/Trino                                                  |
| Popularidad          | Más extendido, estándar de facto                | Menos usado fuera de Hive                                            |
| Estructuras anidadas | Muy bueno con datos anidados                    | Bueno, pero con más fuerza en datos planos                           |
| Compresión           | Muy buena (Snappy por defecto)                  | Suele comprimir algo mejor (Zlib por defecto)                        |
| Índices internos     | Estadísticas por row group/página               | Índices y estadísticas por stripe, más ricos (incluye bloom filters) |
| Soporte ACID en Hive | No nativo                                       | Sí, es el formato nativo de las tablas transaccionales de Hive       |

La estructura interna también cambia: Parquet organiza en row groups → column chunks → pages, y ORC en stripes (con footer e índices).

Cuál elegir

- Parquet: opción por defecto en la mayoría de casos, sobre todo con Spark, Athena y lakes de propósito general. Es lo que el examen asume salvo que se diga otra cosa.
- ORC: tiene sentido si tu entorno gira alrededor de Hive (EMR con Hive) o necesitas tablas transaccionales de Hive.