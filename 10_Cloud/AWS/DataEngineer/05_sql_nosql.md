# SQL vs NoSQL

|                  | SQL                       | NoSQL                                                |
| ---------------- | ------------------------- | ---------------------------------------------------- |
| Schema           | Fijo (schema-on-write)    | Flexible (schema-on-read)                            |
| Relaciones/Joins | Sí                        | No (datos desnormalizados)                           |
| Escalado         | Vertical (principalmente) | Horizontal                                           |
| Consistencia     | ACID                      | BASE / eventual (configurable)                       |
| Datos            | Estructurados             | Semi/no estructurados                                |
| Patrón           | Queries flexibles, ad-hoc | Patrones de acceso conocidos, baja latencia a escala |

## SQL

Las bases relacionales (RDBMS) organizan los datos en tablas con filas y columnas, con un schema fijo y predefinido (defines las columnas y tipos antes de cargar datos).

Características clave:
- Schema-on-write: la estructura se define antes de escribir. El dato debe ajustarse al schema.
- Relaciones entre tablas mediante foreign keys y joins.
- Lenguaje estándar: SQL.
- Priorizan consistencia e integridad → transacciones ACID (Atomicity, Consistency, Isolation, Durability).
- Scaling vertical por naturaleza (máquina más grande); escalar horizontalmente es más difícil.
- Caso de uso: datos estructurados, relaciones complejas, transacciones (OLTP), reporting.

> Servicios AWS: **RDS** (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server), **Aurora**, y **Redshift** (data warehouse, analytics/OLAP).

## NoSQL

Las bases NoSQL ("Not Only SQL") renuncian al modelo relacional rígido para ganar flexibilidad y escala horizontal.

Características clave:
- Schema-flexible / schema-on-read: no necesitas definir la estructura por adelantado; cada item puede tener atributos distintos.
- No hacen joins (o muy limitados) — los datos suelen desnormalizarse (todo junto en un item).
- Scaling horizontal: diseñadas para distribuirse en muchos nodos (sharding/partitioning) → manejan volúmenes y throughput enormes.
- Suelen seguir el modelo BASE (Basically Available, Soft state, Eventual consistency) en vez de ACID estricto, aunque algunas (como DynamoDB) ofrecen consistencia fuerte opcional.
- Caso de uso: datos semiestructurados/no estructurados, altísimo volumen, baja latencia, patrones de acceso conocidos y simples.

Servicios AWS: **DynamoDB** (key-value/document), **DocumentDB** (document), **ElastiCache** (in-memory), **Keyspaces** (wide-column/Cassandra), **Neptune** (graph), **Timestream** (time series).

### Tipos de bases de datos NoSQL

Las NoSQL se clasifican en 4 tipos principales según cómo modelan los datos:

| Tipo        | Modelo             | Servicio AWS          | Uso típico                  |
| ----------- | ------------------ | --------------------- | --------------------------- |
| Key-Value   | clave → valor      | DynamoDB, ElastiCache | caching, sessions, carritos |
| Document    | documentos JSON    | DocumentDB, DynamoDB  | catálogos, perfiles         |
| Wide-Column | column families    | Keyspaces (Cassandra) | IoT, logging masivo         |
| Graph       | nodes + edges      | Neptune               | recomendaciones, fraude     |
| In-Memory   | clave-valor en RAM | ElastiCache, MemoryDB | caching ultrarrápido        |
| Time Series | datos temporales   | Timestream            | métricas, telemetría IoT    |


#### 1. Key-Value (clave-valor)

El modelo más simple: cada item es un par clave → valor. Buscas por la clave y obtienes el valor (que puede ser cualquier cosa, un blob opaco).
- Muy rápido, escala enorme.
- Ejemplos AWS: DynamoDB, ElastiCache (Redis/Memcached).
- Uso: session stores, carritos de compra, caching, perfiles de usuario.

#### 2. Document (documento)

Guarda documentos (típicamente JSON, BSON) donde cada documento es autocontenido y puede tener estructura anidada y variable.
- Es como un key-value pero el valor es un documento consultable por sus campos internos.
- Ejemplos AWS: DocumentDB (compatible MongoDB), DynamoDB (también se considera document).
- Uso: catálogos de productos, perfiles, contenido con estructura variable.

#### 3. Wide-Column (columnar / column-family)

Organiza datos en column families; cada fila puede tener columnas distintas. Optimizado para escribir y leer enormes volúmenes con consultas por clave.
- Ejemplos AWS: Keyspaces (compatible Apache Cassandra), y el concepto detrás de HBase en EMR.
- Uso: datos de IoT a gran escala, time series, logging masivo.

#### 4. Graph (grafo)

Modela entidades (nodes) y relaciones (edges) entre ellas. Optimizado para recorrer relaciones complejas.
- Ejemplos AWS: Neptune.
- Uso: redes sociales, motores de recomendación, detección de fraude, grafos de conocimiento.

#### Tipos adicionales que pueden aparecer

- In-Memory: datos en RAM para latencia de microsegundos → ElastiCache, MemoryDB. Uso: caching, leaderboards.
- Time Series: optimizadas para datos con timestamp → Amazon Timestream. Uso: métricas, IoT, telemetría.

# Terminología

## Ad-hoc

Ad-hoc es una expresión latina que significa literalmente "para esto" o "para este propósito específico". En el mundo de datos, una query ad-hoc es una **consulta improvisada, puntual y no planificada de antemano**, que escribes en el momento para responder una pregunta específica que surge.

- **Query ad-hoc**: la inventas sobre la marcha para explorar o responder algo puntual. Ejemplo: "¿cuántos clientes de Bogotá compraron más de 3 veces el mes pasado?" — una pregunta que se te ocurrió ahora y que quizás no vuelvas a hacer.

- **Query predefinida**: está preparada y optimizada de antemano, se ejecuta de forma repetida (ej. un reporte diario, el acceso que hace una aplicación por su clave).

Es una diferencia clave entre ambos mundos:

- Las bases SQL/relacionales son excelentes para queries ad-hoc: como tienen schema y soportan joins, filtros y agregaciones flexibles, puedes consultar los datos de cualquier forma sin haberlo previsto.

- Las bases NoSQL no son buenas para ad-hoc: están diseñadas para patrones de acceso conocidos de antemano. Si intentas consultar de una forma para la que no modelaste la tabla (ej. buscar por un atributo que no es la key), es ineficiente o imposible sin estructuras adicionales.

## OLTP vs OLAP

Dos tipos de procesamiento de datos con propósitos opuestos. Entender esta diferencia es fundamental porque define cuándo usar RDS/Aurora/DynamoDB vs Redshift/Athena.

|                     | OLTP                        | OLAP                        |
| ------------------- | --------------------------- | --------------------------- |
| Propósito           | Transacciones operacionales | Analytics / reporting       |
| Queries             | Muchas, pequeñas, rápidas   | Pocas, complejas, pesadas   |
| Filas por operación | Pocas                       | Millones                    |
| Storage             | Row-based                   | Columnar                    |
| Datos               | Actuales, normalizados      | Históricos, desnormalizados |
| Concurrencia        | Muy alta                    | Más baja                    |
| Servicios AWS       | RDS, Aurora, DynamoDB       | Redshift, Athena, EMR       |

### OLTP (Online Transaction Processing)

Procesamiento de transacciones del día a día de una aplicación. Son las operaciones operacionales: insertar un pedido, actualizar un saldo, registrar un usuario.

- **Operaciones**: muchas, pequeñas y rápidas (INSERT, UPDATE, DELETE, SELECT puntuales).
- **Acceso**: lee/escribe pocas filas a la vez (ej. "dame el cliente con id=42").
- **Volumen por query**: pequeño, pero muchísimas queries concurrentes.
- **Datos**: actuales, operacionales, muy normalizados.
- **Optimización**: row-based storage (guarda la fila completa junta).
- **Objetivo**: baja latencia, integridad transaccional (ACID).
- **Servicios AWS**: RDS, Aurora, DynamoDB.

### OLAP (Online Analytical Processing)

Procesamiento analítico: consultas complejas sobre grandes volúmenes de datos históricos para obtener insights, reporting y business intelligence.

- **Operaciones**: pocas pero complejas y pesadas (agregaciones, joins grandes, GROUP BY, sumas sobre millones de filas).
- **Acceso**: escanea muchísimas filas pero normalmente pocas columnas (ej. "suma de ventas por región en los últimos 5 años").
- **Volumen por query**: enorme.
- **Datos**: históricos, agregados, a menudo desnormalizados (star/snowflake schema).
- **Optimización**: columnar storage (guarda cada columna junta → lee solo las columnas necesarias, comprime mejor).
- **Objetivo**: throughput analítico, no latencia transaccional.
- **Servicios AWS**: Redshift (data warehouse), Athena, EMR, Redshift Spectrum.

### Cómo trabajan juntas

Los datos suelen fluir de OLTP → OLAP:
```
Fuentes OLTP (RDS/Aurora/DynamoDB)
        │
        │  (ETL con Glue/DMS, o Zero-ETL)
        ▼
Data lake (S3) / Data warehouse (Redshift)  ──► Analytics (Athena, BI)
```

El rol del data engineer es justamente mover y transformar los datos desde los sistemas OLTP (transaccionales) hacia entornos OLAP (analíticos) usando pipelines (Glue, DMS, Zero-ETL, Kinesis).

Por qué importa el row vs columnar (dato clave)

- **Row-based (OLTP)**: para traer "toda la fila de un cliente" es eficiente → leo un registro completo de golpe.
- **Columnar (OLAP)**: para "sumar una columna sobre millones de filas" solo leo esa columna → mucho menos I/O, mejor compresión. Por eso Redshift y Parquet son columnar.


## Locks en bases de datos

los locks (bloqueos) son un concepto general de bases de datos (parte de cómo los RDBMS manejan la concurrencia), no una feature específica de RDS.

Un lock es un mecanismo que la base de datos usa para controlar el acceso concurrente a los datos cuando varias transacciones quieren leer/modificar lo mismo al mismo tiempo. Evita que se corrompan los datos o se produzcan resultados inconsistentes.

Ejemplo del problema: dos usuarios intentan actualizar el saldo de la misma cuenta al mismo tiempo. Sin control, uno podría sobrescribir el cambio del otro. El lock serializa esos accesos.

Tipos de locks (conceptual)

- **Shared lock (S) / read lock**: varias transacciones pueden leer el mismo dato a la vez (comparten el lock). Nadie puede escribir mientras haya un read lock.
- **Exclusive lock (X) / write lock**: solo una transacción puede modificar el dato; bloquea a las demás (ni lectura ni escritura) hasta que termine.

### El comando LOCK

En SQL existe LOCK (su sintaxis varía según el motor), por ejemplo en MySQL:

```sql
LOCK TABLES empleados WRITE;   -- bloquea la tabla para escritura exclusiva
-- ... operaciones ...
UNLOCK TABLES;
```

También hay bloqueo a nivel de fila con SELECT ... FOR UPDATE:

```sql
SELECT * FROM cuentas WHERE id = 10 FOR UPDATE;  -- bloquea esa fila
```

Los locks pueden ser a nivel de:
- Row-level (fila): bloquea solo las filas afectadas → más concurrencia (ej. InnoDB en MySQL, PostgreSQL).
- Table-level (tabla): bloquea la tabla entera → más simple pero menos concurrencia.

Conceptos relacionados que sí pueden rozar el examen

- **Deadlock**: dos transacciones se bloquean mutuamente esperando un recurso que la otra tiene → la base detecta esto y aborta una de ellas. Síntoma de problemas de concurrencia.
- **ACID / Isolation**: los locks implementan el nivel de aislamiento (isolation) de las transacciones — cuánto se "ven" entre sí las transacciones concurrentes.
- **MVCC (Multi-Version Concurrency Control)**: alternativa a los locks que usan PostgreSQL y Aurora/MySQL (InnoDB) → mantienen versiones de los datos para que las lecturas no bloqueen a las escrituras. Mejora la concurrencia.

Relevancia para el examen (seamos honestos)

El DEA-C01 no te va a preguntar sintaxis de LOCK ni detalles finos de locking. Lo que sí importa es el concepto de fondo:
- Las bases relacionales (RDS/Aurora) garantizan ACID usando locks/MVCC → consistencia transaccional fuerte.
- Las bases NoSQL (DynamoDB) evitan ese modelo de locking pesado para lograr escala horizontal; manejan concurrencia de otra forma (ej. optimistic locking con conditional writes y version numbers).

Dato útil de DynamoDB (esto sí es más de examen): DynamoDB usa optimistic concurrency control — en vez de bloquear, usa conditional writes (ej. "actualiza solo si el atributo version sigue siendo X"). Si otro lo cambió antes, la escritura falla y reintentas. Es el equivalente "NoSQL" a manejar concurrencia sin locks tradicionales.


## Comandos SQL básicos

Estos son comandos estándar de SQL (aplican a Redshift, RDS, Aurora y bases relacionales en general). Se agrupan por categorías:

- DML (Data Manipulation Language)
    - INSERT: agrega filas nuevas a una tabla.
    - SELECT: consulta/lee datos.
    - UPDATE: modifica filas existentes.
    - DELETE: elimina filas.

- DDL (Data Definition Language)
    - CREATE: crea objetos (tablas, vistas, esquemas).
    - ALTER: modifica la estructura de un objeto.
    - DROP: elimina un objeto completo.
    - TRUNCATE: borra todas las filas de una tabla de golpe (más rápido que DELETE, no fila por fila).

- DCL (Data Control Language)
    - GRANT: otorga permisos a usuarios/grupos.
    - REVOKE: retira permisos.

- TCL (Transaction Control Language)
    - COMMIT: confirma una transacción, haciendo permanentes los cambios.
    - ROLLBACK: deshace los cambios de una transacción no confirmada.
    - BEGIN: inicia una transacción.

> Nota sobre transacción: conjunto de operaciones que se ejecutan como una unidad all-or-nothing (se confirma con COMMIT o se revierte con ROLLBACK). Es la base de las propiedades ACID.

## JDBC y ODBC

Son dos APIs estándar que permiten a las aplicaciones conectarse y comunicarse con bases de datos usando SQL. Actúan como una capa intermedia estandarizada entre tu aplicación y la base de datos.

El problema que resuelven: Cada motor de base de datos tiene su propio protocolo nativo de comunicación. Sin un estándar, cada aplicación tendría que programarse específicamente para cada base. JDBC y ODBC ofrecen una interfaz común: tu aplicación habla con la API estándar, y un driver traduce esas llamadas al protocolo específico de la base. Así, cambiar de base de datos requiere cambiar el driver, no reescribir la aplicación.
```
Aplicación / BI tool
│  (llamadas estándar SQL)
▼
Driver JDBC/ODBC   ← traduce al protocolo de la base
│
▼
Base de datos (Redshift, RDS, Aurora...)
```
### JDBC (Java Database Connectivity)

- API específica de Java (y lenguajes de la JVM).
- Permite que aplicaciones Java ejecuten SQL contra cualquier base que tenga un driver JDBC.
- Es la opción natural en ecosistemas Java (muchas herramientas de datos y BI están escritas en Java).

### ODBC (Open Database Connectivity)

- API independiente del lenguaje y la plataforma (creada por Microsoft, hoy estándar general).
- No está atada a Java → la usan aplicaciones en C/C++, .NET, Python, herramientas de Windows, etc.
- Más universal en términos de lenguajes.

En la práctica, ambos hacen lo mismo (conectar a una base y ejecutar SQL); la elección depende del lenguaje/plataforma de la herramienta que se conecta.

Lo relevante es entender que servicios como Redshift, RDS y Aurora proporcionan endpoints JDBC/ODBC como mecanismo estándar de conexión. Herramientas de BI y analytics (Tableau, Power BI, QuickSight, clientes SQL, aplicaciones) se conectan a estos servicios mediante estos drivers. Es simplemente la vía estándar de conectividad a bases de datos relacionales.

## Views and Materialized Views

### View — no Materialized

Una view es una consulta guardada a la que le das un nombre, y que se comporta como si fuera una tabla. Pero la clave es que una view normal NO almacena
datos — es solo la definición de la consulta guardada.

- Cada vez que consultas la view, la base de datos ejecuta la query subyacente en ese momento, sobre las tablas reales.
- Es como un "atajo" o un alias para una consulta compleja: en vez de escribir un JOIN largo cada vez, lo guardas como view y consultas `SELECT * FROM
mi_view`.

Ventajas:
- Los datos siempre están actualizados (se calculan al vuelo sobre las tablas reales).
- No ocupa espacio de almacenamiento (solo guarda la definición).
- Simplifica consultas complejas y puede ocultar columnas sensibles (una forma de seguridad).

Desventaja:
- Si la consulta subyacente es pesada (joins grandes, agregaciones sobre millones de filas), la pagas cada vez que consultas la view → puede ser lento.


### Materialized view

Una materialized view resuelve justo esa desventaja: SÍ almacena físicamente el resultado de la consulta (lo "materializa" en disco).

- La query pesada se ejecuta una vez (o cuando se refresca), y el resultado queda guardado.
- Las consultas posteriores leen el resultado ya precomputado → muchísimo más rápidas, no recalculan nada.

Ventaja:
- Performance: ideal para consultas costosas que se repiten (dashboards, reportes recurrentes sobre las mismas agregaciones).

Desventaja:
- Los datos pueden quedar desactualizados (stale): como es una "foto" del momento en que se calculó, si las tablas base cambian, la vista materializada no
lo refleja hasta que se refresca.
- Ocupa espacio de almacenamiento (guarda los datos).

#### El refresh

La diferencia operativa central de una materialized view es que necesita refrescarse para actualizarse:
- **Manual**: ejecutas un comando de refresh cuando quieras.
- **Programado**: cada cierto tiempo.
- **Automático**: la base lo refresca sola cuando detecta cambios (Redshift soporta auto-refresh).
- **Incremental refresh**: en vez de recalcular todo, solo procesa los cambios desde el último refresh → mucho más eficiente (Redshift lo soporta).


En el contexto de AWS

- En Redshift, las materialized views son muy usadas para acelerar dashboards de BI y agregaciones recurrentes, con auto-refresh e incremental refresh.
También son el destino de la streaming ingestion (Kinesis/MSK → materialized view).
- Existen en prácticamente todas las bases relacionales (PostgreSQL, Oracle, etc.) y el concepto aparece también en Athena/otros motores analíticos.

## Federated Query

Una consulta federada es aquella que accede a datos que viven en fuentes de datos externas y distintas, consultándolas directamente en su ubicación original, sin tener que mover o copiar esos datos primero.

Normalmente, para analizar datos de varias fuentes, tendrías que extraerlos y cargarlos todos en un mismo lugar (un proceso ETL). La consulta federada invierte eso: en vez de traer los datos hacia la consulta, lleva la consulta hacia los datos, allí donde están, y combina los resultados. El motor que ejecuta la consulta se encarga de "empujar" (push down) partes de la consulta a cada fuente, recibir los resultados parciales y combinarlos.

En el contexto de AWS/Redshift, específicamente permite que Redshift consulte directamente bases de datos operacionales sin cargar sus datos al warehouse:

Redshift puede consultar en vivo RDS/Aurora PostgreSQL y RDS/Aurora MySQL. Puedes hacer un JOIN en una sola query entre:
- tablas locales de Redshift,
- datos operacionales en RDS/Aurora (vía federated query),
- y datos en S3 (vía Spectrum).

Todo en una sola sentencia SQL, sin pipeline de por medio.

> Esto es muy potente porque te permite combinar datos transaccionales frescos (lo que está ahora mismo en la base operacional) con datos históricos del warehouse, en tiempo real.

Cómo funciona por debajo:

Redshift empuja (query pushdown) parte del filtrado y procesamiento a la base remota, para que esta haga parte del trabajo y devuelva solo los datos
necesarios (en vez de traer tablas enteras). Esto reduce el volumen transferido. Requiere conectividad de red (la base debe ser accesible) y credenciales, que se gestionan con AWS Secrets Manager y un IAM role.

Consideraciones:

- Performance: consultar una base operacional (OLTP) con cargas analíticas pesadas puede impactar su rendimiento (la base transaccional no está optimizada para scans masivos). Hay que usarlo con criterio, apoyándose en el pushdown.
- No reemplaza al ETL para todos los casos: para análisis masivos recurrentes, sigue siendo mejor cargar los datos al warehouse.

> Dato adicional: Athena también es federado

> El concepto no es exclusivo de Redshift. Athena Federated Query permite a Athena consultar fuentes más allá de S3 (DynamoDB, RDS, bases externas, etc.) usando conectores basados en Lambda (data source connectors).