# AWS Lake Formation

Lake Formation es el servicio de AWS para construir, asegurar y gobernar data lakes de forma centralizada.

### El problema que resuelve

Construir un data lake en S3 "a mano" implica una enorme complejidad de seguridad:

- Los datos están repartidos en muchos buckets/prefixes de S3.
- Controlar quién accede a qué requiere gestionar decenas de bucket policies y IAM policies dispersas, difíciles de auditar.
- El control de S3 es a nivel de objeto/prefix — no puedes decir fácilmente "este usuario puede ver estas columnas pero no aquellas", o "solo las filas de su región".
- Montar el lake (crawlear, catalogar, transformar) requiere orquestar muchos servicios manualmente.

Lake Formation resuelve esto poniendo una capa de gobernanza centralizada encima de S3 y del Glue Data Catalog, con un modelo de permisos granular y simple (estilo base de datos), en un solo lugar.

### La idea central: permisos estilo base de datos sobre el data lake

El concepto más importante: Lake Formation te permite gestionar el acceso al data lake con permisos tipo GRANT/REVOKE (como en SQL), a nivel de database, tabla, columna, fila y celda, en lugar de lidiar con bucket policies de S3.

En vez de pensar "quién puede leer este prefix de S3", piensas "quién puede hacer SELECT sobre estas columnas de esta tabla". Lake Formation traduce eso por debajo al acceso físico en S3. Esto es mucho más fino y manejable que lo que S3/IAM permiten por sí solos.

## Componentes y conceptos

### Data Lake Administrator

Un rol/usuario designado como administrador del data lake, que tiene permisos para configurar Lake Formation, registrar ubicaciones, y otorgar/revocar permisos a otros. Es el punto de control central.

### Registrar ubicaciones en S3 (data lake locations)

El paso fundamental: registras ubicaciones de S3 (buckets/prefixes) en Lake Formation. Al hacerlo, Lake Formation pasa a gestionar el acceso a esos datos.

El mecanismo clave aquí es que Lake Formation usa un service role para acceder a los datos en S3 en nombre de los usuarios. Cuando registras una ubicación, Lake Formation asume ese rol y "vende" credenciales temporales (credential vending) a los motores de consulta según los permisos que definiste. Esto conecta con todo lo que vimos de roles/STS: el usuario final no accede a S3 directamente con sus credenciales, sino que Lake Formation media el acceso.

## Integración con el Glue Data Catalog

Lake Formation no tiene su propio catálogo — usa el Glue Data Catalog. Los permisos de Lake Formation se aplican sobre las databases y tables de ese catálogo. Son, esencialmente, el mismo catálogo visto desde dos ángulos: Glue lo gestiona técnicamente, Lake Formation lo gobierna en acceso.

## El modelo de permisos

Lake Formation introduce su propio sistema de permisos que trabaja junto con IAM. Esta dualidad es central y confunde, así que la detallo.

### Dos capas que deben alinearse

Para que alguien acceda a datos vía Lake Formation, se necesitan dos cosas:
1. Permisos IAM: permiso para usar las acciones de los servicios (ej. llamar a la API de Glue/Athena/Lake Formation).
2. Permisos de Lake Formation: permiso sobre los recursos de datos (database/tabla/columna/fila).

Ambos deben permitir el acceso. IAM controla "qué APIs puedes llamar"; Lake Formation controla "qué datos puedes ver".

### Niveles de granularidad

Los permisos de Lake Formation se otorgan a distintos niveles:
- **Database-level**: acceso a todas las tablas de una database.
- **Table-level**: acceso a una tabla específica.
- **Column-level** (column-level security): ver solo ciertas columnas de una tabla (ej. ocultar columnas con PII).
- **Row-level** (row-level security): ver solo ciertas filas según una condición (ej. solo filas de tu región).
- **Cell-level**: combinación de restricciones de fila y columna.

### Data Filters

La forma de implementar seguridad a nivel de fila y columna es mediante Data Filters: defines un filtro que especifica qué columnas son visibles y/o una condición de filtrado de filas, y lo asocias a una tabla al otorgar el permiso. Esto habilita el fine-grained access control real sobre el data lake.

### LF-TBAC (Tag-Based Access Control)

Un mecanismo muy relevante y moderno. En vez de otorgar permisos tabla por tabla (que no escala con miles de tablas), LF-Tags (Lake Formation Tags) permiten:

- Asignar etiquetas (pares clave-valor, ej. clasificacion=confidencial, departamento=finanzas) a databases, tablas y columnas.
- Otorgar permisos sobre las etiquetas, no sobre recursos individuales (ej. "el grupo de finanzas puede acceder a todo lo etiquetado departamento=finanzas").
- A medida que creas recursos nuevos y les pones las etiquetas correctas, heredan automáticamente los permisos → escala a data lakes grandes sin gestionar grants uno por uno.

Es la forma recomendada de gestionar permisos a escala. Es análogo conceptualmente al ABAC (attribute-based access control).

### Cómo lo aplican los motores de consulta

Lake Formation se integra con los motores analíticos para imponer sus permisos:
- **Athena**: al consultar, Athena respeta los permisos LF (solo ves las columnas/filas permitidas).
- **Redshift Spectrum**: ídem para tablas externas.
- **EMR (Spark), Glue ETL jobs, QuickSight**: también se integran.

El flujo: el motor pide acceso → Lake Formation verifica los permisos → vende credenciales temporales limitadas a lo
permitido → el motor lee de S3 solo lo autorizado, aplicando los data filters. El usuario nunca toca S3 directamente.

### Cross-account data sharing

Lake Formation facilita compartir datos del catálogo entre cuentas de forma gobernada:
- Una cuenta productora otorga permisos LF a una cuenta consumidora sobre databases/tablas (o vía LF-Tags).
- Se integra con AWS RAM (Resource Access Manager) para compartir los recursos.
- La cuenta consumidora ve esas tablas en su propio catálogo y las consulta con Athena/Spectrum, respetando los permisos.

Esto es mucho más limpio que gestionar bucket policies cross-account manualmente, y es la base de arquitecturas tipo data mesh.

## Blueprints

Un Blueprint es una plantilla predefinida que automatiza la ingesta de datos hacia un data lake en S3.

En vez de construir manualmente el pipeline de ingesta, eliges un blueprint y Lake Formation genera por ti un workflow de AWS Glue (crawlers, jobs y triggers) que carga los datos al data lake, los cataloga y los organiza.

Hay tipos de blueprint según la fuente:

- **Database blueprint**: ingiere datos desde una base de datos relacional (vía JDBC — RDS, bases on-premise). Soporta:
    - Carga completa (bulk load): toda la fuente
    - Carga incremental (incremental load): solo los registros nuevos/cambiados desde la última ejecución, usando columnas marcadoras
- **Log file blueprint**: ingiere archivos de log desde fuentes como CloudTrail, CloudFront, ELB logs, etc.

Qué genera por debajo

El blueprint produce un Glue workflow completo:
- Crawlers que descubren el esquema y lo registran en el Glue Data Catalog.
- Jobs de Glue que transforman y cargan los datos a S3.
- Triggers que orquestan el orden de ejecución.

> Es decir, el blueprint es un atajo de automatización para montar pipelines de ingesta al data lake sin construirlos pieza por pieza.

## Hybrid Access Mode

Un concepto práctico: Lake Formation permite un modo híbrido donde una ubicación puede ser accedida tanto por permisos de Lake Formation como por los permisos IAM/S3 tradicionales, según el principal. Esto facilita la migración gradual de un lake gestionado con IAM hacia el modelo de Lake Formation sin romper los accesos existentes.

## Lake Formation vs IAM/bucket policies

- Solo IAM + bucket policies: control a nivel de bucket/prefix/objeto, disperso, sin granularidad de columna/fila. Suficiente para casos simples.
- Lake Formation: control centralizado y granular (database/tabla/columna/fila/celda), con TBAC para escala, credential vending y cross-account gobernado. La respuesta cuando el escenario pide column/row-level security, gobernanza centralizada, o compartir datos del lake entre cuentas/equipos de forma controlada.

## Seguridad y auditoría

- Todo el acceso mediado por Lake Formation queda registrado (integración con CloudTrail) → auditoría de quién accedió a qué.
- Centraliza la gestión, reduciendo el riesgo de exposiciones accidentales por policies mal configuradas.

## Governed Tables (deprecated)

Tipo especial de tabla de Lake Formation que añadía capacidades de base de datos transaccional a datos en S3 — transacciones ACID (lecturas/escrituras concurrentes consistentes), automatic compaction  (combina archivos pequeños para resolver el "small files problem"), time travel (consultar versiones históricas) y row-level security integrada.

Han sido efectivamente superadas y ya no son la opción recomendada; AWS adoptó los **open table formats** (sobre todo Apache Iceberg, también Hudi y Delta Lake), que ofrecen las mismas capacidades (ACID, time travel, compaction, upserts/deletes a nivel de registro) pero de forma abierta, portable e interoperable entre motores (Athena, Glue, EMR, Redshift, Spark). Por tanto, si un escenario pide ACID / upserts / time travel en un data lake sobre S3, la respuesta moderna es Iceberg, no Governed Tables.


---
---

# AWS RAM (Resource Access Manager)

AWS RAM es un servicio que permite compartir recursos de AWS entre cuentas (o dentro de una organización) de forma segura y centralizada, sin tener que duplicarlos ni gestionar roles cross-account complejos para cada caso.

La idea central: en vez de crear copias de un recurso en cada cuenta, lo creas una vez y lo compartes con otras cuentas, que lo usan como si fuera propio.

Cómo funciona:
- Creas un Resource Share: defines qué recursos compartes, con quién (cuentas específicas, una OU, o toda tu organización en AWS Organizations) y con qué permisos.
- La cuenta receptora acepta el share (automático si están en la misma organización) y accede al recurso.

Recursos típicos que se comparten con RAM:
- Subnets de VPC (varias cuentas usando la misma red).
- Transit Gateways, Route 53 Resolver rules.
- Lake Formation: los permisos de databases/tablas del catálogo.
- Licencias, portfolios de Service Catalog, etc.

---
---

# Data Mesh

Un data mesh es un enfoque arquitectónico y organizacional para gestionar datos a gran escala en organizaciones grandes. No es un servicio de AWS, sino un paradigma de diseño. Surge como alternativa a los modelos centralizados tradicionales (un único data lake/warehouse gigante gestionado por un solo equipo central).

El problema que ataca: En el modelo centralizado clásico, un equipo central de datos es responsable de ingerir, procesar y servir todos los datos de la empresa. A escala, esto se convierte en un cuello de botella: el equipo central no conoce a fondo cada dominio de negocio, se satura de peticiones y la calidad sufre.

### Los principios del data mesh

El data mesh descentraliza la responsabilidad de los datos. Sus ideas clave:

1. **Domain ownership** (propiedad por dominio): cada dominio de negocio (ventas, marketing, logística...) es dueño de sus propios datos y responsable de producirlos y mantenerlos. Quien mejor conoce los datos los gestiona.

2. **Data as a product** (dato como producto): cada dominio expone sus datos como un "producto" bien documentado, confiable, descubrible y fácil de consumir por otros. Se trata a los datos con la misma seriedad que un producto para clientes.

3. **Self-service infrastructure** (plataforma self-service): existe una plataforma común que permite a cada dominio gestionar sus datos de forma autónoma, sin depender del equipo central para todo.

4. **Federated governance** (gobernanza federada): reglas de gobernanza comunes (seguridad, estándares, interoperabilidad) aplicadas de forma federada, para que los datos descentralizados sigan siendo consistentes e interoperables.

### Cómo encaja en AWS

AWS implementa patrones de data mesh combinando:
- Lake Formation + Glue Data Catalog → cada dominio/cuenta gobierna y comparte sus datos.
- AWS RAM → para compartir los datos entre cuentas/dominios.
- Cuentas separadas por dominio (cada equipo con su cuenta productora).
- Amazon DataZone → servicio más reciente de AWS pensado específicamente para catalogar, descubrir y gobernar datos en un modelo tipo data mesh a nivel organización.

El patrón típico: una cuenta central mantiene el catálogo gobernado, y cuentas productoras (dominios) comparten sus datasets vía Lake Formation/RAM con cuentas consumidoras, todo descubrible y con permisos federados.