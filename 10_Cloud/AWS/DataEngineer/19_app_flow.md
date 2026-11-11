# Amazon AppFlow

AppFlow es un servicio managed y serverless de integración que transfiere datos de forma segura entre aplicaciones SaaS (Salesforce, SAP, ServiceNow, Slack, Zendesk, Google Analytics, Marketo, etc.) y servicios de AWS, sin escribir código. 

El problema que resuelve: Traer datos de aplicaciones SaaS normalmente exige escribir y mantener integraciones propias: autenticación OAuth, paginación de APIs, límites de tasa, cambios de esquema, reintentos. AppFlow encapsula todo eso en conectores listos para usar.

### Conceptos clave:

- **Connector**: integración preconstruida con una aplicación (origen o destino). También existen custom connectors (vía SDK) para fuentes no soportadas.
- **Connection**: credenciales y configuración para acceder a la aplicación (OAuth, API keys). Los secretos se guardan cifrados.
- **Flow**: la unidad central. Define origen, destino, trigger, mapeo de campos y transformaciones.

### Orígenes y destinos:

- **Orígenes**: aplicaciones SaaS (Salesforce, SAP OData, ServiceNow, Zendesk, Slack, Google Analytics, Marketo, Datadog, etc.) y también S3.
- **Destinos**: S3, Redshift, Snowflake, EventBridge, Salesforce, Zendesk, entre otros.
- El patrón típico: `SaaS → AppFlow → S3 (data lake) o → Redshift, y luego Glue/Athena`.

### Tipos de trigger

| Trigger     | Comportamiento                                                                                                       |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| On demand   | Ejecución manual                                                                                                     |
| On schedule | Programado; permite cargas completas o incrementales (solo registros nuevos o modificados desde la última ejecución) |
| On event    | Se dispara cuando ocurre un evento en el SaaS (ej. se crea un registro en Salesforce). Es casi tiempo real           |

### Transformaciones y calidad

Operaciones simples integradas, sin código:
- Mapeo de campos entre origen y destino.
- Enmascarar campos (ej. ocultar PII).
- Filtrar registros por condiciones.
- Validar campos y cálculos simples (concatenar, operaciones aritméticas).
- Formatos de salida en S3: JSON, CSV o Parquet.

Para transformaciones complejas, el patrón es aterrizar en S3 y procesar con Glue.

### Seguridad

- Datos cifrados en tránsito y en reposo, con KMS (clave gestionada por AWS o customer managed key).
- Soporte de AWS PrivateLink para algunos conectores, de modo que el tráfico no pase por internet pública (ej. Salesforce, Snowflake, Zendesk).
- Control de acceso con IAM. El destino S3 requiere una bucket policy que permita a AppFlow escribir.
- Integra con Glue Data Catalog: puede registrar los datos entregados a S3 para consultarlos con Athena.

### Límites y consideraciones

- Es de integración SaaS, no un motor de ETL general ni de streaming masivo.
- Hay límites por flow (por ejemplo, tamaño de registro y volumen por ejecución), que varían por conector.
- Modelo de costos: pagas por flow ejecutado y por volumen de datos procesados.

Comparación con servicios cercanos

| Necesidad                                    | Servicio                   |
| -------------------------------------------- | -------------------------- |
| Datos desde aplicaciones SaaS sin código     | AppFlow                    |
| Replicar o migrar bases de datos (con CDC)   | DMS                        |
| Streaming de eventos de alto volumen         | Kinesis / MSK              |
| ETL con transformaciones complejas           | Glue                       |
| Transferir archivos grandes desde on-premise | DataSync / Transfer Family |
