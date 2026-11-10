# Amazon MSK (Managed Streaming for Apache Kafka)

MSK es el servicio managed de AWS para Apache Kafka. Es la alternativa a Kinesis Data Streams para streaming, pensada para quienes ya usan Kafka o necesitan su ecosistema.

Kafka es una plataforma open-source de streaming distribuido, un log de eventos durable, particionado y replicado. Es el estándar de la industria para pipelines de eventos. Sus conceptos se parecen mucho a los de Kinesis, con otros nombres:

| Concepto Kafka | Equivalente Kinesis          | Qué es                                                   |
| -------------- | ---------------------------- | -------------------------------------------------------- |
| Topic          | Stream                       | Canal lógico de eventos                                  |
| Partition      | Shard                        | Unidad de paralelismo y orden                            |
| Producer       | Producer                     | Quien escribe                                            |
| Consumer       | Consumer                     | Quien lee                                                |
| Consumer group | Aplicación KCL               | Conjunto de consumidores que se reparten las particiones |
| Offset         | Sequence number / checkpoint | Posición de un registro en la partición                  |
| Broker         | (gestionado por AWS)         | Servidor Kafka que almacena y sirve datos                |


Detalles clave de Kafka:
- Un topic se divide en particiones; el orden se garantiza dentro de una partición.
- El productor usa una key para decidir la partición (igual que la partition key).
- Cada partición se replica entre brokers (replication factor), con un líder y réplicas follower. Si el líder cae, otra réplica toma el relevo.
- Los datos se retienen según configuración (tiempo o tamaño), y leer no los borra. Los consumidores controlan su offset, así que pueden releer.
- Consumer groups: dentro de un grupo, cada partición es leída por un solo consumidor (escalado y reparto). Distintos grupos leen el mismo topic de forma independiente.

## Qué aporta MSK

Operar Kafka por tu cuenta es complejo: aprovisionar brokers, gestionar ZooKeeper (o KRaft), parches, replicación, recuperación ante fallos. MSK lo gestiona por ti:

- Provisiona y mantiene los brokers y el plano de control.
- Los despliega en múltiples AZs (normalmente 2 o 3) con replicación.
- Detecta y reemplaza brokers fallidos automáticamente.
- Mantiene compatibilidad total con las APIs de Kafka: tus aplicaciones y herramientas existentes funcionan sin cambios.
- Se integra con CloudWatch, IAM, KMS, VPC y el ecosistema AWS.

No gestionas el servidor, pero sí decides cosas de Kafka: topics, particiones, retención, replication factor. Es menos "serverless" que Firehose o Kinesis On-Demand.

## Modos de despliegue

MSK Provisioned
- Eliges el tipo y número de brokers y el storage por broker.
- Control sobre configuración y capacidad.
- Broker types: Standard (más flexible) y Express (más rendimiento y escalado más rápido, almacenamiento elástico).
- Tiered Storage: mueve datos antiguos a un almacenamiento más barato, lo que permite retención larga a bajo costo.

MSK Serverless
- No gestionas brokers ni capacidad: escala automáticamente según el tráfico.
- Pagas por uso (throughput y storage).
- Ideal para cargas variables o impredecibles, o para empezar sin dimensionar.
- Tiene algunas limitaciones frente a Provisioned (menos configuración, autenticación basada en IAM).

## Seguridad en MSK

Autenticación (muy preguntado):
- IAM access control: usa roles/policies de IAM para autenticar y autorizar, sin gestionar credenciales aparte. Es el único método en Serverless.
- SASL/SCRAM: usuario y contraseña, almacenados en Secrets Manager.
- mTLS: autenticación mutua con certificados de clientes (con AWS Private CA).
- También existe el modo sin autenticación (no recomendado).

Cifrado:
- At rest con KMS.
- In transit con TLS entre clientes y brokers, y entre brokers.

Red:
- Los brokers viven dentro de tu VPC, en subnets que eliges. Los clientes deben tener conectividad de red a la VPC (misma VPC, peering, Transit Gateway, VPN, PrivateLink/multi-VPC).
- Se controla con security groups.

> Contraste con Kinesis: Kinesis es un servicio regional accesible por API pública con IAM; MSK vive en tu VPC.

## Ingesta y consumo: integraciones

### MSK Connect

Servicio managed para ejecutar Kafka Connect, el framework de Kafka para mover datos desde y hacia sistemas externos sin escribir código, mediante conectores:
- Source connectors: traen datos a Kafka (desde bases de datos con CDC, como Debezium, desde archivos, etc.).
- Sink connectors: llevan datos de Kafka a destinos (S3, Redshift, OpenSearch, bases de datos, etc.).

Es el equivalente a lo que Firehose hace por Kinesis. MSK no tiene un "Firehose" propio, pero tiene MSK Connect.

Consumidores nativos de AWS
- Lambda: puede consumir de MSK mediante un event source mapping (también de Kafka autogestionado).
- Managed Service for Apache Flink: lee de MSK, procesa y escribe a destinos.
- Glue Streaming ETL: puede leer de MSK/Kafka.
- Firehose: puede usar MSK como fuente (con ciertas configuraciones).
- Redshift Streaming Ingestion: ingesta desde MSK directamente a una materialized view.
- EMR / Spark Structured Streaming.

### Schema Registry

Se integra con el Glue Schema Registry (Avro, JSON Schema, Protobuf) para gestionar la evolución de esquemas.

### Monitoreo

- CloudWatch con métricas a distintos niveles (cluster, broker, topic).
- Open monitoring con Prometheus (JMX y Node exporters).
- Broker logs hacia CloudWatch Logs, S3 o Firehose.
- Métrica clave: consumer lag (offset lag), análoga al IteratorAge de Kinesis.

### Escalado

- Escalar brokers: agregar brokers al cluster (después hay que reasignar particiones para repartir la carga).
- Escalar storage: aumentar el volumen por broker (auto scaling de storage disponible). Solo crece, no se reduce.
- Cambiar tipo de broker: posible, con impacto controlado.
- Aumentar particiones de un topic: se puede, pero no se pueden reducir, y cambia el mapeo key→partición (afecta el orden por key).
- Con Serverless, todo es automático.

### Límites de mensajes

- Kafka maneja por defecto mensajes de ~1 MB, y MSK permite aumentarlo (configurable). KDS tiene un tope de 1 MB por registro, así que es una diferencia a tener presente.

## MSK vs Kinesis Data Streams

|                        | Kinesis Data Streams   | Amazon MSK                                        |
| ---------------------- | ---------------------- | ------------------------------------------------- |
| Tecnología             | Propietaria de AWS     | Apache Kafka open-source                          |
| Unidad                 | Shard                  | Partition                                         |
| Tamaño máx. de mensaje | 1 MB                   | Configurable (default 1 MB, ampliable)            |
| Retención              | 1 a 365 días           | Configurable, ilimitada con tiered storage        |
| Capacidad              | Shards (o On-Demand)   | Brokers (o Serverless)                            |
| Operación              | Muy simple, cero Kafka | Más configuración (topics, particiones)           |
| Red                    | API regional, IAM      | Dentro de tu VPC                                  |
| Autenticación          | IAM                    | IAM, SASL/SCRAM, mTLS                             |
| Ecosistema             | Integración nativa AWS | Ecosistema Kafka (Connect, Streams, herramientas) |
| Portabilidad           | Atado a AWS            | Portable (Kafka estándar)                         |
| Entrega a destinos     | Firehose               | MSK Connect                                       |


## Cuándo elegir cada uno

- **MSK**: ya usas Kafka (migrar on-premise sin reescribir), necesitas el ecosistema Kafka (Kafka Streams, Connect, Debezium), portabilidad/multi-cloud, mensajes grandes o retención muy larga.
- **Kinesis**: quieres lo más simple y nativo de AWS, sin gestionar nada de Kafka, integrado con Lambda, Firehose, etc.

> La frase típica del examen: "migrar una aplicación Kafka existente a AWS con el mínimo cambio" → MSK.