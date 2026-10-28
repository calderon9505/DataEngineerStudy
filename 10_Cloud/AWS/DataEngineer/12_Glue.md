# AWS Glue

Es el servicio de ETL (Extract, Transform, Load) serverless de AWS, pero con el tiempo se ha convertido en una plataforma de integración de datos completa. 

## Qué es Glue

Glue es un servicio serverless para descubrir, catalogar, limpiar, transformar y mover datos entre fuentes. "Serverless" es clave: no provisionas ni gestionas infraestructura; AWS levanta los recursos de cómputo cuando un job corre y los apaga al terminar. Pagas solo por el tiempo de ejecución.

El propósito es ser el pegamento ("glue") entre todas las fuentes y destinos de datos: tomar datos de S3, RDS, DynamoDB, streams, etc., transformarlos, y cargarlos en un data lake (S3), un warehouse (Redshift), u otro destino.

> Glue no es un solo producto, sino un conjunto de componentes.

## 1. AWS Glue Data Catalog ⭐ (el componente central)

El Data Catalog es un repositorio de metadatos centralizado y persistente. No almacena los datos en sí — almacena información sobre los datos (metadata): dónde están, su esquema (columnas y tipos), formatos, particiones, etc.

Estructura:
- **Databases**: agrupaciones lógicas de tablas.
- **Tables**: definiciones de metadatos de un dataset. Cada tabla describe el esquema, la ubicación (ej. una ruta en S3), el formato (Parquet, CSV, JSON...) y las particiones. La tabla apunta a los datos reales (que viven en S3, por ejemplo), pero no los contiene.

Por qué es tan importante: el Data Catalog es la fuente única de verdad del esquema para todo el ecosistema analítico de AWS. Es compatible con el Hive Metastore, y lo consumen:
- Athena (para saber qué consultar en S3),
- Redshift Spectrum (tablas externas),
- EMR (Spark/Hive),
- Glue ETL jobs,
- Lake Formation (gobernanza sobre el catálogo).

> Es decir, catalogas una vez y todos esos servicios usan la misma definición. Esto convierte a *S3 + Glue Data Catalog* en la base del data lake.

## 2. Glue Crawlers ⭐

Un Crawler es un proceso que escanea automáticamente una fuente de datos (típicamente S3, pero también JDBC, DynamoDB, etc.), infiere el esquema (descubre columnas, tipos, formato) y crea o actualiza las tablas en el Data Catalog.

Cómo funciona:
- Apuntas el crawler a una ubicación (ej. s3://mi-lake/ventas/).
- Usa classifiers para detectar el formato y estructura de los datos (hay classifiers integrados para CSV, JSON, Parquet, Avro, ORC, XML, logs, etc.; puedes crear custom classifiers con Grok, regex, etc.).
- Detecta particiones automáticamente (ej. la estructura year=2025/month=10/ la reconoce como particiones).
- Crea/actualiza la tabla en el catálogo con todo eso.
- Puede ejecutarse on-demand o programado (schedule), o dispararse por eventos.

> Punto importante: el crawler es la forma de mantener el catálogo sincronizado cuando llegan datos nuevos o el esquema cambia. Pero no siempre es necesario: si ya conoces el esquema, puedes crear las tablas manualmente o con los jobs, evitando el costo del crawler.

## 3. Glue ETL Jobs ⭐ (el motor de transformación)

El componente de ejecución de transformaciones. Un Glue job toma datos de una o varias fuentes, los transforma, y los escribe en un destino. Hay varios tipos de jobs, y esta distinción es muy preguntada:

- Spark jobs
    - Corren sobre Apache Spark (procesamiento distribuido en memoria).
    - Para transformaciones de grandes volúmenes en paralelo.
    - Puedes escribirlos en Python (PySpark) o Scala.

- Python Shell jobs
    - Ejecutan un script de Python simple (no Spark), en un solo nodo.
    - Para tareas ligeras que no necesitan procesamiento distribuido (pequeñas transformaciones, llamar APIs, orquestar cosas pequeñas).
    - Más baratos que levantar un cluster Spark.

- Streaming ETL jobs
    - Procesan datos en streaming (micro-batches) desde Kinesis Data Streams o MSK/Kafka, usando *Spark Structured Streaming*.
    - Para transformación casi en tiempo real.

- Ray jobs
    - Para cargas de cómputo en Python distribuido (más nuevo, menos central en el examen).

## 4. DynamicFrames (concepto propio de Glue)

Dentro de los Spark jobs, Glue introduce el DynamicFrame, su propia abstracción de datos (análoga al DataFrame de Spark, pero con diferencias clave):

- Un DataFrame de Spark requiere un esquema fijo conocido de antemano.
- Un DynamicFrame no requiere esquema previo: maneja datos semiestructurados y esquemas que cambian o son inconsistentes. Cada registro puede autodescribirse.
- Maneja ambigüedades de tipo con las "choice" types (ej. una columna que a veces es int y a veces string) sin romperse.
- Tiene transformaciones propias como ResolveChoice (resolver tipos ambiguos), DropNullFields, ApplyMapping (renombrar/retipar columnas), Relationalize (aplanar estructuras anidadas JSON en tablas relacionales).
- Se puede convertir a/desde DataFrame de Spark cuando necesitas la potencia de Spark SQL.

> La idea: el DynamicFrame es ideal para la realidad "sucia" de los datos de un data lake (esquemas inconsistentes), mientras que el DataFrame es mejor cuando el esquema es estable y quieres usar Spark SQL puro.

## 5. Glue Studio y las interfaces de desarrollo

Glue ofrece varias formas de crear jobs según tu perfil:

- Glue Studio: editor visual (drag-and-drop) para construir pipelines ETL sin escribir mucho código. Genera el código Spark por debajo. Bueno para construir visualmente y para quienes no son expertos en Spark.
- Notebooks: desarrollo interactivo (Jupyter) para construir y probar jobs.
- Script editor: escribir el código PySpark/Scala directamente.

## 6. AWS Glue DataBrew

DataBrew es una herramienta visual de preparación de datos orientada a analistas (sin código). Permite limpiar y normalizar datos con una interfaz point-and-click:

- Ofrece 250+ transformaciones predefinidas (eliminar nulos, estandarizar formatos, corregir valores, etc.).
- Genera "recipes" (recetas): conjuntos de transformaciones reutilizables.
- Hace profiling de datos (estadísticas, calidad, detección de anomalías).
- Diferencia con Glue ETL: DataBrew es no-code, visual, para preparación exploratoria por analistas; Glue ETL jobs son para pipelines productivos programáticos.

## 7. Glue Data Quality ⭐

Una capacidad cada vez más preguntada. Glue Data Quality permite definir y evaluar reglas de calidad sobre tus datos.

- Usa DQDL (Data Quality Definition Language) para expresar reglas (ej. "esta columna no debe tener nulos", "los valores deben estar en este rango", "debe ser única").
- Puede recomendar reglas automáticamente analizando los datos.
- Se integra en los pipelines: evalúa la calidad y puede fallar el job o alertar si los datos no cumplen.
- Funciona sobre el Data Catalog o dentro de los jobs ETL.
- Esencial para el concepto de gobernanza y confianza en los datos del data lake.

## 8. Glue Schema Registry

Gestiona y valida el esquema de datos en streaming. Permite registrar esquemas (Avro, JSON Schema, Protobuf) y garantizar que productores y consumidores de streams (Kinesis, MSK, Kafka, Flink) usen esquemas compatibles, controlando la evolución del esquema (que un cambio no rompa a los consumidores).

## 9. Orquestación: Workflows y Triggers

Glue tiene su propia orquestación interna:

- **Triggers**: inician jobs/crawlers. Pueden ser on-demand, scheduled (cron), o event-based/conditional (cuando otro job termina, con éxito/fallo).
- **Workflows**: orquestan múltiples crawlers y jobs como un pipeline con dependencias (ejecutar crawler → job de transformación → job de carga, en orden).

> Nota: para orquestación más compleja o multi-servicio, el examen suele preferir Step Functions o MWAA (Airflow), pero los workflows de Glue sirven para pipelines contenidos dentro de Glue.

## 10. Glue Connections

Definiciones reutilizables de conexión a fuentes de datos (credenciales, parámetros de red). Permiten que los jobs/crawlers accedan a RDS, Redshift, JDBC, Kafka, etc. Para fuentes en una VPC, Glue usa estas conexiones para acceder de forma privada.

## 11. Concepto clave de costos: DPUs

Glue factura su cómputo en DPUs (Data Processing Units). Una DPU es una unidad de capacidad (una combinación de CPU y memoria — 4 vCPU y 16 GB RAM). Pagas por DPU-hora mientras el job corre (facturado por segundo, con un mínimo).

- Más DPUs = más paralelismo = más rápido, pero más costo.
- Auto Scaling: Glue puede ajustar el número de workers dinámicamente según la carga del job.

## 12. Glue Flex

Una opción de ejecución de menor costo para jobs no urgentes/no sensibles al tiempo (ETL batch que puede tolerar tiempos de inicio variables). Usa capacidad de cómputo "sobrante" de AWS a cambio de un precio menor. Para jobs donde la latencia de ejecución no importa.

## 13. Glue Job Bookmarks ⭐

Los Job Bookmarks son un mecanismo para procesar solo datos nuevos en ejecuciones sucesivas, evitando reprocesar lo ya procesado.

- Glue "recuerda" (marca) qué datos ya procesó en la última ejecución (basándose en timestamps, keys, etc.).
- En la siguiente ejecución, procesa solo lo nuevo/cambiado desde el último bookmark.
- Esto habilita procesamiento incremental eficiente: por ejemplo, si cada día llegan archivos nuevos a S3, el job solo procesa los del día, no todo el histórico.
- Evita duplicados y ahorra tiempo/costo.

> Es el equivalente conceptual a lo que CDC hace en migraciones: solo lo incremental.

## Cómo encaja todo (flujo típico)

Un pipeline de data lake clásico con Glue:

1. Datos llegan a S3 (raw)
2. CRAWLER escanea → crea/actualiza tabla en el DATA CATALOG
3. GLUE ETL JOB (Spark) lee desde el catálogo, transforma (limpia, convierte a Parquet, particiona, aplica Data Quality) → con JOB BOOKMARKS procesa solo lo nuevo
4. Escribe resultado en S3 (curated/processed) o Redshift
5. Otro CRAWLER cataloga la salida
6. ATHENA / REDSHIFT SPECTRUM consultan vía el mismo catálogo (orquestado por WORKFLOWS, Step Functions o Airflow)

## Glue vs otras opciones de procesamiento (criterio de examen)

- **Glue vs EMR**: Glue es serverless, más simple, sin gestionar clusters, ideal para ETL que no requiere control fino del entorno Spark. EMR da control total del cluster (Spark, Hive, Presto, HBase...), mejor para cargas muy grandes/personalizadas o si ya tienes expertise en Hadoop/Spark y quieres optimizar costos con instancias. `Glue = conveniencia`; `EMR = control y flexibilidad`.
- **Glue vs Lambda**: para transformaciones muy ligeras y rápidas event-driven, Lambda puede bastar; para ETL real con volumen y Spark, Glue.
- **Glue Python Shell vs Spark job**: tareas ligeras de un nodo → Python Shell (más barato); volumen distribuido → Spark.

## Seguridad e integración

- IAM roles para que los jobs accedan a las fuentes (el patrón de roles que hemos visto).
- Lake Formation se integra encima del Data Catalog para control de acceso granular (column/row-level).
- Cifrado con KMS, conexiones privadas vía VPC.
- Integración nativa con S3, Redshift, RDS, DynamoDB, Kinesis, MSK, Athena, EMR.

## Glue Development Endpoints 👴

Desarrollar un job de ETL con Spark tiene una fricción: el código Spark que procesa datos distribuidos es difícil de escribir "de una sola vez" sin equivocarse. Si tuvieras que, por cada pequeño cambio, lanzar el job completo (que arranca un cluster, carga los datos, ejecuta todo), esperar varios minutos y ver si funcionó, el ciclo de desarrollo sería lentísimo y caro.

El Development Endpoint elimina esa fricción dándote un cluster Spark ya encendido y persistente al que te conectas y
donde pruebas tu código pieza por pieza, de forma interactiva, viendo resultados al instante. Es como tener un
"laboratorio Spark" siempre listo mientras desarrollas.

Cómo funciona:

1. Provisionas el dev endpoint, indicando cuántas DPUs quieres (la capacidad de cómputo Spark).
2. Glue levanta ese entorno Spark y lo mantiene activo.
3. Te conectas a él desde una herramienta interactiva (un notebook, un IDE como PyCharm/VS Code, o una terminal).
4. Escribes y ejecutas fragmentos de código (PySpark o Scala) que corren en el entorno Spark del endpoint, contra tus datos reales (ej. en S3).
5. Iteras hasta que la lógica funciona, y entonces guardas el script como un job de Glue productivo.
6. Importante: cuando terminas, debes eliminar el endpoint, porque mientras exista sigue facturando por DPU-hora, lo uses o no.

### Apache Zeppelin

Un notebook web de código abierto, nacido en el ecosistema de big data, con integración fuerte con Spark. Fue históricamente de los más usados para trabajar con Spark/Scala. Puedes correrlo localmente o en un servidor y conectarlo al dev endpoint. Soporta visualizaciones de datos integradas.

### Jupyter

El notebook de código abierto más popular en general, estándar de facto en Python/data science. Funciona con muchos lenguajes (el nombre viene de Julia, Python, R). En AWS, los SageMaker notebooks están basados en Jupyter, y también puedes conectarlos a un dev endpoint.

> En ambos casos, el notebook es solo la interfaz donde escribes; el cómputo real (Spark) ocurre en el dev endpoint al que está conectado. El notebook manda las celdas al endpoint, el endpoint las ejecuta en Spark y devuelve el resultado.

### En el contexto de AWS:

- Jupyter es el más presente: los SageMaker notebooks se basan en Jupyter, y las Glue Interactive Sessions / Glue Studio notebooks usan interfaz Jupyter. Es el que más te encontrarás.
- Zeppelin aparece sobre todo en el ecosistema EMR (donde Spark es central) y como opción histórica para conectarse a los dev endpoints de Glue. También es la base de los notebooks de Kinesis Data Analytics Studio (Flink).

### La desventaja central: el modelo de costos

Insisto en esto porque es lo más preguntable: un dev endpoint cobra por todo el tiempo que está provisionado, independientemente de si lo estás usando activamente. Como mantiene un cluster Spark "encendido" esperando tus comandos, cada hora cuenta. Si lo olvidas encendido un fin de semana, pagas todo ese tiempo. Por eso la recomendación es crearlo, usarlo, y eliminarlo al terminar.

## Interactive Sessions

Justamente por ese modelo de costos, AWS introdujo las Glue Interactive Sessions como evolución:
- Son serverless: no mantienes un cluster provisionado permanentemente.
- Se inician bajo demanda cuando ejecutas código y se apagan tras un tiempo de inactividad (timeout configurable).
- Pagas solo por el tiempo real de uso, no por tenerlo encendido.
- Se integran directamente con los notebooks de Glue Studio y con Jupyter/VS Code.

Dan la misma experiencia interactiva de desarrollo pero sin el riesgo de costos de un endpoint olvidado. Por eso, en arquitecturas y exámenes modernos, las Interactive Sessions son la opción recomendada, y los dev endpoints quedan como la forma "clásica".


# Hive y el Hive Metastore

## ¿Qué es Apache Hive?

Hive es una herramienta del ecosistema Hadoop, creada originalmente por Facebook, que resolvió un problema concreto: en los primeros días del big data, para procesar datos en Hadoop tenías que escribir programas MapReduce en Java — complejo y tedioso.

Hive introdujo la idea de poder consultar esos datos con SQL (o algo muy parecido, llamado HiveQL) en lugar de programar MapReduce. Es decir, Hive te deja tratar archivos que viven en un sistema de archivos distribuido (HDFS, o S3) como si fueran tablas de una base de datos, y consultarlos con SQL.

La clave conceptual: los datos siguen siendo archivos (CSV, Parquet, etc.) en el almacenamiento. Hive solo pone una "capa de tabla" por encima para poder consultarlos con SQL. Esto se conoce como "schema-on-read": el archivo no cambia; le aplicas una estructura de tabla al momento de leerlo.

## ¿Qué es el Hive Metastore?

Aquí está el punto central. Para que Hive pueda tratar un archivo como una tabla, necesita saber:
- ¿Qué columnas tiene y de qué tipo?
- ¿Dónde están los archivos (qué ruta en HDFS/S3)?
- ¿En qué formato están (CSV, Parquet...)?
- ¿Cómo están particionados?

Toda esa información es metadata. El Hive Metastore es el repositorio donde se guarda esa metadata. Es, esencialmente, un catálogo que mapea "nombre de tabla → esquema + ubicación + formato de los archivos reales".

```
Hive Metastore (metadata)              Datos reales (archivos)
─────────────────────────              ──────────────────────
tabla "ventas":                        s3://lake/ventas/
- columnas: fecha, monto        ───►   ventas_2025.parquet
- ubicación: s3://lake/ventas/         ventas_2024.parquet
- formato: Parquet    
```

El Metastore no guarda los datos, solo la descripción de cómo interpretarlos. ¿Te suena familiar? Es exactamente lo que hace el Glue Data Catalog.

El Hive Metastore se volvió un estándar de facto

Aquí está lo importante: con el tiempo, el Hive Metastore dejó de ser "solo de Hive". Se convirtió en el estándar de la industria para catálogos de metadata en big data. Muchísimas herramientas lo adoptaron como la forma estándar de saber "qué tablas existen y dónde están los datos":

- Apache Spark puede usar un Hive Metastore.
- Presto / Trino (motores de consulta) lo usan.
- Apache Hive mismo, obviamente.
- Herramientas en EMR, etc.

### Qué significa "el Glue Data Catalog es compatible con el Hive Metastore"

Ahora la frase cobra sentido. Significa que el Glue Data Catalog puede funcionar como un Hive Metastore — habla ese "idioma estándar". Las implicaciones prácticas:

1. Drop-in replacement: cualquier herramienta que espere un Hive Metastore (Spark, Presto, Hive en EMR, etc.) puede usar el Glue Data Catalog en su lugar, sin cambios significativos. Glue se presenta como si fuera un Hive Metastore.

2. Managed y serverless: en vez de tener que instalar, operar y mantener tu propio Hive Metastore (que tradicionalmente corre sobre una base de datos relacional que tú administras, normalmente en un cluster Hadoop/EMR), AWS te lo da managed y serverless con el Glue Data Catalog. Un dolor de cabeza operativo menos.

3. Migración fácil: si vienes de un entorno Hadoop on-premise con un Hive Metastore, puedes migrar esa metadata al Glue Data Catalog.

4. Interoperabilidad total en AWS: como EMR (que corre Spark/Hive/Presto) entiende Hive Metastore, puede usar directamente el Glue Data Catalog — por eso Athena, Redshift Spectrum, EMR y Glue ETL comparten el mismo catálogo. Todos hablan el mismo idioma de metadata.

Por qué esto importa para el examen

El mensaje de fondo: el Glue Data Catalog es un Hive Metastore managed y serverless, lo que lo convierte en el catálogo universal del data lake en AWS. Esa compatibilidad es la razón técnica por la que un solo catálogo sirve a tantos servicios distintos. Cuando el examen menciona migrar un Hive Metastore, o compartir metadata entre EMR y Athena, la respuesta suele girar en torno al Glue Data Catalog.

# Glue Data Catalog — profundización

## Estructura completa y jerarquía

El catálogo tiene más niveles de los que mencioné:

- **Catalog**: el contenedor de nivel superior, uno por cuenta de AWS y por región. Se identifica por el Catalog ID, que normalmente es el ID de tu cuenta. Este detalle importa para el acceso cross-account (puedes referenciar el catálogo de otra cuenta por su Catalog ID).
- **Databases**: agrupaciones lógicas de tablas dentro del catálogo.
- **Tables**: las definiciones de metadata que ya vimos.
- Connections, Crawlers, Classifiers, Schema Registry también viven dentro del catálogo.

### Las tablas por dentro: 

Una tabla del catálogo guarda más de lo que parece:

- **Schema**: columnas, tipos de datos, comentarios.
- **Location**: la ruta de los datos (ej. s3://...).
- **Input/Output format y SerDe (Serializer/Deserializer)**: cómo leer/escribir el formato físico (esto viene directo del mundo Hive — el SerDe le dice al motor cómo interpretar los bytes de un CSV, JSON, Parquet, etc.).
- **Table properties**: pares clave-valor con metadata adicional (número de filas, tamaño, parámetros de clasificación, etc.).
- **Partition keys**: las columnas por las que está particionada.

## Gestión de particiones

Las particiones son uno de los puntos más relevantes del catálogo para performance, porque permiten el **partition pruning** (que Athena/Spectrum lean solo las particiones necesarias, reduciendo datos escaneados y costo).

El reto: en un data lake con millones de archivos, puedes tener cientos de miles de particiones, y gestionarlas se
vuelve un problema. Hay varias herramientas:

Cómo se registran las particiones
- **Crawlers**: detectan y registran particiones automáticamente.
- **MSCK REPAIR TABLE** (desde Athena): escanea S3 y añade las particiones nuevas al catálogo.
- **ALTER TABLE ADD PARTITION**: agregar particiones manualmente.
- Los ETL jobs pueden escribir particiones y registrarlas.

## Partition Indexes

Cuando una tabla tiene muchísimas particiones, filtrarlas se vuelve lento (el catálogo tiene que evaluar todas). Un partition index acelera la recuperación de particiones específicas al consultar, evitando escanear toda la lista de particiones. Mejora el performance de las queries con filtros de partición sobre tablas enormes.

## Partition Projection

En lugar de almacenar cada partición en el catálogo, partition projection le dice a Athena cómo calcular/proyectar las particiones a partir de un patrón (ej. "las fechas van del 2020 al 2026, en formato year=YYYY/month=MM"). Athena deduce qué particiones existen sin consultarlas en el catálogo.

Ventajas:
- Elimina el cuello de botella de gestionar/consultar millones de particiones en el catálogo.
- No necesitas crawlers ni MSCK REPAIR para mantener las particiones al día.
- Ideal para tablas con patrones de partición predecibles y muy alta cardinalidad (sobre todo fechas).

Lo veremos de nuevo en Athena, pero conceptualmente vive en la definición de la tabla del catálogo.

## Schema Versioning

El catálogo mantiene versiones de las definiciones de tabla. Cuando un crawler o un proceso actualiza el esquema de una tabla, se crea una nueva versión, y puedes comparar versiones y revertir a una versión anterior si un cambio rompió algo.

Esto conecta con cómo el crawler maneja los cambios de esquema (schema evolution): puedes configurar qué hace cuando detecta cambios — actualizar la tabla, ignorar, o añadir columnas nuevas pero no borrar las que desaparecieron, etc. (políticas de actualización/eliminación del crawler).

## Column Statistics

El catálogo puede almacenar estadísticas de las tablas (número de valores distintos, nulos, min/max, etc.). Estas estadísticas las usan los motores de consulta (Athena, Redshift Spectrum) para que su optimizador de consultas (cost-based optimizer) genere mejores planes de ejecución → consultas más rápidas. Generar estadísticas es un paso de optimización que conviene conocer.

## Seguridad y control de acceso

El acceso al catálogo se puede controlar de tres formas, y esto es muy de examen:

1. **IAM policies**: permisos sobre las acciones de Glue (glue:GetTable, etc.).
2. **Lake Formation**: control de acceso granular (a nivel de database, tabla, columna, fila y celda) sobre los recursos del catálogo. Lake Formation se pone "encima" del Data Catalog y gestiona los permisos de forma centralizada, en vez de policies IAM dispersas. Esta es la evolución recomendada para gobernanza de data lakes.
3. **Resource-based policies del catálogo**: policies basadas en recurso sobre el propio catálogo, usadas sobre todo para acceso cross-account.

También: cifrado de la metadata en reposo con KMS, y cifrado de las connection passwords.

## Acceso cross-account

El catálogo se puede compartir entre cuentas (usando el Catalog ID de la otra cuenta + resource policies o Lake Formation). Esto permite arquitecturas donde una cuenta central (data lake) comparte su catálogo con cuentas consumidoras.

## Soporte para formatos de data lake transaccionales

Un tema moderno y creciente en el examen: el Data Catalog soporta los open table formats transaccionales:

- Apache Iceberg
- Apache Hudi
- Delta Lake

Estos formatos añaden capacidades tipo base de datos a un data lake en S3: transacciones ACID, time travel (consultar versiones históricas), upserts/deletes a nivel de registro, y schema evolution robusta. El catálogo mantiene la metadata de estas tablas para que Athena, EMR, Spectrum las consulten. Es la base del concepto "data lakehouse".

## El catálogo y la federación

Más recientemente, el Data Catalog puede actuar como un catálogo más amplio con federation hacia otros metastores/fuentes, y se integra con Amazon SageMaker Lakehouse y Amazon DataZone para catálogos de datos a nivel organización.

## Costos

El modelo de precios del catálogo es sencillo:
- Pagas por objetos almacenados por encima del primer millón (el primer millón de objetos es gratis).
- Pagas por requests al catálogo por encima del primer millón mensual.
- Los crawlers y los ETL jobs se facturan aparte (por DPU-hora / tiempo de crawler), no como parte del catálogo en sí. En la práctica, el catálogo en sí es barato; lo que cuesta es el cómputo (crawlers/jobs).

## Buenas prácticas que conviene recordar

- No siempre necesitas crawlers: si conoces el esquema, puedes crear tablas directamente o desde los jobs → ahorras el costo del crawler y evitas que un crawler "redescubra" mal el esquema.
- Para tablas con particiones masivas y predecibles → partition projection en lugar de registrar todas.
- Para tablas grandes con muchas particiones que sí registras → partition indexes.
- Genera column statistics para acelerar consultas en Athena/Spectrum.
- Usa Lake Formation para gobernanza granular en lugar de solo IAM.