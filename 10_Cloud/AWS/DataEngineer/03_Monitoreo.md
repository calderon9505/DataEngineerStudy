# CloudWatch

CloudWatch es el servicio de observabilidad de AWS: recoge métricas, logs y trazas de tu infraestructura y aplicaciones, y te permite alertar y visualizar sobre todo eso. Es el lugar donde respondes "¿está funcionando bien?" y "¿qué pasó a las 3 AM?".

## Metrics

Series temporales numéricas. Casi todos los servicios de AWS publican métricas automáticamente y gratis: CPU de EC2, latencia de un ALB, conexiones de RDS, invocaciones de Lambda, longitud de una cola SQS.

Se organizan en namespaces (ej. AWS/EC2) y se filtran por dimensiones (InstanceId, LoadBalancer, etc.).

- **Resolución estándar**: 1 minuto. Las métricas básicas de EC2 son cada 5 minutos salvo que habilites detailed monitoring (de pago).
- **Métricas personalizadas**: las publicas tú con PutMetricData, y pueden ser de alta resolución (hasta 1 segundo).
- **Metric math** te deja combinar métricas (sumas, tasas, promedios ponderados) y **anomaly detection** aprende el patrón normal de una métrica para alertar sobre desviaciones en lugar de umbrales fijos.

> El error más común aquí: el uso de memoria y de disco de una EC2 no son métricas nativas. El hipervisor no ve dentro del sistema operativo. Para tenerlas necesitas instalar el **CloudWatch Agent** en la instancia.

## Logs

Los logs se organizan en log groups (normalmente uno por aplicación o servicio) que contienen log streams (uno por instancia, contenedor o ejecución).

- **Logs Insights**: lenguaje de consulta para buscar y agregar sobre tus logs. Es la herramienta que realmente usas cuando investigas un incidente.
- **Metric filters**: convierten un patrón de los logs en una métrica. Por ejemplo, contar apariciones de ERROR y alertar sobre eso.
- **Subscription filters**: envían logs en streaming a Lambda, Kinesis o OpenSearch para procesamiento o archivado.
- **Live Tail**: ver logs en tiempo real, útil durante un despliegue.
- **Retención**: por defecto es infinita, y esto cuesta dinero. Configúrala explícitamente (30, 90, 365 días) en cada log group.

Ejemplo de Logs Insights:

```log
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50
```

## Alarms

Vigilan una métrica contra un umbral y cambian de estado: OK, ALARM, INSUFFICIENT_DATA.

Las acciones típicas son notificar vía SNS, disparar una política de Auto Scaling, o ejecutar acciones de EC2 (reiniciar, recuperar, terminar). También existen **composite alarms**, que combinan varias alarmas con lógica booleana — muy útiles para reducir el ruido de alertas durante un incidente, cuando veinte alarmas se disparan por la misma causa raíz.

> Detalle importante: define bien el **treat missing data** de la alarma. Una métrica que deja de reportar porque el servicio se murió puede quedarse en INSUFFICIENT_DATA en lugar de alertar, que es exactamente lo contrario de lo que quieres.

Para poner a prueba una alarma `aws cloudwatch set-alarm-state --alarm-name MiAlarma --state-value ALARM --state-reason "Prueba manual"`

## Dashboards

Paneles con widgets de métricas, logs y texto. Soportan dashboards automáticos por servicio y se pueden definir como código (JSON) desde CloudFormation o Terraform.

Las piezas más modernas

- **Application Signals**: APM. Instrumenta tu aplicación (OpenTelemetry) y te da latencia, tasa de error y throughput por servicio, con SLOs y un mapa de dependencias. Es el reemplazo de lo que antes era ServiceLens.
- **Container Insights**: métricas y logs detallados para EKS, ECS y Fargate a nivel de cluster, nodo, pod y contenedor.
- **Lambda Insights**: lo mismo enfocado en funciones serverless, con cold starts y uso de memoria.
- **Synthetics (Canaries)**: scripts que ejecutan periódicamente desde fuera para verificar que tu endpoint o flujo de login responde. Monitoreo sintético.
- **RUM (Real User Monitoring)**: métricas de rendimiento desde el navegador de usuarios reales.
- **Cross-account observability**: ver métricas y logs de varias cuentas desde una cuenta monitora central. Imprescindible en organizaciones multi-cuenta.
- **Metric Streams**: exportar métricas en near real-time a S3 o a herramientas de terceros (Datadog, Grafana).

Dos aclaraciones de nomenclatura

> CloudWatch Events ya no existe con ese nombre: es EventBridge, un servicio aparte para enrutar eventos y programar tareas con cron. Si ves documentación hablando de CloudWatch Events, está desactualizada.

> CloudWatch no es CloudTrail. CloudWatch monitorea rendimiento y salud; CloudTrail audita quién hizo qué llamada a la API. Son complementarios y se suelen integrar (CloudTrail puede enviar sus logs a CloudWatch Logs para alertar sobre acciones sospechosas).

## Costos

CloudWatch es uno de los servicios que más sorprende en la factura. Los tres culpables habituales:

1. Ingesta de logs. Se cobra por GB ingerido, y es la partida más grande en la mayoría de cuentas. Logs de debug en producción son caros.
2. Retención infinita por no configurarla.
3. Métricas personalizadas con alta cardinalidad. Cada combinación única de dimensiones es una métrica facturable. Poner un user_id o un request_id como dimensión genera miles de métricas y una factura considerable.

## CloudWatch Agent (amazon-cloudwatch-agent)

Software que se instala dentro de una EC2 (o servidor on-premises) para enviar a CloudWatch lo que AWS no ve desde fuera.

Qué resuelve:

- **Logs**: archivos del sistema operativo y de la aplicación (/var/log/*, nginx, logs propios). **Sin el agente, EC2 no envía ningún log**.
- **Métricas internas**: memoria, espacio en disco, procesos. El hipervisor no ve dentro del SO, así que estas métricas no existen por defecto.

Requisitos para que funcione:

1. Rol IAM en la instancia con CloudWatchAgentServerPolicy.
2. Agente instalado (dnf install amazon-cloudwatch-agent o SSM Distributor).
3. Configuración en JSON: qué archivos leer, a qué log group, con qué retención.
4. Arrancarlo con `amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s`.

### Cositas a saber:

- "**Agente unificado**" es el mismo agente. Se llama así porque reemplazó dos herramientas antiguas (awslogs para logs + scripts Perl para métricas). El viejo awslogs está deprecado.
- **Convención**: un log group por aplicación, un log stream por instancia ({instance_id}).
- **Define siempre retention_in_days**; por defecto la retención es infinita y se paga.
- Las métricas de memoria y disco son métricas personalizadas, y esas sí se facturan.
- En contenedores (EKS/ECS) no se usa este agente, sino Fluent Bit.


---
---

# EventBridge

EventBridge es el bus de eventos serverless de AWS. Su trabajo es enrutar eventos: algo pasa en algún lugar, y EventBridge decide quién debe enterarse y lo invoca. Es la pieza que conecta servicios sin que se conozcan entre sí.

* **Event bus**: el canal por donde pasan los eventos.

    - **default**: aquí llegan automáticamente y gratis los eventos de los servicios de AWS.
    - **Custom Buses**: para los eventos de tus propias aplicaciones.
    - **Partner buses**: para SaaS externos (Datadog, Zendesk, Shopify, MongoDB).

* **Rule**: la regla que decide qué hacer. Tiene dos modalidades, y es importante no confundirlas:

    - **Event pattern**: coincide con la estructura del evento (reactivo).
    - **Schedule**: se ejecuta por cron o rate (programado).

* **Target**: a quién se invoca. Más de 30 destinos — Lambda, Step Functions, SQS, SNS, Kinesis, Firehose, ECS, Batch, SSM, SageMaker pipelines, y API destinations para webhooks HTTP externos.

Ejemplo de event pattern:
```json
{
    "source": ["aws.glue"],
    "detail-type": ["Glue Job State Change"],
    "detail": {
        "state": ["FAILED", "TIMEOUT"]
    }
}
```

Esa regla captura cualquier job de Glue que falle y puede disparar una notificación o un flujo de remediación. Fíjate que el filtrado ocurre antes de invocar el target: no pagas ni ejecutas nada por los eventos que no coinciden.

## EventBridge for data engineering

* **EventBridge Scheduler** (distinto de las rules con schedule). Es un servicio dedicado a programación a escala: millones de schedules, soporte de zonas horarias con horario de verano, schedules de una sola vez, ventanas de tiempo flexibles para distribuir carga. Para disparar un pipeline diario, hoy la recomendación es Scheduler, no una rule.

* **EventBridge Pipes**. Conexión punto a punto entre un origen y un destino, con filtrado y enriquecimiento opcional en medio:

    origen → filtro → enriquecimiento → destino

    Los orígenes son precisamente los de streaming: DynamoDB Streams, Kinesis Data Streams, SQS, MSK, Amazon MQ, Kafka autogestionado. El enriquecimiento puede ser una Lambda, Step Functions o una API. Pipes te ahorra escribir el Lambda de pegamento que antes hacía esto.

* **S3 Event Notifications vía EventBridge**. Históricamente S3 notificaba directo a Lambda/SNS/SQS, con una limitación fuerte: un solo destino por prefijo y filtrado pobre. Activando EventBridge en el bucket, los eventos de S3 entran al bus y obtienes filtrado rico (por tamaño, por tags, por patrón complejo de clave) y múltiples destinos para el mismo evento. Es el mecanismo moderno para disparar un pipeline cuando llega un archivo nuevo a tu data lake.

* **Archive y Replay**. Puedes archivar eventos de un bus y reproducirlos después. En data engineering esto vale para reprocesar: si tu pipeline tuvo un bug tres días, reproduces los eventos de esa ventana.

* **Entrega fiable**: política de reintentos configurable (hasta 24 horas) y dead-letter queue en SQS para los eventos que nunca se pudieron entregar. Si te preguntan cómo garantizar que no se pierda un evento ante un fallo del target, la respuesta es DLQ.

* **resource-based policy**: Se crean políticas basadas en recursos para permitir que otras cuentas puedan poner eventos en el bus de EventBridge.

Límites que conviene saber

- **Tamaño de evento: 256 KB**. EventBridge no transporta datos, transporta avisos. Si necesitas mover un archivo, el evento lleva la referencia a S3, no el contenido.
- **Entrega at-least-once y sin orden garantizado**. Tus targets deben ser idempotentes. Si necesitas orden, es Kinesis con partition key o SQS FIFO.
- **No es para alto throughput de datos**. Técnicamente escala a miles de eventos por segundo, pero el modelo de precios (~$1 por millón de eventos personalizados) lo hace absurdo para volúmenes de streaming. Los eventos de servicios AWS en el bus default son gratis.

## Schema Registry de EventBridge

es un catálogo que guarda la estructura de tus eventos: qué campos tiene cada tipo de evento, de qué tipo son y cuáles son obligatorios. Los almacena en formato OpenAPI 3 o JSON Schema.

Tiene tres partes:

* **Registries**. Los contenedores de schemas.

    - **aws.events**: viene precargado con los schemas de todos los eventos de servicios AWS. Puedes consultar exactamente qué campos trae un "Glue Job State Change" sin tener que provocar uno y mirar el JSON.
    - **discovered-schemas**: se llena automáticamente.
    - Registries propios para tus eventos.

* **Schema discovery**. Lo activas en un bus y EventBridge infiere los schemas de los eventos que van pasando, automáticamente. Útil cuando heredas un sistema y no sabes qué eventos circulan.

* **Code bindings**. La parte realmente práctica: a partir de un schema, EventBridge te genera clases tipadas para Java, Python, TypeScript o Go. En lugar de escribir `event["detail"]["jobName"]` y descubrir el typo en runtime, trabajas con un objeto con autocompletado y validación en tiempo de compilación. Se descarga desde la consola, la CLI o plugins de IDE.

Los schemas también se versionan, lo que te permite seguir la evolución de un evento cuando le añaden campos.

---
---

# X-Ray

X-Ray es el servicio de trazabilidad distribuida de AWS. Responde una pregunta que ni las métricas ni los logs resuelven bien: esta petición concreta tardó 4 segundos — ¿en qué servicios se fueron?

En una arquitectura distribuida, una petición atraviesa `API Gateway → Lambda → DynamoDB → otra Lambda → SQS`. Las métricas te dicen que la latencia subió. Los logs te dan fragmentos sueltos en cinco log groups distintos. Ninguno te reconstruye el recorrido completo de una petición.

X-Ray inyecta un `trace ID` en la petición (header X-Amzn-Trace-Id) que se propaga por todos los servicios. Al final tienes la cronología completa con el tiempo consumido en cada salto.

Conceptos

* **Segment**: el trabajo que hizo un servicio. Un segmento por servicio atravesado.

* **Subsegment**: granularidad dentro de un segmento — una query a la base de datos, una llamada HTTP externa, un bloque de código que instrumentaste manualmente.

* **Trace**: el conjunto de todos los segmentos que comparten el mismo `trace ID`. Una petición completa.

* **Service map (o trace map)**: el grafo visual de tus servicios con latencia, tasa de error y throughput en cada nodo y arista. Es la vista que usas primero: de un vistazo ves qué nodo está rojo.

* **Sampling rules**: X-Ray no traza todo. Por defecto captura 1 petición por segundo más un 5% del resto. Es configurable, y es el mecanismo de control de costos — trazar el 100% de un servicio de alto tráfico es caro e innecesario.

* **Annotations vs metadata**: ambas son datos que adjuntas a una traza, pero las annotations están indexadas (puedes filtrar y buscar por ellas) y las metadata no (solo se visualizan). Es exactamente la misma lógica que las dimensiones de CloudWatch frente a los campos de un log: lo indexado debe ser de cardinalidad baja y enumerable; los identificadores únicos van en metadata.

* **Errors, Faults, Throttles**: X-Ray los distingue. Error = 4xx (culpa del cliente), Fault = 5xx (culpa del servidor), Throttle = 429. Saber la diferencia es una pregunta típica.

Cómo se instrumenta

| Entorno          | Cómo                                                  |
|------------------|-------------------------------------------------------|
| Lambda           | Activar Active Tracing en la configuración. Nada más. |
| EC2              | Instalar el X-Ray daemon (o el ADOT Collector)        |
| ECS/EKS          | Daemon como sidecar o DaemonSet                       |
| API Gateway, ELB | Activar tracing en la consola                         |


Para el código, o usas el X-Ray SDK, o — la recomendación actual — OpenTelemetry vía ADOT (AWS Distro for
OpenTelemetry), que es vendor-neutral y te permite enviar las mismas trazas a X-Ray o a otra herramienta.

Lo que sí aplica a tu examen

X-Ray no instrumenta Glue, EMR, Redshift ni Athena. Esos se depuran con CloudWatch Logs, métricas de job y la Spark UI / Spark History Server en el caso de Glue y EMR. Si una pregunta te plantea "un job de Glue va lento, cómo diagnosticas", la respuesta no es X-Ray.

Donde sí toca data engineering:

- **Step Functions** soporta X-Ray tracing. Si orquestas un pipeline con una state machine y quieres ver dónde se acumula el tiempo entre pasos, es la herramienta.
- **Pipelines de ingesta por API**: API Gateway → Lambda → Kinesis/Firehose. Ahí sí hay una cadena de peticiones que trazar.
- Lambdas de transformación dentro de Firehose o como glue code entre servicios.

Para Glue y EMR, la contraparte conceptual que el examen sí pregunta son las Spark UI y los job metrics de Glue, más Glue Job Observability.

---
---

# CloudTrail

CloudTrail es el servicio de auditoría de AWS. Registra cada llamada a la API de tu cuenta: quién la hizo, qué acción, sobre qué recurso, cuándo, desde qué IP, con qué credenciales, y si tuvo éxito o falló.

Está activo desde el primer día sin que lo configures, pero con limitaciones importantes que conviene entender.

### tipos de evento

* **Management events** (plano de control). Operaciones sobre la estructura de tus recursos: `CreateBucket`, `RunInstances`, `CreateCrawler`, `AttachRolePolicy`. Se registran por defecto y gratis en la primera copia.

* **Data events** (plano de datos). Operaciones sobre el contenido: `s3:GetObject`, `s3:PutObject`, `dynamodb:GetItem`, `lambda:Invoke`. No están activados por defecto y se cobran por evento. La razón es el volumen: un data lake puede generar millones de GetObject al día.

* **Insights events**. Detección automática de patrones anómalos de actividad de API — un pico inusual de borrados, por ejemplo. Se activa aparte y tiene costo.

* **Network activity events**. Actividad a través de VPC endpoints, útil para investigar exfiltración.

### Formas de acceder a los datos:
|                 | Alcance                                          | Retención          | Costo                  |
|-----------------|--------------------------------------------------|--------------------|------------------------|
| Event history   | Solo management events, una región               | 90 días            | Gratis                 |
| Trail           | Management + data events, multi-región, multi-cuenta | Indefinida (en S3) | Almacenamiento S3      |
| CloudTrail Lake | Igual + fuentes externas                         | Hasta 10 años      | Por ingesta y consulta |

* **Event history**: es lo que ves en la consola sin configurar nada. Si alguien borró algo hace cuatro meses, ahí ya no está.

* **Trail**: Entrega los eventos como archivos JSON comprimidos a un bucket de S3, donde los conservas el tiempo que quieras. Puedes crearlo como organization trail para capturar todas las cuentas de la organización en un bucket central — el patrón estándar en empresas.

* **CloudTrail Lake**: Es el enfoque gestionado. Almacena los eventos en un lago propio y los consultas con SQL directamente, sin montar tablas de Athena ni particiones. Cuesta más pero elimina trabajo de plomería.

### Formas de consumir el servicio

* **Consulta histórica (forense)**: los archivos en S3 con Athena. La propia consola de CloudTrail te genera la tabla. Es una tarea muy de data engineering: particionar por fecha, convertir a Parquet si el volumen lo justifica, y consultar.

* **Alertas reactivas**: enviar el trail a CloudWatch Logs y poner metric filters + alarmas. El ejemplo clásico es alertar cuando alguien modifica una policy de IAM o desactiva el propio CloudTrail.

* **Automatización**: los eventos de CloudTrail llegan a EventBridge, así que puedes disparar una Lambda de remediación automática ante una acción concreta.

### Garantías de integridad

Para compliance, dos características:

- **Log file validation**: CloudTrail genera archivos digest con hashes SHA-256 de los logs, firmados. Permite demostrar que nadie alteró ni borró registros.
- Cifrado con SSE-KMS y bucket policy restrictiva sobre el bucket de destino.

Y un patrón que se pregunta: el bucket de CloudTrail debe tener S3 Object Lock o al menos versionado y MFA Delete si necesitas inmutabilidad real.

### Comparativa con S3 Server Access Logs 

S3 Server Access Logs es una característica que activas por bucket: S3 escribe un registro de texto por cada petición que recibe ese bucket, y los entrega como archivos a otro bucket que tú designas.

|             | CloudTrail Data Events          | S3 Server Access Logs                       |
|-------------|---------------------------------|---------------------------------------------|
| Fiabilidad  | Garantizada                     | Best-effort (puede perder registros)        |
| Latencia    | ~5-15 min                       | Horas                                       |
| Filtrado    | Por prefijo, por bucket         | Todo o nada                                 |
| Integración | EventBridge, CloudWatch, Athena | Solo archivos en S3                         |
| Costo       | Por evento (caro a escala)      | Solo almacenamiento                         |
| Campos      | Identidad IAM detallada         | Más campos HTTP (turn-around time, referer) |

Si la pregunta enfatiza auditoría fiable, near-real-time, o reaccionar automáticamente, es CloudTrail data events. Si enfatiza costo bajo y análisis de patrones de acceso a gran volumen, son server access logs. Nota además que CloudTrail te permite filtrar data events por prefijo — así registras solo la zona curated/ de tu lake y no el raw/ entero, que es la forma de controlar el costo.

Otros puntos que tocan tu examen:

- Lake Formation registra sus decisiones de acceso en CloudTrail. Es como demuestras que los permisos a nivel de
columna se aplicaron.
- Consultas de Athena, ejecuciones de Glue jobs, accesos a Redshift y operaciones de KMS (Decrypt, GenerateDataKey) todas quedan en CloudTrail. Esto último es la razón por la que SSE-KMS se exige en entornos regulados y SSE-S3 no basta: con KMS tienes rastro auditable de cada descifrado. (SSE = Server-Side Encryption: con SSE-KMS S3 cifra el objeto al escribirlo y lo descifra al leerlo, de forma transparente. con SSE-KMS la clave la gestiona KMS.)
- Los eventos de servicios globales (IAM, STS, CloudFront, Route 53) se registran en us-east-1.