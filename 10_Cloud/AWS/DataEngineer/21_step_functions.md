# AWS Step Functions

Step Functions es el servicio serverless de orquestación de AWS. Coordina múltiples servicios en un workflow definido como una state machine.

## State Machine

Defines el flujo en Amazon States Language (ASL), un formato JSON, normalmente diseñándolo visualmente en Workflow Studio (drag-and-drop). Cada paso es un state, y la ejecución avanza de estado en estado pasando datos en JSON como entrada y salida.

Una **execution** es una corrida de la state machine. Puedes ver en la consola, paso a paso, qué ocurrió, con qué datos y dónde falló.

## Tipos de state

| State          | Función                                                                                        |
| -------------- | ---------------------------------------------------------------------------------------------- |
| Task           | Ejecuta trabajo: invoca un servicio de AWS (Lambda, Glue, Athena, EMR, ECS...) o una actividad |
| Choice         | Bifurcación condicional (if/else según los datos)                                              |
| Parallel       | Ejecuta varias ramas al mismo tiempo y espera a que todas terminen                             |
| Map            | Itera sobre una lista de elementos, procesando cada uno (con concurrencia configurable)        |
| Wait           | Pausa por un tiempo o hasta una fecha                                                          |
| Pass           | Pasa datos, opcionalmente transformándolos (útil para pruebas)                                 |
| Succeed / Fail | Terminan la ejecución con éxito o error                                                        |

**Distributed Map**: variante de Map para procesamiento masivo en paralelo (hasta miles de ejecuciones hijas concurrentes), leyendo directamente de S3 (por ejemplo, millones de objetos o un CSV enorme). Es una respuesta moderna a "procesar a gran escala en paralelo".

## Integraciones con servicios

Step Functions se integra con más de 200 servicios de AWS por SDK integrations, sin necesidad de código "pegamento" en Lambda. Hay tres patrones de integración:

1. **Request Response (por defecto)**: llama al servicio y sigue sin esperar a que termine el trabajo.
2. **Run a Job (.sync)**: espera a que el job termine antes de avanzar. Ejemplo: glue:startJobRun.sync espera al fin del job de Glue. Es lo habitual en ETL.
3. **Wait for Callback (.waitForTaskToken)**: pausa hasta que algo externo devuelva un task token (por ejemplo, aprobación humana o un sistema externo). Permite esperas largas.

> Integraciones típicas en data engineering: Glue (jobs y crawlers), EMR (clusters y steps), Athena (consultas), Lambda, ECS/Fargate, Batch, SageMaker, DynamoDB, SNS/SQS, Redshift Data API.

## Manejo de errores y reintentos ⭐

Una de sus mayores fortalezas, y muy preguntada. En cada state se define de forma declarativa:

- **Retry**: reintentos por tipo de error, con IntervalSeconds, MaxAttempts y BackoffRate.
- **Catch**: captura errores y redirige a un state alternativo (limpieza, notificación, ruta de compensación).
- **Timeouts**: TimeoutSeconds y HeartbeatSeconds para detectar tasks colgadas.

**Errores predefinidos**: States.ALL, States.Timeout, States.TaskFailed, etc. Esto reemplaza lógica de reintentos que de otro modo programarías a mano.

## Tipos de workflow: Standard vs Express ⭐
|                 | Standard                                                | Express                                                                    |
| --------------- | ------------------------------------------------------- | -------------------------------------------------------------------------- |
| Duración máxima | Hasta 1 año                                             | Hasta 5 minutos                                                            |
| Semántica       | Exactly-once                                            | At-least-once (async) / at-most-once (sync)                                |
| Volumen         | Hasta ~2,000 ejecuciones/s de inicio                    | Más de 100,000/s                                                           |
| Historial       | Completo en la consola de Step Functions (90 días)      | Solo en CloudWatch Logs                                                    |
| Costo           | Por transición de estado                                | Por número de ejecuciones y duración/memoria                               |
| Ideal para      | ETL, procesos largos, aprobaciones humanas, trabajos no idempotentes | Streaming, IoT, alto volumen y corta duración, procesamiento de eventos |

> Criterio: pipelines de datos largos y que no deben ejecutarse dos veces → Standard. Alto volumen y baja duración → Express.

## Cómo se dispara una ejecución

- EventBridge (regla programada o por evento, ej. llegada de un objeto a S3). Es el patrón estándar.
- API / SDK / CLI (StartExecution).
- API Gateway, Lambda, otra state machine.
- EventBridge Scheduler para ejecuciones programadas.

## Paso de datos entre estados

ASL ofrece filtros para controlar el JSON que fluye:
- InputPath, Parameters, ResultSelector, ResultPath, OutputPath: seleccionan y combinan datos de entrada y salida de cada state.
- Funciones intrínsecas (States.Format, States.JsonToString, etc.).
- Límite de tamaño del payload: 256 KB entre estados. Para datos grandes se pasa solo una referencia (ruta de S3), no el dato.

## Seguridad

- Execution role (IAM): rol que la state machine asume para invocar los servicios. Mismo patrón de roles y trust policy que hemos visto; si un state falla por permisos, se revisa este rol.
- Cifrado con KMS y registro con CloudTrail.
- Logging a CloudWatch Logs (obligatorio en Express para tener historial) y X-Ray para trazabilidad.

## Monitoreo

- Consola con historial visual de cada ejecución.
- Métricas de CloudWatch (ejecuciones fallidas, throttled, duración) y alarmas.
- EventBridge emite eventos de cambio de estado de las ejecuciones, útil para notificar con SNS.

## Costos

- **Standard**: pagas por transición de estado, sin costo cuando está inactivo. Es serverless de verdad.
- **Express**: por solicitudes y duración.
- Contraste con MWAA, que cobra por hora de environment aunque no corra nada.

## Step Functions vs otras opciones de orquestación
s
| Necesidad                                                                         | Opción                                   |
| --------------------------------------------------------------------------------- | ---------------------------------------- |
| Orquestación serverless nativa de AWS, con ramas, paralelismo y manejo de errores | Step Functions                           |
| Ya usas Airflow / portabilidad / DAGs en Python                                   | MWAA                                     |
| Pipeline contenido solo en Glue (crawlers y jobs)                                 | Glue Workflows                           |
| Reaccionar a eventos y enrutarlos                                                 | EventBridge (dispara, no orquesta pasos) |
| Flujo con espera de aprobación humana o callbacks                                 | Step Functions (waitForTaskToken)        |

### Patrón típico de ETL
```
EventBridge (llega archivo a S3)
    → Step Functions:
        1. Glue crawler (.sync)
        2. Glue job (.sync)           ← Retry con backoff
        3. Choice: ¿calidad OK?
            sí → Athena/Redshift carga
            no → SNS notificación (Catch)
```