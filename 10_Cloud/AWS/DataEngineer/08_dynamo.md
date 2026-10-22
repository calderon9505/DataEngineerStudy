# Amazon DynamoDB

DynamoDB es la base de datos NoSQL serverless de AWS, de tipo key-value y document. Es totalmente managed, escala horizontalmente de forma masiva y ofrece latencia de milisegundos de un solo dígito (single-digit ms) a cualquier escala.

### Características fundamentales

- **Serverless**: no provisionas servidores; AWS gestiona todo. No hay instancias que administrar.
- **Escala horizontal automática**: maneja millones de requests por segundo particionando los datos por detrás.
- **Latencia consistente**: single-digit ms, incluso con petabytes de datos.
- **Totalmente managed**: replicación, patching, scaling automáticos.
- **Alta disponibilidad**: replica automáticamente en 3 AZs dentro de la región.
- Ideal para OLTP a gran escala, no para analytics (OLAP).

### Estructura de datos (vocabulario clave)

| Concepto  | Equivalente | Qué es                                     |
| --------- | ----------- | ------------------------------------------ |
| Table     | Tabla       | Colección de items                         |
| Item      | Fila        | Un registro (hasta 400 KB)                 |
| Attribute | Columna     | Un campo del item (pero flexible, no fijo) |

> A diferencia de SQL, solo las keys son obligatorias; cada item puede tener atributos distintos (schema flexible).

### primary keys

DynamoDB tiene dos tipos de primary key:

1. Partition Key (simple primary key)
    - Una sola key (también llamada hash key).
    - DynamoDB aplica una función hash sobre ella para decidir en qué partición física se guarda el item.
    - Debe ser única por item.

2. Partition Key + Sort Key (composite primary key)
    - Combinación de partition key (hash key) + sort key (range key).
    - Varios items pueden compartir la misma partition key, pero deben diferir en la sort key.
    - Permite consultar rangos y ordenar dentro de una partición (ej. "todos los pedidos del cliente 42 ordenados por fecha").


### diseño según access patterns

- En DynamoDB modelas la tabla según tus patrones de acceso (access patterns) conocidos de antemano , NO según las entidades (al revés que en SQL). Es decir:
    - SQL: guardas los datos organizados por lo que son (entidades en tablas separadas) y decides después cómo consultarlos (JOINs flexibles, ad-hoc).
    - DynamoDB: decides primero cómo vas a consultar (access patterns) y organizas los datos para servir exactamente esas consultas rápido. Antes de crear la tabla, tienes que listar todas las preguntas que tu aplicación le hará a la base, y diseñar la tabla para responder exactamente esas preguntas. En DynamoDB es común meter varias entidades en una sola tabla (single-table design), estructurando las keys para que esas consultas sean directas
- No sirve para queries ad-hoc. Si no diseñaste la tabla para una consulta, será ineficiente o imposible.
- La partition key debe tener alta cardinalidad y distribuir bien la carga → si eliges mal, generas una hot partition (una partición sobrecargada) que degrada el performance.

La consecuencia importante:

- En SQL, si surge una pregunta nueva que no previste → escribes un nuevo JOIN y listo. **Flexible**.
- En DynamoDB, si surge un access pattern que no previste al diseñar la tabla → puede que la tabla no pueda responderlo eficientemente. Tendrías que crear un GSI (índice secundario, que da "otra forma de ver" los datos) o incluso rediseñar la tabla. **Rígido**, pero rapidísimo para lo que sí previste.

### Query vs Scan

| Operación | Qué hace                                                      | Eficiencia                                   |
| --------- | ------------------------------------------------------------- | -------------------------------------------- |
| Query     | Busca por partition key (y opcionalmente filtra por sort key) | ✅ Eficiente — accede directo a la partición |
| Scan      | Lee toda la tabla y filtra después                            | ❌ Ineficiente y caro — evítalo              |

> siempre prefiere Query sobre Scan. Si te ves obligado a hacer Scan frecuentemente, el diseño de la tabla está mal (o necesitas un índice).

### Secondary Indexes (índices secundarios)

Permiten consultar por otros atributos que no son la primary key

|                | GSI                  | LSI                     |
| -------------- | -------------------- | ----------------------- |
| Partition key  | Diferente a la tabla | Igual a la tabla        |
| Sort key       | Diferente            | Diferente               |
| ¿Cuándo crear? | Cualquier momento    | Solo al crear la tabla  |
| Capacidad      | Propia               | Compartida con la tabla |
| Consistencia   | Solo eventual        | Fuerte posible          |


- Global Secondary Index (GSI)
    - Define una partition key y sort key totalmente distintas a las de la tabla base.
    - Se puede crear/eliminar en cualquier momento.
    - Tiene su propia capacidad (throughput) provisionada aparte.
    - Es el más flexible y usado. Replicación asíncrona → eventualmente consistente.

- Local Secondary Index (LSI)
    - Usa la misma partition key que la tabla, pero distinta sort key.
    - Debe crearse al crear la tabla (no se puede añadir después).
    - Comparte la capacidad de la tabla base. Soporta consistencia fuerte.


### Capacity Modes

- On-Demand
    - No provisionas nada; pagas por request.
    - Escala automáticamente e instantáneamente.
    - Ideal para cargas impredecibles, variables o nuevas (no sabes el tráfico).
    - Más caro por request, pero sin desperdicio.

- Provisioned
    - Defines RCUs (Read Capacity Units) y WCUs (Write Capacity Units) por adelantado.
    - Más barato si el tráfico es predecible y constante.
    - Puedes añadir Auto Scaling para ajustar dentro de rangos.


### Consistencia de lectura

- Eventually Consistent (default): puede devolver datos ligeramente desactualizados; más barato (0.5 RCU).
- Strongly Consistent: siempre el dato más reciente; cuesta el doble (1 RCU) y no funciona sobre GSI.


### DynamoDB Accelerator (DAX)

- Cache en memoria totalmente managed, específico para DynamoDB.
- Reduce latencia de ms a microsegundos para lecturas.
- Ideal para cargas read-heavy con lecturas repetidas.
- Es write-through: transparente, no cambias el código casi.


### DynamoDB Streams ⭐

- Streams captura un registro ordenado de los cambios (INSERT/MODIFY/REMOVE) en la tabla → Change Data Capture (CDC).
- Se conserva 24 horas.
- permite reaccionar a cambios en tiempo real
- Caso de uso estrella: DynamoDB Streams → Lambda para procesar cambios en tiempo real (event-driven).
- Permite replicar cambios, actualizar agregados, alimentar pipelines, etc.

> También existe Kinesis Data Streams for DynamoDB como alternativa para enviar los cambios a Kinesis con retención más larga y más consumidores.

### Global Tables

- Replicación multi-región, active-active (escribes y lees en cualquier región).
- Replicación asíncrona, eventualmente consistente entre regiones.
- Casos: baja latencia global y DR cross-region.
- Requiere Streams habilitado.

### TTL (Time To Live)

- Borra automáticamente items expirados según un atributo timestamp.
- Gratis, ideal para datos temporales (sesiones, cache, logs).

### Backups y recuperación

- PITR (Point-in-Time Recovery): restaura a cualquier segundo de los últimos 35 días.
- On-demand backups: snapshots manuales que persisten.

## Seguridad

- Encryption at rest por defecto (KMS).
- Control de acceso con IAM, incluso a nivel de item/atributo con fine-grained access control (condiciones IAM sobre dynamodb:LeadingKeys).
- VPC endpoints para acceso privado.

### Integración con analytics (data engineering)

Como DynamoDB es OLTP y no sirve para analytics, el examen pregunta cómo llevar sus datos a analytics:

- **Export to S3**: exportar tablas a S3 (formato DynamoDB JSON / Ion) sin consumir capacidad → luego Athena/Glue. Usa PITR por detrás.
- **Zero-ETL to Redshift / OpenSearch**: integración para analytics casi en tiempo real sin pipeline.
- DynamoDB Streams → Kinesis → analytics.
- Glue puede leer DynamoDB como fuente.
