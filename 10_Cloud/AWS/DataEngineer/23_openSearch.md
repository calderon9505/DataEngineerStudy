# Amazon OpenSearch Service

OpenSearch Service es el servicio managed de AWS para ejecutar OpenSearch (fork open-source de **Elasticsearch**): un motor de búsqueda y analítica sobre texto y logs.

Es un motor de búsqueda distribuido basado en Apache Lucene. Guarda documentos JSON y los indexa para que puedas buscar y agregar en milisegundos. Casos típicos:

- Búsqueda de texto completo (catálogos, sitios, documentos), con relevancia, tolerancia a errores tipográficos y autocompletado.
- Log y observabilidad: centralizar logs de aplicaciones y analizarlos casi en tiempo real.
- Analítica de eventos / clickstream y monitoreo de seguridad (SIEM).
- Búsqueda vectorial / semántica (k-NN), cada vez más usada en aplicaciones de GenAI y RAG.

> Es un motor de búsqueda y analítica, no una base transaccional: no ofrece ACID, ni joins relacionales reales.

## Conceptos clave

| Concepto                      | Equivalente / significado                                                  |
| ----------------------------- | -------------------------------------------------------------------------- |
| Document                      | Registro JSON (como una fila)                                              |
| Index                         | Colección de documentos (como una tabla)                                   |
| Shard                         | Fragmento de un index; unidad de paralelismo                               |
| Primary shard / replica shard | Datos originales / copias para disponibilidad y lecturas                   |
| Mapping                       | Esquema: tipos de campos del index                                         |
| Inverted index                | Estructura que mapea términos a documentos; lo que hace rápida la búsqueda |

Los shards primarios se definen al crear el index y no se pueden cambiar fácilmente después (requiere reindexar). Demasiados shards pequeños degradan el rendimiento.

## Arquitectura de un domain

Un domain es un cluster de OpenSearch:

- **Data nodes**: almacenan los datos y ejecutan búsquedas/indexación.
- **Dedicated cluster manager nodes (antes master)**: gestionan el estado del cluster; se recomiendan 3 en producción para estabilidad.
- **Coordinator nodes (opcional)**: reciben las peticiones y reparten la carga.
- **Multi-AZ** (2 o 3 AZs), con réplicas en AZs distintas; Multi-AZ with Standby para mayor disponibilidad.
- **Tipos de instancia**: general purpose, optimizadas para memoria, y OR1 (con almacenamiento respaldado en S3).

## Tiers de almacenamiento (costos)

- **Hot**: nodos de datos normales, para datos recientes y consultados con frecuencia.
- **UltraWarm**: almacenamiento en S3 con caché, más barato, de solo lectura, para datos antiguos que aún se consultan.
- **Cold storage**: datos en S3 sin cómputo asociado; hay que "adjuntarlos" para consultar.
- **Index State Management (ISM)**: políticas que mueven automáticamente los indexes entre tiers y los eliminan (el equivalente a las lifecycle policies de S3).

## OpenSearch Serverless

Variante sin cluster que gestionar: escala automáticamente. Usa collections (de tipo search, time series o vector search) y se factura en OCUs (OpenSearch
Compute Units). Ideal para cargas variables o para empezar sin dimensionar.

## Ingesta de datos

- Kinesis Data Firehose: destino nativo; entrega streaming a OpenSearch (con backup opcional de documentos fallidos en S3).
- OpenSearch Ingestion: pipelines managed basados en Data Prepper, para ingesta y transformación sin servidores.
- Logstash / Beats / agentes (Fluent Bit, etc.).
- CloudWatch Logs: suscripción para enviar logs a OpenSearch.
- DynamoDB: integración zero-ETL con OpenSearch, o vía Streams + Lambda.
- Lambda, MSK, Kinesis Data Streams, y S3 (cargas y consultas directas).
- DMS: puede usar OpenSearch como destino.

## Consulta y visualización

- OpenSearch Dashboards (fork de Kibana): visualización y exploración de logs.
- Query DSL (JSON), SQL y PPL.
- Direct Query a datos en S3 (por ejemplo, logs en el data lake) sin ingerirlos.
- Integración con Athena/QuickSight vía conectores, aunque QuickSight es más habitual con Athena/Redshift.

## Seguridad

- Se despliega dentro de una VPC (acceso privado) o con endpoint público.
- Resource-based (domain access) policies, IAM y SigV4 para autenticar peticiones.
- Fine-grained access control: permisos a nivel de index, documento y campo, con usuarios internos, IAM o SAML/Cognito.
- Cifrado: at rest (KMS), in transit (TLS) y node-to-node.
- Cognito o SAML para acceso a Dashboards.
- Logs de auditoría y de errores hacia CloudWatch.

## Backups y operación

- Snapshots automáticos (horarios, retenidos 14 días) y manuales en S3.
- Escalado: agregar o cambiar nodos (blue/green deployment sin downtime) o auto-tune.
- Monitoreo con CloudWatch: ClusterStatus (red/yellow/green), JVMMemoryPressure, FreeStorageSpace, CPUUtilization. Cluster en rojo = al menos un primary
shard sin asignar; amarillo = faltan réplicas.

OpenSearch frente a otros servicios

| Necesidad                                                       | Servicio    |
| --------------------------------------------------------------- | ----------- |
| Búsqueda de texto completo, logs, analítica casi en tiempo real | OpenSearch  |
| Consultas SQL ad-hoc sobre S3                                   | Athena      |
| Warehouse y BI con joins complejos                              | Redshift    |
| Acceso por clave a baja latencia                                | DynamoDB    |
| Cache en memoria                                                | ElastiCache |
