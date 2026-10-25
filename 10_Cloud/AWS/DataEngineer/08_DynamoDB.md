# Amazon DynamoDB

DynamoDB es la base de datos NoSQL serverless de AWS, de tipo key-value y document. Es totalmente managed, escala horizontalmente de forma masiva y ofrece latencia de milisegundos de un solo dígito (single-digit ms) a cualquier escala.

## Características fundamentales

- **Serverless**: no provisionas servidores; AWS gestiona todo. No hay instancias que administrar.
- **Escala horizontal automática**: maneja millones de requests por segundo particionando los datos por detrás.
- **Latencia consistente**: single-digit ms, incluso con petabytes de datos.
- **Totalmente managed**: replicación, patching, scaling automáticos.
- **Alta disponibilidad**: replica automáticamente en 3 AZs dentro de la región.
- Ideal para OLTP a gran escala, no para analytics (OLAP).

## Estructura de datos (vocabulario clave)

| Concepto  | Equivalente | Qué es                                     |
| --------- | ----------- | ------------------------------------------ |
| Table     | Tabla       | Colección de items                         |
| Item      | Fila        | Un registro (hasta 400 KB)                 |
| Attribute | Columna     | Un campo del item (pero flexible, no fijo) |

> A diferencia de SQL, solo las keys son obligatorias; cada item puede tener atributos distintos (schema flexible).

## primary keys

DynamoDB tiene dos tipos de primary key:

1. Partition Key (simple primary key)
    - Una sola key (también llamada hash key).
    - DynamoDB aplica una función hash sobre ella para decidir en qué partición física se guarda el item.
    - Debe ser única por item.

2. Partition Key + Sort Key (composite primary key)
    - Combinación de partition key (hash key) + sort key (range key).
    - Varios items pueden compartir la misma partition key, pero deben diferir en la sort key.
    - Permite consultar rangos y ordenar dentro de una partición (ej. "todos los pedidos del cliente 42 ordenados por fecha").


## diseño según access patterns

- En DynamoDB modelas la tabla según tus patrones de acceso (access patterns) conocidos de antemano , NO según las entidades (al revés que en SQL). Es decir:
    - SQL: guardas los datos organizados por lo que son (entidades en tablas separadas) y decides después cómo consultarlos (JOINs flexibles, ad-hoc).
    - DynamoDB: decides primero cómo vas a consultar (access patterns) y organizas los datos para servir exactamente esas consultas rápido. Antes de crear la tabla, tienes que listar todas las preguntas que tu aplicación le hará a la base, y diseñar la tabla para responder exactamente esas preguntas. En DynamoDB es común meter varias entidades en una sola tabla (single-table design), estructurando las keys para que esas consultas sean directas
- No sirve para queries ad-hoc. Si no diseñaste la tabla para una consulta, será ineficiente o imposible.
- La partition key debe tener alta cardinalidad y distribuir bien la carga → si eliges mal, generas una hot partition (una partición sobrecargada) que degrada el performance.

La consecuencia importante:

- En SQL, si surge una pregunta nueva que no previste → escribes un nuevo JOIN y listo. **Flexible**.
- En DynamoDB, si surge un access pattern que no previste al diseñar la tabla → puede que la tabla no pueda responderlo eficientemente. Tendrías que crear un GSI (índice secundario, que da "otra forma de ver" los datos) o incluso rediseñar la tabla. **Rígido**, pero rapidísimo para lo que sí previste.

## GetItem

GetItem es la operación que recupera un solo item de una tabla, buscándolo por su primary key completa.

- Debes proporcionar la primary key exacta (la partition key, y la sort key si la tabla es composite). No sirve para buscar por otros atributos ni por rangos.
- Devuelve un único item (o nada si no existe).
- Es la lectura más eficiente posible: acceso directo por key.
- Por defecto es eventually consistent; puedes pedir strongly consistent con `ConsistentRead=true`.
- Admite ProjectionExpression para traer solo ciertos atributos.

> Operación relacionada: BatchGetItem recupera varios items (hasta 100) por sus keys en una sola llamada.

## Query vs Scan

|                      | Query                                         | Scan                          |
| -------------------- | --------------------------------------------- | ----------------------------- |
| Qué lee              | Solo los items de la `partition key` indicada | Toda la tabla/índice          |
| Cómo accede          | Directo a la partición (hash)                 | Recorre todas las particiones |
| Eficiencia           | Alta                                          | Baja (lee todo)            |
| Costo (RCU)          | Proporcional a lo que coincide con la key     | Proporcional a toda la tabla  |
| Requiere             | partition key                                 | Nada (lee todo)               |
| Performance a escala | Constante                                     | Se degrada al crecer la tabla |

> siempre prefiere Query sobre Scan. Si te ves obligado a hacer Scan frecuentemente, el diseño de la tabla está mal (o necesitas un índice).

### Query

Query recupera items basándose en la partition key (obligatoria) y, opcionalmente, una condición sobre la sort key.

Cómo funciona por dentro:
- DynamoDB usa la partition key para ir directamente a la partición donde están los datos (vía la función hash). No recorre nada más.
- Dentro de esa partición, los items están ordenados por sort key, así que puede filtrar rangos eficientemente.

Lo que puedes hacer con Query:
- `PK = valor` (obligatorio, debe ser **igualdad exacta** sobre la partition key).
- Sobre la sort key: =, <, >, between, begins_with, etc. (condiciones de rango).
- Ordenar resultados (ascendente/descendente) con ScanIndexForward.
- Limitar resultados.

Lo que NO puedes:
- Buscar por un atributo que no sea la key (para eso necesitas un GSI/LSI).
- Usar condiciones distintas de *igualdad* sobre la partition key.

### Scan

Scan lee TODOS los items de toda la tabla (o índice) y después aplica los filtros.

Es decir, Scan recorre todas las particiones y lee cada uno de los items.

### FilterExpression

Tanto Query como en Scan, el `FilterExpression` se aplica después de leer los datos, por tanto, NO ahorra capacidad.

- El filtro reduce lo que te devuelve, pero NO reduce la capacidad consumida (RCU/RRU).
- Pagas por todo lo leído, no por lo que recibes.
- Por eso un Scan con filtro es caro: lees toda la tabla aunque el filtro deje solo 3 items.

> Lo que sí reduce la capacidad es la `KeyConditionExpression` de un Query (que determina qué se lee), no el FilterExpression.

### ProjectionExpression

Un `ProjectionExpression` sirve para traer solo los atributos que te interesan de un item, en lugar del item completo. Es el equivalente a elegir columnas específicas en SQL.

Cuando haces un `GetItem`, Query o Scan, por defecto DynamoDB te devuelve el item completo (todos sus atributos). Con ProjectionExpression especificas cuáles atributos quieres que te devuelva. Es útil para reducir el tamaño de la respuesta (menos datos por la red, menos payload en tu app), sobre todo si los items tienen muchos atributos o atributos grandes y solo necesitas unos pocos.

⚠️ PERO, NO ahorra capacidad, lo que ahorra es transferencia de datos y payload de respuesta, no capacidad de lectura.

| Expression               | Qué controla                                | ¿Reduce capacidad (RCU)?     |
| ------------------------ | ------------------------------------------- | ---------------------------- |
| `KeyConditionExpression` | Qué items se leen (por key) — solo en Query | ✅ Sí (determina qué se lee) |
| `FilterExpression`       | Descarta items después de leer              | ❌ No                        |
| `ProjectionExpression`   | Qué atributos devolver de cada item         | ❌ No                        |


### Performance / paginación

Tanto Query como en Scan devuelven máximo 1 MB de datos por llamada. Si hay más, DynamoDB devuelve un LastEvaluatedKey y debes paginar (hacer más llamadas).

### Parallel Scan (cuando el Scan es inevitable)

Si tienes que hacer un Scan completo (ej. una migración o exportación puntual), puedes acelerarlo con Parallel Scan:
- Divide la tabla en segmentos y los escanea en paralelo con múltiples workers.
- Acelera el tiempo total, pero consume aún más capacidad a la vez → cuidado con el throttling del tráfico de producción.

> Si te encuentras necesitando Scans frecuentes, la respuesta casi siempre es rediseñar el acceso

## Secondary Indexes (índices secundarios)

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


## Capacity Modes

- On-Demand
    - No provisionas nada; Es un modelo pay-per-request.
        - RRU (Read Request Unit) = una unidad de lectura consumida
        - WRU (Write Request Unit) = una unidad de escritura consumida.
    - Escala automáticamente e instantáneamente.
    - Ideal para cargas impredecibles, variables o nuevas (no sabes el tráfico).
    - Más caro por request, pero sin desperdicio.


- Provisioned (default)
    - Defines RCUs (Read Capacity Units) y WCUs (Write Capacity Units) por adelantado. Son capacidades por segundo.
    - Más barato si el tráfico es predecible y constante.
    - Puedes añadir Auto Scaling para ajustar dentro de rangos.
    - Burst capacity: Mecanismo para manejar picos cortos de tráfico sin que te rechacen las requests, aprovechando capacidad que no usaste antes.
        - DynamoDB acumula la capacidad no usada de los últimos 300 segundos (5 minutos)
        - Cuando llega un spike repentino que supera tu capacidad provisionada, DynamoDB usa esa reserva acumulada (el "burst") para absorber el pico en lugar de hacer throttling (rechazar requests).

## Reglas de lectura (RCU = RRU)

Basado en items de hasta 4 KB:
- 1 unidad de lectura = 1 lectura strongly consistent de un item de hasta 4 KB.
- 1 unidad = 2 lecturas eventually consistent de hasta 4 KB (la mitad de costo)
- 2 unidad = 1 lectura transaccional
- Items más grandes de 4 KB → redondean hacia arriba (ej. un item de 6 KB necesita 2 unidades).

## Reglas de escritura (WCU = WRU)

Basado en items de hasta 1 KB:
- 1 unidad de escritura = 1 escritura de un item de hasta 1 KB.
- Items más grandes → redondean hacia arriba (ej. 3 KB = 3 unidades).
- Escritura transaccional cuesta 2 unidades.


## Consistencia de lectura

- Eventually Consistent (default): puede devolver datos ligeramente desactualizados; más barato (0.5 RCU).
- Strongly Consistent: siempre el dato más reciente; cuesta el doble (1 RCU) y no funciona sobre GSI.

## ConditionExpression

Hasta ahora las expressions que vimos eran de lectura/respuesta. Un `ConditionExpression` permite que una operación de escritura (PutItem, UpdateItem, DeleteItem) se ejecute solo si se cumple una condición. Si la condición es falsa, la escritura falla y no se aplica.

```
UpdateItem CLIENTE#42
    SET saldo = 100
    ConditionExpression: "attribute_exists(PK)"
```

Si la condición no se cumple → DynamoDB lanza `ConditionalCheckFailedException` y la operación no modifica nada.

> A tener en cuenta: Una escritura condicional consume capacidad de escritura (WCU/WRU) AUNQUE la condición falle y no se modifique nada. Esto tiene sentido, DynamoDB tuvo que leer y evaluar el item para comprobar la condición.

## DynamoDB Transactions

Operaciones que DynamoDB ejecuta con garantías ACID, aplicadas a NoSQL.

DynamoDB normalmente trabaja operación por operación. Pero a veces necesitas que varias operaciones se ejecuten como un todo: o todas tienen éxito, o ninguna se aplica (all-or-nothing). Para eso existen las transacciones, con dos APIs:

- `TransactWriteItems` → escrituras transaccionales (hasta 100 items, en una o varias tablas).
- `TransactGetItems` → lecturas transaccionales.

Una lectura transaccional te entrega una vista consistente y aislada de múltiples items a la vez, como si fueran una sola operación atómica.

El valor está en leer varios items juntos con la garantía de que:
- Obtienes un snapshot coherente de todos ellos en el mismo instante.
- Ninguna otra transacción está modificándolos a medias mientras los lees, es decir, no ves un estado "intermedio" de una escritura que está ocurriendo en paralelo.

## Optimistic Locking

Estrategia para manejar concurrencia cuando varios procesos intentan modificar el mismo dato al mismo tiempo (pero sin usar el tradicional Pessimistic Locking)

Imagina dos procesos que leen el mismo item y lo actualizan casi a la vez:
```
Proceso A lee stock = 10
Proceso B lee stock = 10
Proceso A vende 1 → escribe stock = 9
Proceso B vende 1 → escribe stock = 9   ❌ (debería ser 8)
```
Se perdió una actualización (lost update): ambos leyeron 10 y uno pisó el cambio del otro. El stock real debería ser 8, pero quedó en 9. Esto es lo que
las estrategias de concurrencia evitan.

### Pessimistic Locking

"Asumo que habrá conflictos, así que bloqueo el dato antes de tocarlo."

- El proceso bloquea el registro (lock) → nadie más puede tocarlo hasta que termine.
- Es lo que hacen las bases relacionales con locks (SELECT ... FOR UPDATE)
- Garantiza que no hay conflictos, pero penaliza el rendimiento y la concurrencia: otros esperan, puede haber deadlocks.
- Bueno cuando los conflictos son frecuentes.

### Optimistic Locking

"Asumo que los conflictos son raros, así que no bloqueo nada; solo verifico al final que nadie cambió el dato mientras yo trabajaba."

- No bloquea el dato → todos pueden leer libremente.
- Al momento de escribir, comprueba si el dato cambió desde que lo leíste.
- Si no cambió → escribe. Si cambió → falla y reintentas.
- Mejor rendimiento y concurrencia (nadie espera), pero requiere manejar reintentos.
- Bueno cuando los conflictos son poco frecuentes

El mecanismo clásico usa un version number (o un timestamp) en cada item:
```
1. Leo el item:           producto#10, stock=10, version=5
2. Calculo mi cambio:     stock=9
3. Escribo CON condición: actualiza a stock=9, version=6 SOLO SI version sigue siendo 5
4a. Si version aún = 5 → éxito, ahora version=6 ✅
4b. Si otro ya escribió (version=6) → mi condición falla ❌ → releo y reintento
```

En DynamoDB esto se implementa con el `ConditionExpression`, si la condición falla → `ConditionalCheckFailedException` → relees y reintentas (idealmente con exponential backoff):

```sql
UpdateItem producto#10
    SET stock = 9, version = 6
    ConditionExpression: "version = 5"
```

> DynamoDB es optimista por naturaleza — no tiene locks pesados. Por eso el optimistic locking es el patrón de concurrencia en DynamoDB.

> Las transacciones de DynamoDB (TransactWriteItems) también usan este enfoque optimista por debajo.


## DynamoDB Accelerator (DAX)

- Cache en memoria fully managed, específico para DynamoDB.
- Reduce latencia de ms a microsegundos para lecturas.
- Ideal para cargas read-heavy con lecturas repetidas.
- Es write-through: transparente, no cambias el código casi.

> ElastiCache tambien sirve para cachear datos en memoria en bases de datos. Pero, DAX es una solución optimizada para DynamoDB


## DynamoDB Streams ⭐

- Streams captura un registro **ordenado** (cronológicamente) de los cambios (INSERT/MODIFY/REMOVE) en la tabla → Change Data Capture (CDC).
- Se conserva 24 horas.
- permite reaccionar a cambios en tiempo real
- Caso de uso estrella: DynamoDB Streams → Lambda para procesar cambios en tiempo real (event-driven).
- Permite replicar cambios, actualizar agregados, alimentar pipelines, etc.

> También existe **Kinesis Data Streams** for DynamoDB como alternativa para enviar los cambios a Kinesis con retención más larga y más consumidores.

## Global Tables

- Replicación multi-región, active-active (escribes y lees en cualquier región).
- Replicación asíncrona, eventualmente consistente entre regiones.
- Casos: baja latencia global y DR cross-region.
- Requiere Streams habilitado.

## TTL (Time To Live)

- Borra automáticamente items expirados según un atributo Unix Epoch timestamp.
- **Gratis**, no consume WCU
- ideal para datos temporales (sesiones, cache, logs).
- Los items cadudados se eliminan 48 horas despues de su caducidad

## Backups y recuperación

- PITR (Point-in-Time Recovery): restaura a cualquier segundo de los últimos 35 días.
- On-demand backups: snapshots manuales que persisten.

## Seguridad

- Encryption at rest por defecto (KMS).
- Control de acceso con IAM, incluso a nivel de item/atributo con fine-grained access control (condiciones IAM sobre dynamodb:LeadingKeys).
- VPC endpoints para acceso privado.

## Integración con analytics (data engineering)

Como DynamoDB es OLTP y no sirve para analytics, el examen pregunta cómo llevar sus datos a analytics:

- **Export to S3**: exportar tablas a S3 (formato DynamoDB JSON / Ion) sin consumir capacidad → luego Athena/Glue. Usa PITR por detrás.
- **Zero-ETL to Redshift / OpenSearch**: integración para analytics casi en tiempo real sin pipeline.
- DynamoDB Streams → Kinesis → analytics.
- Glue puede leer DynamoDB como fuente.


# PartiQL en DynamoDB

PartiQL es un lenguaje de consulta compatible con SQL que AWS creó para operar sobre datos no relacionales. En DynamoDB te permite usar sintaxis tipo SQL (CRUD) en lugar de las APIs nativas (GetItem, Query, Scan, etc.).

La idea: Mucha gente ya sabe SQL, así que PartiQL ofrece una capa familiar para interactuar con DynamoDB:
```sql
-- En lugar de la API Query nativa:
SELECT nombre, email
FROM "TiendaTabla"
WHERE "PK" = 'CLIENTE#42' AND begins_with("SK", 'PEDIDO#')
```

> Funciona vía la API `ExecuteStatement` (o `BatchExecuteStatement` para lotes, y también con transacciones).

partiQL es solo "sintaxis". Esto es clave y contraintuitivo. PartiQL no cambia cómo funciona DynamoDB por debajo — es solo una forma distinta de escribir la operación. Las mismas reglas y limitaciones siguen aplicando:

- Un SELECT de PartiQL se traduce por detrás a un Query (si usa la partition key) o a un Scan (si no la usa).
- Si escribes un SELECT cuyo WHERE no filtra por la partition key, PartiQL hace un Scan completo por debajo (implicando costo e ineficiencia). El hecho de "parecer SQL" no lo vuelve mágicamente eficiente. ⚠️⚠️⚠️
- Consume las mismas RCU/WCU (o RRU/WRU) que la operación equivalente.
- No habilita JOINs ni agregaciones complejas como un SQL real → sigue siendo DynamoDB, no una base relacional.
- Funciona en la consola, CLI y SDKs.
- Para control fino del performance, las APIs nativas (Query con KeyConditionExpression) son más explícitas sobre lo que consumes.

> PartiQL no es exclusivo de DynamoDB — AWS lo usa también en otros servicios (como Redshift, QLDB y para consultar en S3 con S3 Select). Es un lenguaje pensado para unificar consultas sobre datos estructurados, semiestructurados y anidados.


# Migrar otra base de datos a DynamoDB

DynamoDB tiene particularidades por ser NoSQL. No puedes migrar un esquema relacional tal cual a DynamoDB. Como vimos, el modelado es radicalmente distinto:

- En relacional tienes muchas tablas normalizadas con relaciones y JOINs.
- En DynamoDB modelas según access patterns, sueles desnormalizar y combinar entidades (single-table design).

Entonces, migrar implica rediseñar el modelo de datos primero (data modeling), no solo copiar filas. Si alguien intenta replicar las tablas relacionales 1:1 en DynamoDB, el resultado funciona mal (Scans, falta de JOINs, etc.).

## AWS DMS (Database Migration Service)

DMS es el servicio managed para migrar bases de datos. Soporta DynamoDB como target.

Cómo funciona:
- Un source endpoint (la base origen: RDS, Oracle, MySQL, MongoDB, etc.) y un target endpoint (DynamoDB).
- Una replication instance ejecuta la migración.
- Usas table mappings y object mapping rules (JSON) para definir cómo se transforman las filas del origen en items de DynamoDB — aquí especificas qué
columnas forman la partition key / sort key y cómo se estructuran los atributos.

### Tipos de migración en DMS:
- **Full Load**: copia todos los datos existentes una vez.
- **CDC (Change Data Capture)**: captura cambios continuos del origen y los replica → para mantener sincronizado o migrar con mínimo downtime.
- **Full Load + CDC**: copia lo existente y luego sigue replicando los cambios → el patrón típico para migrar sin parar la aplicación.

### Otras opciones según el escenario

- **Import from S3** → DynamoDB puede importar datos directamente desde S3 (formatos CSV, DynamoDB JSON, Ion) al crear una tabla nueva. Ideal si ya tienes los
datos exportados en S3 o puedes volcarlos ahí. No consume WCU y es más barato que escribir item por item.

- **AWS Glue** → puede leer de una fuente, transformar los datos (reshape al modelo NoSQL) y escribir en DynamoDB. Útil cuando la migración necesita transformaciones complejas.

- **Código custom / batch** → leer del origen y escribir con `BatchWriteItem`. Para casos a medida, pero menos recomendado para grandes volúmenes.

### Consideración de capacidad durante la migración

Un detalle práctico que puede aparecer: cargar millones de items consume mucha capacidad de escritura.

- Si usas DMS/escrituras, conviene usar On-Demand durante la carga (absorbe el pico sin throttling) o subir las WCU provisionadas temporalmente.
- Si usas Import from S3, este problema desaparece porque no consume WCU — otra razón por la que es atractivo para cargas iniciales masivas.


## Conceptos

## Exponential Backoff

Es una estrategia de reintentos (retry strategy) para manejar errores temporales. No es exclusivo de DynamoDB — se usa en toda la comunicación con APIs de AWS — pero conecta directo con el tema del throttling de DynamoDB.

**problema**: Cuando una request falla por un error temporal/transitorio (ej. DynamoDB te hace throttling con un error ProvisionedThroughputExceededException, o un 503
ServiceUnavailable), lo natural es reintentar. Pero si reintentas inmediatamente y de forma agresiva, empeoras las cosas: miles de clientes reintentando al mismo tiempo contra un servicio ya saturado.

**solución**: esperar cada vez más. Exponential backoff significa que, entre cada reintento, esperas progresivamente más tiempo, de forma exponencial.

## Jitter

Es un complemento al exponential backoff. Añade jitter (aleatoriedad) al tiempo de espera.

**Problema**: si todos los clientes usan exactamente los mismos intervalos, reintentarán todos sincronizados al mismo instante.

**Solución**: añadir un componente aleatorio a cada espera para desincronizar los reintentos y repartirlos en el tiempo. `espera = random(0, min(tiempo_máximo, base * 2^intento))`

> Exponential backoff + jitter es la práctica recomendada por AWS.
