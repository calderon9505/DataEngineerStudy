# Amazon QuickSight

servicio de BI y visualización serverless y managed. Crea dashboards e informes interactivos desde el navegador. En el DEA-C01 aparece como el consumidor final de los datos del pipeline. Relevancia baja a moderada.

## SPICE vs Direct Query
- **SPICE**: motor en memoria de QuickSight. Los datos se importan a él, lo que da dashboards rápidos y no golpea la fuente en cada consulta. Se refresca de forma programada o por API.
- **Direct Query**: consulta la fuente en cada interacción. Los datos siempre están frescos, pero es más lento y carga la fuente.

## Fuentes de datos
Athena, Redshift, RDS/Aurora, S3 (con manifest file), OpenSearch y otras vía JDBC.

## Seguridad

- Row-level security (RLS) y column-level security (CLS) limitan qué datos ve cada usuario.
- Respeta los permisos de Lake Formation cuando la fuente los usa.
- QuickSight usa su propio rol de servicio, que hay que autorizar explícitamente para S3, Athena y Redshift. Error típico: "QuickSight no puede leer el bucket" suele ser un problema de permisos de ese rol.
- VPC connection para llegar de forma privada a fuentes dentro de una VPC.

> Otros: Amazon Q en QuickSight (consultas en lenguaje natural) y embedding (incrustar dashboards en aplicaciones propias). Basta con reconocerlos.

Posición en la arquitectura: `Fuentes → Kinesis/Glue/DMS → S3 + Glue Catalog → Athena / Redshift → QuickSight`
