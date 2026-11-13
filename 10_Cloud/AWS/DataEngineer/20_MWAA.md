# Amazon MWAA (Managed Workflows for Apache Airflow)

MWAA es el servicio managed de AWS para Apache Airflow, la plataforma open-source de orquestación de workflows más
usada en data engineering.

## Apache Airflow

Airflow permite definir, programar y monitorear pipelines como código Python. No procesa los datos él mismo: orquesta
otras herramientas (Glue, EMR, Athena, Redshift, Lambda, etc.) indicando qué se ejecuta, en qué orden y qué pasa si
algo falla.

### Conceptos centrales

- **DAG (Directed Acyclic Graph)**: el workflow completo. Es un grafo dirigido (las dependencias tienen sentido) y acíclico (no hay ciclos, no se vuelve atrás). Se define en un archivo Python.
- **Task**: una unidad de trabajo dentro del DAG (ej. lanzar un job de Glue).
- **Operator**: plantilla que define qué hace una task. Ejemplos: `GlueJobOperator`, `EmrAddStepsOperator`, `AthenaOperator`, `RedshiftSQLOperator`, `LambdaInvokeFunctionOperator`, `PythonOperator`, `BashOperator`.
- **Sensor**: tipo especial de operator que espera a que ocurra algo (ej. S3KeySensor espera a que llegue un archivo a S3).
- **Hook**: interfaz de conexión reutilizable hacia sistemas externos.
- **Dependencias**: se definen con task_a >> task_b (b corre después de a).
- **Schedule**: cuándo corre el DAG (cron o intervalos), con soporte de backfill (ejecutar para fechas pasadas) y catchup.
- **XCom**: mecanismo para pasar pequeñas cantidades de datos entre tasks (no para datasets grandes).
- **Retries y alertas**: reintentos, timeouts y callbacks configurables por task.

### Ejemplo conceptual:
```
with DAG("etl_ventas", schedule="@daily", start_date=...) as dag:
    esperar = S3KeySensor(...)
    transformar = GlueJobOperator(...)
    cargar = RedshiftSQLOperator(...)
    esperar >> transformar >> cargar
```

## MWAA

Operar Airflow uno mismo implica gestionar servidores, base de datos de metadata, workers, escalado, parches y alta disponibilidad. MWAA lo gestiona, y tú solo subes tus DAGs.

### Arquitectura de un environment

Un environment de MWAA incluye:
- **Scheduler**: lee los DAGs y dispara las tasks (en múltiples AZs).
- **Workers**: ejecutan las tasks; escalan automáticamente entre un mínimo y un máximo.
- **Web server**: la UI de Airflow para monitorear, ver logs y lanzar DAGs manualmente.
- **Metadata database**: gestionada por AWS, guarda el estado.
- **Bucket de S3**: donde subes tus DAGs, requirements.txt (dependencias Python) y plugins. MWAA los sincroniza solo.

Detalles de operación:
- El environment corre en una VPC (AWS gestiona los componentes, tú aportas las subnets, que deben ser privadas en dos AZs).
- Tamaños de environment (small, medium, large...) que determinan la capacidad.
- Auto scaling de workers según la cola de tasks.
- Soporta distintas versiones de Airflow, y las actualizaciones de versión requieren planificación.

### Seguridad

- Execution role (IAM): rol que MWAA asume para acceder a S3, CloudWatch y a los servicios que orquestan los DAGs (Glue, EMR, Athena...). Mismo patrón de roles/STS que hemos visto. Si un DAG falla por permisos, normalmente es este rol.
- Acceso a la UI: controlado con IAM; puede ser público o privado (por VPC endpoint).
- Cifrado: at rest con KMS, in transit con TLS.
- Secrets: las conexiones y variables pueden guardarse en AWS Secrets Manager como backend de secretos.
- Control de red con security groups.

### Monitoreo

- CloudWatch: métricas del environment (cola de tasks, heartbeat del scheduler) y logs de scheduler, workers, web server y tasks.
- La UI de Airflow muestra el estado de DAGs y tasks, tiempos, reintentos y logs.
- Alarmas en CloudWatch y notificaciones por fallo mediante callbacks o SNS.

### Costos

Pagas por hora de environment (según tamaño), por workers adicionales y por almacenamiento de metadata. El environment tiene costo aunque no corran DAGs, a diferencia de Step Functions, que cobra por transición. Esto es un factor de decisión.

## MWAA vs Step Functions vs Glue Workflows ⭐

|             | MWAA (Airflow)                                                   | Step Functions                                                       | Glue Workflows                    |
| ----------- | ---------------------------------------------------------------- | -------------------------------------------------------------------- | --------------------------------- |
| Modelo      | Código Python (DAGs)                                             | Máquina de estados (JSON/ASL, visual)                                | Crawlers y jobs de Glue           |
| Servidor    | Environment siempre activo                                       | Serverless                                                           | Serverless                        |
| Alcance     | Multi-servicio y multi-nube                                      | Muy integrado con AWS (200+ servicios)                               | Solo dentro de Glue               |
| Complejidad | Pipelines complejos, muchas dependencias                         | Flujos con ramas, paralelismo, manejo de errores                     | Pipelines simples en Glue         |
| Costo       | Por hora de environment                                          | Por transición de estado                                             | Sin costo extra de orquestación   |
| Ideal si    | Ya usas Airflow, necesitas portabilidad o el ecosistema de operators | Quieres serverless y flujos event-driven nativos                 | Todo ocurre en Glue               |

Criterio del examen:
- Migrar workflows de Airflow existentes o necesidad de portabilidad y ecosistema open-source → MWAA.
- Orquestación serverless, nativa de AWS, event-driven → Step Functions.
- Pipeline contenido solo en Glue → Glue Workflows.
- Trigger por evento (llega un archivo a S3): lo más natural es EventBridge + Step Functions; en MWAA se haría con un
sensor o disparando el DAG por API.

Buenas prácticas

- Airflow orquesta, no procesa: delega el trabajo pesado a Glue, EMR, etc. Ejecutar transformaciones grandes dentro de los workers de MWAA es un antipatrón.
- Idempotencia en las tasks, para que los reintentos y backfills no dupliquen datos.
- Usar deferrable operators o sensores en modo reschedule para no ocupar slots de workers esperando.
- Mantener los DAGs ligeros al parsearse (sin consultas pesadas a nivel superior del archivo).
- Pasar solo metadata por XCom, no datos grandes.
- Guardar credenciales en Secrets Manager, no en el código.