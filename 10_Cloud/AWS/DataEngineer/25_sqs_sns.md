Amazon SQS (Simple Queue Service)

SQS es una cola de mensajes managed y serverless. Los productores envían mensajes a la cola y los consumidores los leen (pull) y procesan. Modelo
point-to-point: normalmente cada mensaje lo procesa un solo consumidor.

Ciclo de vida de un mensaje

1. El productor envía el mensaje (SendMessage).
2. El consumidor lo lee (ReceiveMessage). El mensaje no se borra: queda invisible durante el visibility timeout.
3. Si el consumidor termina bien, borra el mensaje (DeleteMessage).
4. Si no lo borra antes de que expire el visibility timeout (por un fallo), el mensaje reaparece y otro consumidor lo reintenta.

Esto da entrega at-least-once, así que el procesamiento debe ser idempotente.

Conceptos clave

- Visibility timeout: tiempo en que un mensaje queda oculto tras leerse (default 30 s, máx. 12 h). Debe ser mayor que el tiempo de procesamiento.
- Retención: por defecto 4 días, configurable de 1 minuto a 14 días.
- Tamaño máximo: 256 KB por mensaje. Para payloads mayores se usa el patrón de guardar el dato en S3 y enviar la referencia (Extended Client Library).
- Short polling vs long polling: el long polling (WaitTimeSeconds hasta 20 s) espera a que haya mensajes, reduce llamadas vacías y costo. Es lo
recomendado.
- Delay queues: retrasan la entrega de nuevos mensajes (hasta 15 min).
- Dead-letter queue (DLQ): cola a la que se mueven los mensajes que fallan más de maxReceiveCount veces, para analizarlos sin bloquear la cola principal.
Con redrive puedes devolverlos a la cola original.
- Escalado: prácticamente ilimitado, sin gestionar capacidad.

Tipos de cola

┌────────────┬─────────────────────────────────────┬──────────────────────────────────────────────────────────────────┐
│            │ Standard                            │ FIFO                                                             │
├────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ Throughput │ Casi ilimitado                      │ 300 msg/s (3,000 con batching); más alto en modo high throughput │
├────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ Orden      │ Best-effort                         │ Estricto dentro de un message group                              │
├────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ Entrega    │ At-least-once (posibles duplicados) │ Exactly-once processing (deduplicación)                          │
├────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ Nombre     │ Libre                               │ Debe terminar en .fifo                                           │
└────────────┴─────────────────────────────────────┴──────────────────────────────────────────────────────────────────┘

En FIFO se usan MessageGroupId (orden por grupo, análogo a la partition key) y MessageDeduplicationId (deduplicación en una ventana de 5 minutos).

Seguridad

- IAM policies y queue policies (resource-based, para acceso cross-account o para que SNS/S3/EventBridge puedan escribir en la cola).
- Cifrado en reposo con SSE (SQS-managed o KMS) y en tránsito con TLS.
- VPC endpoint para acceso privado.

Integración con Lambda y datos

- Lambda con SQS (event source mapping): Lambda hace el polling y procesa en lotes, con escalado automático. Se configuran batch size y partial batch
response para no reprocesar el lote entero si falla un mensaje.
- Buffer entre un productor rápido y un consumidor lento (por ejemplo, proteger una base de datos).
- Destino de S3 event notifications y de DLQs de otros servicios (Lambda, EventBridge).

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Amazon SNS (Simple Notification Service)

SNS es un servicio pub/sub managed. Un productor publica un mensaje en un topic y SNS lo empuja (push) a todos los suscriptores. Modelo uno a muchos
(fan-out).

Conceptos clave

- Topic: canal de publicación.
- Subscription: suscriptor y su protocolo de entrega.
- Destinos soportados: SQS, Lambda, HTTP/HTTPS, email, SMS, notificaciones push móviles y Kinesis Data Firehose.
- Message filtering: cada suscripción puede tener una filter policy (sobre atributos o el cuerpo del mensaje) para recibir solo los mensajes relevantes.
- Tamaño máximo: 256 KB.
- Sin persistencia: SNS no retiene mensajes para suscriptores que no están disponibles, aunque reintenta la entrega y admite DLQ por suscripción.
- Tipos: Standard (alto throughput, orden best-effort) y FIFO (orden estricto y deduplicación; solo se entrega a colas SQS, estándar o FIFO).
- Soporta cifrado con KMS, y message archiving y replay en topics FIFO.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

El patrón fan-out: SNS + SQS

Un solo evento debe procesarse por varios sistemas independientes:

Productor → SNS topic → SQS cola A → Consumidor A (ETL)
                    → SQS cola B → Consumidor B (auditoría)
                    → Lambda     → Notificación

- Cada consumidor tiene su propia cola, así que procesa a su ritmo y con sus reintentos.
- Si un consumidor falla, no afecta a los demás.
- Con filter policies cada cola recibe solo lo que le interesa.
- SNS necesita permiso en la queue policy para escribir en cada cola.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Comparaciones clave

SQS vs SNS

┌──────────────┬──────────────────────────────────────────────┬─────────────────────────┐
│              │ SQS                                          │ SNS                     │
├──────────────┼──────────────────────────────────────────────┼─────────────────────────┤
│ Modelo       │ Cola (pull)                                  │ Pub/sub (push)          │
├──────────────┼──────────────────────────────────────────────┼─────────────────────────┤
│ Consumidores │ Uno por mensaje (competing consumers)        │ Todos los suscriptores  │
├──────────────┼──────────────────────────────────────────────┼─────────────────────────┤
│ Persistencia │ Sí (hasta 14 días)                           │ No                      │
├──────────────┼──────────────────────────────────────────────┼─────────────────────────┤
│ Uso típico   │ Buffer, desacople, procesamiento de trabajos │ Notificaciones, fan-out │
└──────────────┴──────────────────────────────────────────────┴─────────────────────────┘

SQS vs Kinesis Data Streams

┌─────────────────┬─────────────────────────────────────┬──────────────────────────────────────────────────────┐
│                 │ SQS                                 │ Kinesis Data Streams                                 │
├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ Lectura         │ El mensaje se borra tras procesarse │ Los datos permanecen hasta expirar la retención      │
├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ Consumidores    │ Un grupo competidor                 │ Múltiples consumidores independientes                │
├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ Reprocesamiento │ No (salvo DLQ/redrive)              │ Sí                                                   │
├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ Orden           │ Solo en FIFO                        │ Por shard                                            │
├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ Escalado        │ Automático                          │ Shards u On-Demand                                   │
├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ Uso             │ Colas de trabajo, desacople         │ Streaming de alto volumen y analítica en tiempo real │
└─────────────────┴─────────────────────────────────────┴──────────────────────────────────────────────────────┘

SNS vs EventBridge

- SNS: fan-out simple y de alto throughput, filtrado básico, destinos como email/SMS/push.
- EventBridge: enrutamiento basado en reglas con filtrado avanzado, eventos de servicios AWS y SaaS, schedules, archive/replay, transformación de input.
- Para eventos nativos de servicios AWS, EventBridge; para notificaciones a personas o fan-out masivo simple, SNS.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Uso en data engineering

- Alertas de pipelines: Step Functions, Glue, CloudWatch alarms o EventBridge publican en SNS para avisar por email o a un canal.
- DLQ para Lambda, EventBridge o Step Functions, normalmente en SQS.
- Buffer de eventos de S3 hacia consumidores lentos: S3 → SQS → Lambda/ECS.
- Fan-out de un evento de ingesta a varios pipelines (SNS → varias SQS).
- Reintento controlado de registros fallidos para no bloquear un stream.