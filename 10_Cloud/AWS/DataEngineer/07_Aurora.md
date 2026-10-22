# Amazon Aurora

Aurora es el motor de base de datos relacional propio de AWS, compatible con MySQL y PostgreSQL, pero rediseñado desde cero para la nube. **Es parte de la familia RDS**, pero con una arquitectura de storage distinta que le da ventajas importantes en performance, disponibilidad y escalabilidad.

La idea central: compatible pero reinventado

- Aurora es drop-in compatible: una aplicación que usa MySQL o PostgreSQL puede usar Aurora sin cambiar el código (mismos drivers, mismas queries).
- AWS afirma hasta ~5x el throughput de MySQL y ~3x el de PostgreSQL estándar.
- La diferencia clave está en cómo separa cómputo y storage.

## La arquitectura de storage (lo que lo hace especial)

- Aurora separa el compute (las instancias de base de datos) del storage. El storage es una capa distribuida, compartida y auto-reparable.
- Los datos se replican automáticamente en 6 copias a través de 3 Availability Zones (2 copias por AZ).
- El storage crece automáticamente en incrementos, hasta 128 TB, sin que tú lo provisiones. No te preocupas por el tamaño del disco.
- Es self-healing: detecta y repara bloques dañados automáticamente usando las otras copias.
- Tolerancia a fallos del storage: puede perder 2 copias sin afectar escrituras y 3 copias sin afectar lecturas.

```
        ┌──────────────── Compute layer ────────────────┐
        │   Writer instance   +   Reader instances      │
        └───────────────────────┬───────────────────────┘
                                │ (todos comparten el mismo storage)
        ┌───────────────────────▼────────────────────────┐
        │   Shared distributed storage (auto-scaling)    │
        │   6 copias  ×  3 AZs   (self-healing)          │
        └────────────────────────────────────────────────┘
```

Esto cambia todo respecto a RDS tradicional: como el storage es compartido, agregar réplicas de lectura no requiere copiar los datos — todas las instancias leen del mismo storage.

## Alta disponibilidad y réplicas

- Puedes tener hasta 15 Aurora Replicas (vs. 5 read replicas en RDS MySQL).
- Las réplicas comparten el storage con el writer → replicación casi instantánea (lag de milisegundos) y sin carga extra de copiado.
- Failover automático y muy rápido (típicamente < 30 segundos): si el writer cae, una réplica es promovida automáticamente. Mucho más rápido que el Multi-AZ clásico de RDS.
- Una sola instancia Aurora ya tiene el storage replicado en 3 AZs, así que la durabilidad es alta incluso sin réplicas de cómputo.

## Endpoints de Aurora

Aurora expone endpoints inteligentes para que tu app se conecte correctamente:

| Endpoint                  | Para qué                                                                      |
| ------------------------- | ----------------------------------------------------------------------------- |
| Cluster (writer) endpoint | Apunta siempre al writer actual (escrituras). Se reapunta solo tras failover. |
| Reader endpoint           | Balancea automáticamente las lecturas entre todas las réplicas.               |
| Custom endpoints          | Subconjuntos de instancias para cargas específicas.                           |
| Instance endpoints        | Una instancia concreta (uso avanzado).                                        |

## Backups

- Backups automáticos continuos a S3, con Point-in-Time Recovery.
- Snapshots manuales, compartibles y copiables entre regiones.
- Los backups no impactan el performance (por la arquitectura de storage).

## Aurora Global Database

- Replica un cluster Aurora a otras regiones (hasta 5 regiones secundarias).
- Replicación con lag típico < 1 segundo.
- Casos: DR cross-region (RTO/RPO bajos) y lecturas de baja latencia para usuarios globales.
- Promoción de una región secundaria a primaria en caso de desastre regional (< 1 minuto típicamente).

## Aurora Serverless

Aurora Serverless escala la capacidad de cómputo automáticamente según la carga, sin que provisiones instancias.

- v2 (la actual) escala de forma fina y rápida, sin downtime, y sirve para cargas de producción.
- Ideal para cargas variables, intermitentes o impredecibles → pagas por la capacidad que usas (medida en ACUs – Aurora Capacity Units).
- Evita sobre-provisionar para picos que ocurren a ratos.

## Endpoints

Un endpoint en Aurora es una URL de conexión (DNS) a la que apunta tu aplicación. Aurora ofrece varios tipos, cada uno con una función distinta de enrutamiento. Entenderlos evita gestionar manualmente a qué instancia conectarse.

| Endpoint         | Apunta a                         | Uso principal     | Failover-aware        |
| ---------------- | -------------------------------- | ----------------- | --------------------- |
| Cluster (Writer) | Writer actual                    | Escrituras        | Sí (se reapunta solo) |
| Reader           | Réplicas de lectura (balanceado) | Escalar lecturas  | Sí (ajusta el pool)   |
| Custom           | Subconjunto definido por ti      | Separar workloads | Sí (dentro del grupo) |
| Instance         | Una instancia concreta           | Debug / avanzado  | No                    |


### 1. Cluster Endpoint (Writer Endpoint)

- Apunta siempre a la instancia writer (la primaria) del cluster.
- Se usa para escrituras (INSERT/UPDATE/DELETE) y también lecturas si hace falta.
- Clave: tras un failover, este endpoint se reapunta automáticamente a la nueva writer. Tu app no cambia la connection string.
- Solo hay uno por cluster.

> Úsalo para: todas las escrituras.

### 2. Reader Endpoint

- Apunta al conjunto de Aurora Replicas (instancias de solo lectura).
- Balancea automáticamente las conexiones de lectura entre todas las réplicas disponibles (round-robin a nivel de conexión).
- Si agregas o quitas réplicas, el reader endpoint las incluye/excluye automáticamente.
- Si no hay réplicas, apunta al writer.

> Úsalo para: escalar y repartir lecturas sin gestionar balanceo tú mismo.

> Matiz: balancea por conexión, no por query. Una conexión de larga duración queda "pegada" a una réplica.

### 3. Custom Endpoints

- Apuntan a un subconjunto específico de instancias que tú defines.
- Útil para dirigir ciertas cargas a instancias con características concretas (ej. instancias más grandes para reporting pesado vs. instancias normales para la app).
- Puedes tener varios.

> Úsalo para: separar workloads (ej. analytics vs. tráfico normal) en grupos de instancias distintos.

### 4. Instance Endpoints

- Apuntan a una instancia específica del cluster (por su nombre).
- Uso avanzado/diagnóstico: cuando necesitas conectarte a una instancia puntual.
- No recomendado para la app general, porque si esa instancia falla o cambia de rol, pierdes el beneficio del enrutamiento automático.

> Úsalo para: debugging / casos puntuales, no para la app en producción.


## Proxy

Con Aurora, el beneficio de RDS Proxy se combina con los endpoints inteligentes que ya trae Aurora de fábrica. Conviene no confundirlos porque resuelven cosas distintas:

Es decir:
- El reader endpoint de Aurora decide a qué instancia va la conexión (balanceo de lectura).
- RDS Proxy gestiona cuántas conexiones reales se abren y las reutiliza (pooling).

# Features relevantes para Data Engineering (DEA-C01)

1. **Zero-ETL integration con Redshift** ⭐ — replica datos transaccionales de Aurora a Redshift casi en tiempo real sin construir un pipeline ETL. Elimina la necesidad de Glue/DMS para llevar datos OLTP → OLAP para analytics.

2. **Aurora Machine Learning** — integra con SageMaker y Comprehend para hacer inferencias ML directamente desde SQL.

3. **Fuente para pipelines** — como RDS, Aurora es fuente para DMS (con CDC), Glue, federated queries.

4. **Backtrack (solo Aurora MySQL)** — "rebobina" la base a un punto anterior en segundos sin restaurar un backup. Útil para deshacer errores rápido.

5. **Fast cloning** — crea un clon de la base casi instantáneo usando copy-on-write (no duplica el storage de inmediato). Ideal para crear entornos de test/dev sobre datos de producción sin copiar todo.


## Aurora vs RDS

|                     | RDS (MySQL/PostgreSQL)                       | Aurora                                         |
| ------------------- | -------------------------------------------- | ---------------------------------------------- |
| Storage             | Ligado a la instancia, lo provisionas        | Compartido, distribuido, auto-scaling (128 TB) |
| Réplicas de lectura | Hasta 5, replicación asíncrona (copia datos) | Hasta 15, storage compartido, lag ms           |
| Durabilidad         | Multi-AZ (1 standby)                         | 6 copias en 3 AZs siempre                      |
| Failover            | ~1–2 min                                     | < 30 seg                                       |
| Serverless          | No (salvo Aurora)                            | Aurora Serverless v2                           |
| Cross-region        | Read replica                                 | Global Database (lag <1s)                      |
| Costo               | Más barato base                              | Más caro, pero más performance/features        |
