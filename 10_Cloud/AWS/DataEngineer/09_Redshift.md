# Redshift

Redshift es el **data warehouse** fully managed de AWS. Es una base de datos relacional orientada a OLAP (analytics), es decir, pocas consultas pero muy pesadas, con agregaciones, joins y scans sobre volúmenes enormes de datos históricos. Es lo opuesto a RDS/Aurora (OLTP).

- Es relacional y habla SQL (basado en PostgreSQL, así que la sintaxis es muy familiar).
- Es el destino típico de un pipeline: los datos operacionales (RDS, DynamoDB, logs) se transforman (ETL) y se cargan en Redshift para business intelligence, reporting y analytics.
- Se integra con herramientas de BI (QuickSight, Tableau, etc.) vía JDBC/ODBC.

Lo que hace que Redshift sea rápido para analytics se basa en tres pilares: arquitectura MPP, almacenamiento columnar y compresión. 

## Pilar 1: Arquitectura MPP (Massively Parallel Processing)

Redshift distribuye los datos y el procesamiento de las consultas a través de múltiples nodos que trabajan en paralelo. Esta es la clave de su velocidad a escala.

La arquitectura de un cluster tradicional tiene dos tipos de nodos:

Leader Node
- Es el cerebro coordinador. Recibe las consultas de los clientes (aplicaciones, BI tools).
- Parsea la consulta SQL, desarrolla el plan de ejecución y lo optimiza.
- Compila el código y lo distribuye a los compute nodes.
- Agrega los resultados parciales de los compute nodes y devuelve el resultado final al cliente.
- No almacena datos de usuario; solo coordina. Es gratis (no se factura aparte).

Compute Nodes
- Son los que realmente almacenan los datos y ejecutan las consultas sobre su porción.
- Cada compute node se divide internamente en slices (porciones). Cada slice tiene una parte de la memoria y disco del nodo, y procesa su fragmento de datos en paralelo con los demás.
- El número de slices depende del tipo de nodo. Los datos se reparten entre los slices → el paralelismo real ocurre a nivel de slice.

```
     Cliente / BI tool
             │
             │ SQL
             ▼
      ┌──────────────┐
      │ Leader Node  │  (planifica, optimiza, agrega resultados)
      └──────┬───────┘
      ┌──────┼──────┐
      ▼      ▼      ▼
[Compute][Compute][Compute]   ← cada uno con sus slices
 slices   slices   slices     ← procesan en paralelo
```
Cuando necesitas más capacidad, agregas más nodos (scaling horizontal) → más slices → más paralelismo.

## Pilar 2: Almacenamiento columnar (columnar storage)

Redshift guarda los datos por columnas, no por filas. Esto es fundamental para analytics:

- Una consulta analítica típica (SELECT SUM(ventas) FROM ...) solo necesita unas pocas columnas de millones de filas. Con almacenamiento columnar, Redshift solo lee las columnas involucradas, ignorando el resto → muchísimo menos I/O de disco.
- En cambio, una base row-based tendría que leer filas completas (todas las columnas) aunque solo necesites una → desperdicio enorme en analytics.

## Pilar 3: Compresión (column encoding)

Como cada columna almacena datos del mismo tipo juntos (todos enteros, todas fechas, etc.), se comprimen muy eficientemente. Redshift llama a esto **compression encodings**.

- Menos datos en disco → menos I/O → consultas más rápidas + menor costo de storage.
- Redshift puede elegir el encoding óptimo automáticamente (el comando COPY con `COMPUPDATE`, o `ANALYZE COMPRESSION`, o el encoding AZ64, muy eficiente para numéricos y fechas).
- Es un proceso casi transparente, pero conviene saber que existe.

## Tipos de nodo y arquitecturas

- DS — Dense Storage (legacy)
    - Optimizados para almacenar grandes volúmenes de datos a bajo costo, usando HDD.
    - Priorizan capacidad de storage sobre velocidad
    - La versión fue DS2. Hoy están obsoletos — AWS recomienda migrar de DS2 a RA3.

- DC — Dense Compute
    - Optimizados para performance, usando SSD y más CPU/RAM por nodo.
    - Priorizan velocidad de cómputo sobre capacidad
    - La versión actual es DC2.
    - Caso: datasets más pequeños (que caben en el SSD local) donde quieres máximo rendimiento de consulta.

- RA3 nodes
    - Separan cómputo y almacenamiento: los datos se guardan en Redshift Managed Storage (RMS), respaldado por S3, y los nodos usan SSD local solo como caché de los datos más usados.
    - Esto permite escalar cómputo y storage de forma independiente → pagas cómputo por lo que necesitas y el storage escala automáticamente en S3.

- Redshift Serverless
    - No gestionas clusters ni nodos. Redshift provisiona y escala la capacidad automáticamente según la carga.
    - Pagas por RPUs (Redshift Processing Units) por segundo de uso.
    - Ideal para cargas variables, intermitentes o impredecibles, o cuando no quieres administrar un cluster.
    - Con Redshift Serverless no se puede usar Redshift Spectrum

## Distribution Styles

Como los datos se reparten entre nodos/slices, cómo los distribuyes afecta enormemente el performance. Cuando una consulta hace un JOIN, si las filas que deben unirse están en nodos distintos, Redshift tiene que mover datos entre nodos por la red (lo que se llama data shuffling o redistribution) → lento. El objetivo de elegir bien la distribution style es minimizar ese movimiento.

1. KEY distribution
    - Las filas se distribuyen según el valor de una columna (la dist key). Filas con el mismo valor van al mismo slice.
    - Ideal para JOINs: si distribuyes dos tablas por la columna del JOIN, las filas que se unen quedan co-localizadas en el mismo nodo → el JOIN es local, sin movimiento de datos.
    - Riesgo: si la columna tiene valores desbalanceados → data skew (unos slices con muchos más datos que otros).

2. ALL distribution
    - Una copia completa de la tabla en cada nodo.
    - Ideal para tablas de dimensión pequeñas que se usan en muchos JOINs → como están en todos los nodos, el JOIN nunca necesita mover datos.
    - Costo: ocupa mucho espacio (se replica entera) y ralentiza las escrituras. Solo para tablas pequeñas.

3. EVEN distribution
    - Las filas se reparten round-robin (método de repartir elementos de forma cíclica y secuencial) uniformemente entre slices, sin considerar valores.
    - Default cuando no hay un patrón de JOIN claro. Distribuye parejo pero no optimiza JOINs.

4. AUTO distribution (default actual)
    - Redshift elige automáticamente el estilo: empieza con ALL cuando la tabla es pequeña y cambia a KEY o EVEN a medida que crece. Es el default moderno.

> La idea general del examen: las tablas de hechos grandes (fact tables) suelen ir en KEY (por la columna de JOIN), y las dimensiones pequeñas en ALL.

## Sort Keys

Además de cómo se distribuyen, importa cómo se ordenan físicamente los datos en disco. La sort key define el orden de almacenamiento de las filas.

Al estar ordenados, Redshift puede saltarse bloques enteros de datos que no cumplen el filtro de una consulta (usando zone maps, que guardan el min/max de cada bloque) → menos I/O. Esto se llama a veces "block pruning".

Ejemplo: si ordenas por fecha y consultas "ventas de octubre 2026", Redshift ignora todos los bloques fuera de ese rango sin leerlos.

Tipos:
- **Compound sort key** (default): ordena por varias columnas en un orden jerárquico (primero col A, luego B...). Muy eficiente cuando los filtros usan el prefijo de la sort key.
- **Interleaved sort key**: da igual peso a varias columnas. Útil cuando consultas por columnas distintas de forma impredecible, pero tiene overhead de mantenimiento.

> La combinación de distribution style + sort key bien elegidos es lo que más impacta el performance de un cluster Redshift.

## Cargar y extraer datos: COPY y UNLOAD

**COPY** — la forma correcta de cargar datos
    - El comando COPY carga datos masivamente a Redshift, típicamente desde S3 (también desde DynamoDB, EMR, o vía SSH).
    - Es mucho más eficiente que hacer INSERT fila por fila, porque carga en paralelo distribuyendo el trabajo entre todos los slices simultáneamente.
    - Para máximo paralelismo, conviene dividir el archivo origen en múltiples archivos (idealmente un múltiplo del número de slices) → cada slice carga un archivo en paralelo.
    - Usa un IAM role (vía la cláusula IAM_ROLE) para acceder a S3.
    - Soporta varios formatos: CSV, JSON, Parquet, ORC, Avro.

> Regla clave: para cargas masivas siempre COPY desde S3, nunca INSERTs individuales.

**UNLOAD** — exportar datos
    - El comando UNLOAD hace lo inverso: exporta el resultado de una consulta desde Redshift hacia S3, en paralelo.
    - Útil para mover datos procesados de vuelta al data lake, compartirlos, o archivarlos. Puede escribir en Parquet (columnar).


## Redshift Spectrum

Spectrum permite ejecutar consultas SQL de Redshift directamente sobre datos en S3, sin cargarlos antes al cluster.

- Defines tablas externas (external tables) cuyo esquema vive en el AWS Glue Data Catalog (o Hive metastore), apuntando a los archivos en S3.
- Puedes hacer JOINs entre tablas locales de Redshift y datos en S3 en una sola consulta.
- Spectrum usa una flota de nodos separada y masiva (gestionada por AWS) que escanea S3 en paralelo, así que no consume los nodos de tu cluster para el scan.
- Se factura por datos escaneados en S3 (como Athena), así que particionar y usar Parquet reduce el costo drásticamente.

> Es clave para la arquitectura lake house: mantienes datos "fríos" o enormes en S3 y los datos "calientes" en el cluster, consultando ambos juntos.

> Diferencia conceptual con Athena: Athena es serverless e independiente (bueno para consultas ad-hoc sobre S3); Spectrum es una extensión de Redshift que une S3 con tus tablas del warehouse.

## Concurrency Scaling

Problema: si llegan muchas consultas simultáneas, el cluster puede saturarse y las consultas hacen cola.

- Concurrency Scaling agrega clusters transitorios automáticamente cuando hay picos de concurrencia, y los quita cuando baja la demanda.
- Da capacidad de lectura casi ilimitada para esos picos, de forma transparente.
- AWS lo ofrece con créditos gratis acumulables (1 hora de crédito por cada 24h de uso del cluster), lo que lo hace a menudo sin costo extra.

## Workload Management (WLM)

WLM gestiona cómo se asignan los recursos a las consultas y define colas (queues) de ejecución.

- Puedes crear colas para separar cargas (ej. una cola para ETL pesado, otra para consultas rápidas de BI) y asignarles memoria y concurrencia.
- **Auto WLM**: Redshift gestiona esto automáticamente (recomendado). **Manual WLM**: tú defines las colas y parámetros.
- **Short Query Acceleration (SQA)**: prioriza automáticamente las consultas cortas para que no esperen detrás de las largas.
- Permite reglas de **QMR (Query Monitoring Rules)** para abortar o registrar consultas que consumen demasiado.

## Materialized Views

- Una materialized view precomputa y almacena el resultado de una consulta (joins, agregaciones costosas).
- Las consultas posteriores leen el resultado ya calculado → mucho más rápidas.
- Se pueden refrescar (manual, programado, o auto-refresh), y Redshift soporta incremental refresh (solo recalcula lo que cambió).
- Ideal para dashboards/reportes recurrentes sobre las mismas agregaciones pesadas.

## Data Sharing

- Permite compartir datos entre clusters de Redshift (y con Serverless) sin copiarlos ni moverlos, en vivo.
- El cluster productor expone datos y los consumidores los leen directamente.
- Casos: separar cargas (un cluster de ETL y otro de BI sobre los mismos datos), compartir entre equipos/cuentas, arquitecturas multi-cluster. Requiere nodos RA3.

## Zero-ETL y integraciones

- **Aurora/RDS Zero-ETL to Redshift**: replica datos transaccionales a Redshift casi en tiempo real sin construir pipeline ETL → analytics sobre datos frescos.
- **Federated Queries**: Redshift puede consultar directamente bases RDS/Aurora PostgreSQL/MySQL en vivo, sin mover los datos.
- **Redshift ML**: crear y usar modelos de machine learning con SQL, integrado con SageMaker (CREATE MODEL ...).
- **Streaming ingestion**: ingesta directa desde Kinesis Data Streams o MSK hacia una materialized view, para analytics casi en tiempo real.

| Mecanismo       | Accede a                                    | Mueve datos?                 |
| --------------- | ------------------------------------------- | ---------------------------- |
| Federated Query | Bases RDS/Aurora (PostgreSQL/MySQL) en vivo | No                           |
| Spectrum        | Datos en S3                                 | No                           |
| Data Sharing    | Otros clusters Redshift                     | No                           |
| Zero-ETL        | Replica desde Aurora/RDS/DynamoDB           | Sí (replica automáticamente) |


## Seguridad

- Encryption at rest con KMS (o HSM); in transit con SSL.
- Despliegue en VPC, control con security groups; se puede aislar con Enhanced VPC Routing (fuerza que el tráfico COPY/UNLOAD pase por tu VPC).
- Control de acceso con IAM y permisos SQL nativos (GRANT/REVOKE a usuarios y grupos).
- Column-level y row-level security para control granular de quién ve qué.
- Integración con Lake Formation para gobernanza centralizada vía Spectrum.
- Redshift usa IAM roles para COPY/UNLOAD/Spectrum (nada de credenciales incrustadas).

## Backups y disponibilidad

- Snapshots automáticos (incrementales) a S3, con retención configurable; también manuales. Se pueden copiar a otra región (DR).
- Restaurar un snapshot crea un cluster nuevo.
- Los RA3 con RMS tienen durabilidad respaldada por S3.
- Multi-AZ disponible para Redshift (en RA3) para alta disponibilidad con failover automático.
- **Resize** (redimensionamiento): Proceso de cambiar la capacidad de un cluster: modificar el número de nodos o el tipo de nodo. Lo necesitas cuando tu carga de trabajo crece o cuando quieres ajustar costos.

-Elastic Resize
    - Cambia el número de nodos del cluster (agregar o quitar), o en algunos casos el tipo de nodo.
    - Es rápido: típicamente tarda unos minutos (10–15 min normalmente). Las consultas se pausan/quedan en cola momentáneamente, luego se reanudan.
    - Funciona redistribuyendo las particiones (slices) de datos entre el nuevo conjunto de nodos, en lugar de copiar todo desde cero.
    - Limitación: solo puedes cambiar el número de nodos dentro de ciertos rangos (por ejemplo, duplicar o reducir a la mitad, con límites según el tipo de nodo). No sirve para cambios arbitrariamente grandes.
    - Es el que usas para ajustes de capacidad del día a día, incluso programados (ej. escalar para la carga de ETL nocturna y reducir de día).

- Classic Resize
    - Permite cambiar a cualquier configuración de nodos y cambiar el tipo de nodo sin las restricciones de rango del elastic.
    - Funciona copiando todos los datos a un cluster nuevo con la nueva configuración → por eso es lento: puede tardar horas o días según el volumen de datos.
    - Durante gran parte del proceso el cluster queda en modo solo lectura (read-only) → impacto mayor en disponibilidad.
    - Se usa cuando el elastic resize no puede hacer el cambio deseado (cambios de tipo de nodo, o cambios de tamaño fuera de los rangos permitidos).

## Mantenimiento: VACUUM y ANALYZE

Dos operaciones de mantenimiento que conviene conocer:
- **VACUUM**: reordena las filas según la sort key y recupera espacio de filas borradas (en analytics se borra/actualiza en bloque). Redshift moderno hace auto-vacuum.
- **ANALYZE**: actualiza las estadísticas de las tablas que el optimizador usa para planificar consultas. También hay auto-analyze.

## UDF (User-Defined Function)

Una UDF es una función personalizada que tú defines y que luego puedes invocar dentro de tus consultas SQL, igual que usarías una función nativa (como `SUM()` o `UPPER()`). Sirven para encapsular lógica propia y reutilizarla en las queries. Redshift soporta varios tipos:

1. SQL UDF
    - Escrita en SQL. Encapsula una expresión SQL reutilizable.
    - Simple, para lógica que se puede expresar con SQL.

2. Python UDF (scalar)
    - Escrita en Python. Permite lógica más compleja (manipulación de strings, cálculos, etc.) que no es fácil en SQL puro.
    - Se ejecuta dentro del cluster.

3. Lambda UDF
    - La función se ejecuta en una función AWS Lambda externa, no dentro del cluster.
    - Redshift invoca la Lambda durante la consulta, le pasa los datos, y la Lambda devuelve el resultado.
    - Puede usar cualquier lenguaje/runtime soportado por Lambda
    - Integración con servicios externos: como la Lambda es código arbitrario, puede llamar a otros servicios de AWS o APIs externas durante la consulta.
    - Casos típicos:
        - Enmascaramiento/tokenización de datos sensibles usando un servicio externo.
        - Enriquecer datos consultando otra fuente o API.
        - Acceder a secretos, hacer cálculos especializados, invocar modelos, etc.
