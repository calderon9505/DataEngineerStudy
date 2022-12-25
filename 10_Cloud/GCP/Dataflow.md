# Dataflow

[Introducción a Dataflow](https://www.youtube.com/watch?v=Bo8ztVTWWA8&ab_channel=GoogleCloudTech)

Servicio **unificado** de procesamiento streaming y batch, totalmente administrado, con modelo de programación de código abierto y con capacidad de escalar inteligentemente a millones de operaciones por segundo.

> Dataflow es un sistema distribuido que asegura procesado **exactly one** (cada elemento de la entrada se procesa una sola vez y se escribe exactamente una vez a la salida, esto se garantiza incluso en caidas de nodos)

Cuando se tiene procesamiento streaming se obtienen resultados inmediatos pero no tan precisos. Cuando se tiene procesamiento batch se obtienen resultados más precisos pero más lentos. De aquí surge la arquitectura Lambda

## Arquitectura Lambda

Arquitectura donde se tiene tanto procesamiento en streaming como batch. Pero, aquí no se tienen dos flujos distintos (streaming y batch), sino que se tiene un *modelo de datos unificado*.

Para esto se usa el SDK de Apache Beam, en donde se define un flujo de datos; se puede emitir resultados rápidamente (antes de que los datos estén completos), y se encarga de que los datos que lleguen tarde vuelvan a se calculados para tener resultados completos y precisos.

Los flujos de datos son portables. Se pueden ejecutar en Spark, Flink o en Dataflow.

# Conceptos

## Pipelines (flujos de procesamiento)

Encapsulan toda la tarea de procesamiento de principio a fin. Es decir, todo el proceso ETL.

## PCollection (Contenedor de datos ilimitado e inmutable)

Conjunto de datos que procesará. Es ilimitado en el sentido que se lee de una fuente de datos que se actualiza continuamente (e.g. Pub/Sub o Kafka). Son inmutable, por lo que al operar con ellos se creará otro PCollection con los datos modificados.

## PTransform (cambio de datos)

Toman una PCollection, procesan los datos, y entregan cero, una o más PCollection.

## I/O transforms

Leer y escribir en distintos sistemas.


# El "Stack"

* **Flujo de datos** final.
* **Bibliotecas**. Transformaciones, fuentes/destinos, etc.
* **SDK específico del lenguaje**. Java, Python, etc.
* **Modelo Beam**. ParDo, GBK, Windowing.
* **Ejecutor**. Dataflow, Spark, Apache Flink.
* **Entorno de ejecución**. Nube, On premise, local.

Apache Beam se involucra en el SDK, el Modelo Beam y el Ejecutor.