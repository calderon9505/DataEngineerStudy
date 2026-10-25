# Amazon DocumentDB

Base de datos NoSQL de tipo documento, compatible con **MongoDB**.

- Almacena documentos JSON/BSON con estructura flexible y anidada, consultables por sus campos internos.
- Es compatible con la API de MongoDB → aplicaciones que ya usan MongoDB pueden migrar sin reescribir el código (usan los mismos drivers).
- **Managed**: AWS gestiona infraestructura, backups, escalado, parcheo.
- Arquitectura que separa cómputo y almacenamiento (similar en filosofía a Aurora): storage auto-escalable, réplicas de lectura, alta disponibilidad multi-AZ.
- **Cuándo elegirla**: cargas de trabajo basadas en documentos que necesitan compatibilidad con MongoDB (catálogos de productos, perfiles de usuario, gestión
de contenido con estructura variable).
- **vs DynamoDB**: DynamoDB es key-value/document serverless sin servidores que gestionar; DocumentDB es específicamente para compatibilidad MongoDB y
consultas más ricas sobre documentos.

# Amazon Neptune

Base de datos de grafos (graph database) totalmente managed.

- Modela entidades (nodes/vértices) y las relaciones (edges/aristas) entre ellas, optimizada para recorrer relaciones complejas eficientemente.
- Soporta los lenguajes/modelos de grafos estándar: **Gremlin** (property graph, Apache TinkerPop), **openCypher**, y *SPARQL* (RDF).
- Cuándo elegirla: cuando el valor está en las conexiones entre datos:
    - Redes sociales (quién conoce a quién).
    - Motores de recomendación ("usuarios que compraron esto también compraron...").
    - Detección de fraude (encontrar patrones y anillos de relaciones sospechosas).
    - Grafos de conocimiento y datos de identidad.

> La ventaja frente a una relacional: consultas de relaciones muy profundas (muchos "saltos") que en SQL requerirían JOINs recursivos carísimos, en un
grafo son naturales y rápidas.

**Neptune Analytics**: variante para análisis de grafos a gran escala. También tiene integración con ML y, más recientemente, soporte para vector search
(casos de GenAI).

# Amazon Keyspaces (for Apache Cassandra)

Base de datos NoSQL wide-column, compatible con Apache Cassandra.

- **Modelo wide-column** (column families): filas que pueden tener columnas distintas, optimizado para escrituras masivas y escala.
- **Compatible con CQL** (Cassandra Query Language) → migras cargas Cassandra sin reescribir.
- **Serverless**: escala automáticamente, pago por uso, sin gestionar clusters (a diferencia de Cassandra autogestionado).
- **Cuándo elegirla**: cargas Cassandra existentes que quieres llevar a managed, o casos de wide-column a gran escala (datos de IoT, series temporales de alto volumen, logging, catálogos de equipos industriales).

# Amazon Timestream

Base de datos de series temporales (time series) totalmente managed y serverless.

- Diseñada específicamente para datos con timestamp que llegan de forma continua: métricas, telemetría, sensores IoT, logs de aplicaciones, datos de monitoreo.
- Optimizada para ingerir volúmenes enormes de puntos temporales y hacer consultas analíticas sobre el tiempo (agregaciones por ventanas, tendencias) de forma eficiente.
- Tiene gestión de ciclo de vida por tiers: datos recientes en memoria (consultas rápidas) y datos antiguos en storage magnético barato, automáticamente.
- Funciones analíticas específicas de series temporales (interpolación, suavizado, etc.).
- **Cuándo elegirla**: cualquier escenario de IoT / métricas / telemetría con datos indexados por tiempo. Es la respuesta natural cuando el escenario menciona sensores, mediciones periódicas o monitoreo temporal.

# Amazon MemoryDB for Redis

Base de datos in-memory durable, compatible con Redis.

- Guarda los datos en memoria (RAM) → latencia de microsegundos en lectura y milisegundos de un solo dígito en escritura.
- A diferencia de un caché puro, MemoryDB es durable: persiste los datos (usa un log transaccional multi-AZ), así que puede ser tu base de datos primaria, no solo una caché.
- **Cuándo elegirla**: cuando necesitas la velocidad de Redis pero con durabilidad como base de datos primaria (no solo acelerar otra base).

# Amazon ElastiCache

Servicio de caché en memoria managed, con dos motores: Redis y Memcached.

- Su propósito principal es cachear datos de acceso frecuente para descargar la base de datos principal (RDS/Aurora) y acelerar las lecturas a sub-milisegundos.
- A diferencia de MemoryDB, el enfoque clásico de ElastiCache es ser una caché (acelera otra base), aunque Redis puede persistir.
- Casos: caching de resultados de queries, session stores, leaderboards, rate limiting, pub/sub.
- ElastiCache vs MemoryDB: ElastiCache = caché delante de una base; MemoryDB = base de datos primaria durable en memoria.
- Redis vs Memcached (dato clásico): Redis es más rico (estructuras de datos, persistencia, replicación, pub/sub, alta disponibilidad); Memcached es más simple, multi-hilo, solo caching básico y escala horizontal sencilla.

# Amazon QLDB (Quantum Ledger Database)

Base de datos de tipo ledger (libro contable).

- Mantiene un registro de transacciones inmutable, transparente y verificable criptográficamente → un historial completo e imborrable de todos los cambios.
- **Cuándo elegirla**: cuando necesitas una pista de auditoría inmutable y verificable (registros financieros, cadena de suministro, historial de datos sensibles).

> Nota: AWS anunció que QLDB está en camino a descontinuarse, así que su relevancia en el examen es marginal; basta reconocer el concepto de "ledger inmutable".


| Servicio    | Tipo                               | Cuándo elegirlo                                               |
| ----------- | ---------------------------------- | ------------------------------------------------------------- |
| DocumentDB  | Documento (MongoDB-compatible)     | Documentos JSON con compatibilidad MongoDB                    |
| Neptune     | Grafo                              | Relaciones complejas: redes sociales, recomendaciones, fraude |
| Keyspaces   | Wide-column (Cassandra)            | Cargas Cassandra, wide-column a escala, IoT                   |
| Timestream  | Series temporales                  | IoT, métricas, telemetría, datos con timestamp                |
| MemoryDB    | In-memory durable (Redis)          | Base primaria en memoria con durabilidad                      |
| ElastiCache | Caché en memoria (Redis/Memcached) | Acelerar lecturas / descargar la base principal               |
| QLDB        | Ledger inmutable                   | Auditoría verificable e imborrable                            |


Lo que más importa para el DEA-C01

Para estas bases, el examen rara vez pide detalles profundos; lo clave es reconocer el escenario y mapearlo al servicio correcto:

- "Relaciones / conexiones complejas, recomendaciones, fraude" → Neptune (grafo).
- "Datos de sensores / IoT / métricas con timestamp" → Timestream (series temporales).
- "Compatibilidad con MongoDB" → DocumentDB.
- "Compatibilidad con Cassandra / wide-column" → Keyspaces.
- "Caché para acelerar lecturas / descargar la base" → ElastiCache.
- "Base en memoria pero durable como primaria" → MemoryDB.
- "Registro inmutable y verificable" → QLDB (ledger).