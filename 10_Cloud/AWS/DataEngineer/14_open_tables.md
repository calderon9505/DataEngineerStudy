# Open Table Formats (Iceberg, Hudi, Delta Lake)

### El problema que resuelven
Un data lake tradicional en S3 es, en esencia, archivos sueltos (Parquet, CSV, JSON) organizados en prefixes. Eso es barato y escalable, pero tiene limitaciones serias comparado con una base de datos:

1. No hay transacciones ACID. Si un job está escribiendo archivos y otro lee al mismo tiempo, el lector puede ver datos a medias (archivos parciales) → resultados inconsistentes. No hay garantía de atomicidad.

2. No hay updates/deletes a nivel de registro. Los archivos en S3 son inmutables. Para "actualizar una fila" o "borrar una fila" (ej. por GDPR), tendrías que reescribir archivos/particiones enteras manualmente. Muy costoso y propenso a errores.

3. Schema evolution frágil. Cambiar el esquema (añadir/renombrar/borrar columnas) puede romper las consultas o requerir reprocesar todo.

4. No hay versionado ni time travel. No puedes consultar "cómo estaban los datos ayer" ni revertir un cambio erróneo.

5. Consistencia de particiones. Listar y gestionar millones de archivos/particiones en S3 es lento y propenso a inconsistencias.

Los open table formats resuelven todo esto añadiendo una capa de metadata transaccional encima de los archivos de datos en S3, dándole al data lake capacidades de base de datos. De ahí el término lakehouse: un data lake (barato, escalable, abierto) con features de data warehouse (ACID, updates, consistencia).

### Cómo funcionan

El truco común de los tres formatos: separan los datos (archivos Parquet) de una capa de metadata que rastrea qué archivos componen la tabla en cada momento.

> Tabla = archivos de datos (Parquet en S3) + capa de METADATA (qué archivos son válidos, en qué versión/snapshot)

En lugar de "la tabla son todos los archivos de este prefix", la metadata dice exactamente qué archivos forman la versión actual (y las versiones anteriores). Esto habilita:
- ACID: un cambio se "confirma" actualizando la metadata atómicamente → los lectores siempre ven una versión completa y consistente, nunca archivos a medias.
- Time travel: como la metadata guarda snapshots (versiones), puedes consultar cualquier versión histórica.
- Updates/deletes: se gestionan escribiendo nuevos archivos y actualizando la metadata para reflejar qué registros cambiaron, sin reescribir todo manualmente.
- Schema evolution: la metadata rastrea la evolución del esquema de forma segura.

### Capacidades clave (comunes a los tres)

- Transacciones ACID sobre S3.
- Upserts (MERGE), updates y deletes a nivel de registro/fila.
- Time travel / consulta de snapshots históricos y rollback.
- Schema evolution robusta (añadir, renombrar, reordenar columnas sin romper nada).
- Compaction: combinar archivos pequeños en grandes (resolver el "small files problem").
- Partition evolution (especialmente Iceberg): cambiar el esquema de particionamiento sin reescribir los datos históricos.

## Los tres formatos

### Apache Iceberg ⭐ (el más relevante hoy en AWS)
- Creado originalmente en Netflix, hoy es el estándar que AWS impulsa con más fuerza y el que tiene soporte nativo más amplio en el ecosistema AWS.
- Diseño de metadata muy robusto basado en **snapshots** y **manifiestos** que listan los archivos → excelente para tablas enormes, evita el costoso listado de S3.
- **Partition evolution y hidden partitioning**: puedes cambiar cómo se particiona sin reescribir datos, y los usuarios no necesitan conocer la columna de partición para beneficiarse del pruning.
- Fuerte **schema evolution** (incluso cambios complejos).
- Soporte nativo en AWS: Athena, Glue, EMR, Redshift, y el propio Glue Data Catalog lo tratan como ciudadano de primera clase. Es la apuesta recomendada de AWS.

### Apache Hudi (Hadoop Upserts Deletes and Incrementals)
- Creado en Uber, orientado especialmente a upserts eficientes y procesamiento incremental (streaming/CDC hacia el lake).
- Ofrece dos tipos de tabla:
    - Copy-on-Write (CoW): al actualizar, reescribe los archivos afectados → lecturas rápidas, escrituras más costosas. Bueno para cargas read-heavy.
    - Merge-on-Read (MoR): guarda los cambios en archivos delta y los combina al leer → escrituras rápidas, lecturas algo más costosas. Bueno para cargas write-heavy / baja latencia de ingesta.
- Fuerte en incremental queries (consultar solo lo que cambió desde un punto) → ideal para pipelines CDC.
- Soportado en AWS (EMR, Glue, Athena).

### Delta Lake
- Creado por Databricks, muy ligado a su ecosistema Spark.
- Usa un transaction log (el "Delta Log", archivos JSON ordenados) que registra cada cambio atómicamente.
- Muy maduro y popular, sobre todo donde se usa Databricks/Spark intensivamente.
- Soportado en AWS (EMR, Glue, Athena con cierto alcance), aunque la integración nativa más profunda en AWS es con Iceberg.

Comparación rápida

|                 | Iceberg                                                | Hudi                            | Delta Lake                                      |
| --------------- | ------------------------------------------------------ | ------------------------------- | ----------------------------------------------- |
| Origen          | Netflix                                                | Uber                            | Databricks                                      |
| Fortaleza       | Tablas masivas, partition evolution, estándar abierto  | Upserts e incremental/CDC       | Transaction log, ecosistema Spark/Databricks    |
| Tipos de tabla  | Un modelo (con copy/merge-on-read config)              | CoW y MoR                       | —                                               |
| Integración AWS | La más amplia y recomendada                            | Buena (EMR, Glue)               | Buena (más atada a Spark)                       |
| Caso ideal      | Lakehouse general en AWS                               | Ingesta incremental/CDC frecuente | Entornos Databricks/Spark                     |


Integración con AWS (lo que importa para el examen)

- Glue Data Catalog registra la metadata de estas tablas → los motores las descubren.
- Athena puede consultar (y con Iceberg, también hacer INSERT/UPDATE/DELETE/MERGE y time travel con SQL).
- Glue ETL (Spark) lee y escribe en los tres formatos.
- EMR (Spark/Hive/Presto) los soporta.
- Redshift puede consultar tablas Iceberg (vía Spectrum/integración).
- Lake Formation gobierna el acceso a tablas Iceberg.

El patrón general: cuando el escenario pide ACID, upserts/deletes a nivel de fila (p. ej. GDPR/"right to be
forgotten"), time travel, o CDC incremental sobre un data lake en S3 → la respuesta es un open table format, y en AWS normalmente Iceberg.

Caso de uso típico: borrado por cumplimiento (GDPR)

Un ejemplo que ilustra el valor: una ley exige borrar los datos de un usuario específico del data lake. Con archivos Parquet sueltos, tendrías que encontrar y reescribir todas las particiones que lo contienen — carísimo. Con Iceberg/Hudi/Delta, ejecutas un simple `DELETE FROM tabla WHERE user_id = X` y el formato gestiona el borrado a nivel de registro eficientemente.


---
---
### Si en mi empresa están empezando a implementar Databricks, pero a su vez se esta desarrollando un lakehouse con iceberg. Entrarían en conflicto?

La respuesta corta: no tienen por qué entrar en conflicto, pero hay matices que conviene entender para no tomar decisiones que luego cuesten revertir.

#### Por qué NO es un conflicto inherente

Existe la percepción de que "Databricks = Delta Lake" e "Iceberg = el competidor", porque históricamente Databricks creó y promovió Delta Lake como su formato nativo, mientras que Iceberg creció como alternativa abierta (Netflix, luego muy adoptado por AWS, Snowflake, etc.).

Pero esa rivalidad se ha diluido mucho, por un hecho clave: en 2024 Databricks adquirió Tabular, la empresa fundada por los creadores originales de Apache Iceberg. Esto marcó un giro estratégico de Databricks hacia la interoperabilidad con Iceberg, en lugar de competir contra él. Databricks declaró explícitamente que quiere converger los dos formatos y evitar que los clientes queden atrapados en un silo de formato.

En la práctica, hoy Databricks puede trabajar con Iceberg, así que ambos pueden coexistir.

#### Los mecanismos que permiten la coexistencia

Hay dos piezas que hacen que Databricks e Iceberg convivan:

1. Delta UniForm (Universal Format)

    Es una capacidad de Databricks/Delta que hace que una tabla escrita en Delta también exponga metadata de Iceberg automáticamente. Es decir, escribes una vez en Delta, y un motor que habla Iceberg (Athena, Trino, Snowflake, etc.) puede leerla como si fuera Iceberg, sin duplicar los datos. Resuelve gran parte del problema de interoperabilidad de lectura.

2. Unity Catalog con soporte Iceberg (REST Catalog)

    El catálogo de Databricks (Unity Catalog) ha incorporado soporte para el Iceberg REST Catalog, lo que permite que tablas gestionadas se lean/expongan vía el estándar de Iceberg, y que motores externos accedan a ellas.

#### Dónde SÍ debes poner atención (los matices)

Aunque pueden coexistir, no es automáticamente perfecto. Las fricciones reales que debes vigilar:

1. Lectura vs. escritura. La interoperabilidad suele ser más sólida en lectura que en escritura bidireccional completa. Que Databricks lea Iceberg y que motores externos lean Delta-vía-UniForm funciona bien; tener ambos escribiendo concurrentemente sobre la misma tabla es donde aparecen los problemas (dos "autoridades" transaccionales sobre los mismos archivos pueden pisarse). Conviene definir quién es el escritor (owner) de cada tabla.

2. El catálogo es la decisión más importante, más que el formato. El verdadero riesgo de conflicto no es tanto Delta vs Iceberg, sino qué catálogo es la fuente de verdad: ¿Unity Catalog (Databricks)? ¿Glue Data Catalog (AWS)? Si tienes dos catálogos gestionando las mismas tablas, ahí es donde surgen inconsistencias de permisos y metadata. Definir un catálogo autoritativo (o una federación clara entre ellos) es la decisión arquitectónica clave.

3. Features avanzadas no siempre se traducen 1:1. Cosas como time travel, ciertos tipos de deletes, o estadísticas pueden comportarse distinto entre un motor Databricks/Spark y un motor Iceberg externo. Las capacidades "de punta" de cada formato no siempre están disponibles cuando lo lees desde el otro lado.

4. Versiones y madurez. Todo esto evoluciona rápido; el nivel de soporte depende de las versiones de Databricks Runtime, de los motores AWS (Athena/Glue/EMR), etc. Hay que validar con las versiones concretas que uses.

#### Cómo lo plantearía en tu empresa

Para que convivan sanamente, las preguntas que vale la pena resolver con los equipos:

- ¿Quién escribe cada tabla? Define el motor "dueño" de escritura por dominio/tabla, y deja a los demás como lectores.
- ¿Cuál es el catálogo autoritativo? Decide si Unity Catalog, Glue, o una federación entre ambos es la fuente de verdad de metadata y permisos.
- ¿Para qué usan Databricks vs el lakehouse Iceberg? A veces la división natural es: Databricks para ciertos equipos de ML/ingeniería avanzada con Spark, e Iceberg como el estándar "neutral" de intercambio entre todos los consumidores (Athena, Redshift, otras herramientas). UniForm como puente.
- Evita la doble escritura sobre la misma tabla desde ambos mundos hasta tener muy claro el modelo de concurrencia.

En conclusión

No entran en conflicto por definición — Databricks ha apostado por la interoperabilidad con Iceberg (compra de Tabular, UniForm, Unity Catalog con Iceberg REST), así que un lakehouse Iceberg y Databricks pueden coexistir. El riesgo no está en "elegir el formato equivocado", sino en no definir claramente el catálogo autoritativo y quién escribe cada tabla. Si gobiernas eso, conviven bien; si dejas dos sistemas escribiendo y catalogando lo mismo sin coordinación, ahí sí aparecen inconsistencias.

Un consejo honesto: como este terreno cambia rápido, vale la pena validar los detalles de interoperabilidad (UniForm, Unity Catalog ↔ Glue, soporte de escritura) contra las versiones específicas y la documentación vigente antes de comprometer la arquitectura, porque lo que es cierto hoy puede ampliarse en pocos meses.