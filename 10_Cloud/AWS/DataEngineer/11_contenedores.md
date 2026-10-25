
# Contenedores en AWS para Data Engineering

## ¿qué es un contenedor y por qué existe?

Un contenedor empaqueta una aplicación junto con todo lo que necesita para ejecutarse (código, runtime, librerías, dependencias, variables de entorno) en una unidad portable y aislada. La idea central es resolver el clásico "en mi máquina funciona": el contenedor se ejecuta igual en cualquier entorno (tu laptop, un servidor, la nube).

La diferencia con una máquina virtual (VM):
- Una VM virtualiza el hardware completo e incluye un sistema operativo completo → pesada (GBs), arranque lento (minutos).
- Un contenedor virtualiza a nivel de sistema operativo: todos los contenedores de un host comparten el mismo kernel del SO, pero están aislados entre sí → ligero (MBs), arranque en segundos.

Esto hace a los contenedores ideales para cargas que necesitan escalar rápido, empaquetar dependencias complejas o garantizar consistencia entre desarrollo y producción.

## Docker — el estándar de contenedores

Docker es la plataforma que popularizó los contenedores. Los conceptos que importan:

- **Dockerfile**: un archivo de texto con las instrucciones para construir la imagen (qué SO base usar, qué dependencias instalar, qué código copiar, qué comando ejecutar).
- **Image**: la plantilla inmutable resultante de construir el Dockerfile. Contiene todo lo necesario para ejecutar la app. Es lo que se distribuye.
- **Container**: una instancia en ejecución de una imagen. De una imagen puedes lanzar muchos contenedores idénticos.

```
Dockerfile  ──build──►     Image   ──run──►  Container(s)
(receta)                (plantilla)       (instancias corriendo)
```

En el contexto de datos, lo relevante es que puedes empaquetar tu lógica de procesamiento (un script de transformación con sus librerías, un job, una app) en una imagen y ejecutarla de forma consistente en los servicios de AWS. Verás imágenes custom en Glue, Lambda (container images), SageMaker y en los servicios de contenedores que siguen.

## Amazon ECR (Elastic Container Registry)

ECR es el registro de imágenes de contenedores managed de AWS. Es, esencialmente, el "repositorio" donde guardas y versionas tus imágenes Docker, análogo a lo que S3 es para objetos pero específico para imágenes de contenedor.

- Guardas (push) tus imágenes ahí y los servicios de cómputo las descargan (pull) para ejecutarlas.
- Integrado con IAM para control de acceso, cifrado en reposo, y escaneo de vulnerabilidades de las imágenes.
- Es el equivalente privado y managed a Docker Hub.

En un pipeline de datos, ECR es de dónde salen las imágenes que ejecutan ECS, EKS, Fargate, Lambda container images o contenedores custom de Glue/SageMaker. Suele ser un detalle de arquitectura, no el protagonista.

### El concepto clave: orquestación de contenedores

Ejecutar un contenedor es fácil. El reto real es ejecutar muchos contenedores en producción: dónde colocarlos, cómo escalarlos, reiniciarlos si fallan, balancear carga, conectarlos entre sí. Eso es la orquestación, y es lo que resuelven ECS y EKS.

AWS ofrece dos orquestadores: ECS (propio de AWS) y EKS (Kubernetes). Y dos modelos de cómputo para ejecutarlos: EC2 (tú gestionas los servidores) o Fargate (serverless). Esta es la matriz mental importante.

## Amazon ECS (Elastic Container Service)

ECS es el orquestador de contenedores propio de AWS — más simple y profundamente integrado con el ecosistema AWS. Conceptos:

- **Task Definition**: la "receta" que define cómo correr tus contenedores (qué imagen de ECR usar, CPU/memoria, puertos, variables, roles IAM). Como un blueprint.
- **Task**: una instancia en ejecución de una task definition (uno o varios contenedores juntos).
- **Service**: mantiene un número deseado de tasks corriendo, las reinicia si fallan, e integra balanceo de carga. Garantiza que "siempre haya N tasks activas".
- **Cluster**: la agrupación lógica donde corren las tasks.

> ECS es más fácil de operar que Kubernetes y es una buena opción cuando estás todo-dentro de AWS y no necesitas la portabilidad/ecosistema de Kubernetes.

## Amazon EKS (Elastic Kubernetes Service)

EKS es Kubernetes managed por AWS. Kubernetes es el orquestador de contenedores estándar de la industria, open-source, muy potente pero más complejo.

- AWS gestiona el control plane de Kubernetes (la parte de coordinación), tú gestionas (o delegas a Fargate) los worker nodes.
- Cuándo elegirlo: cuando ya usas Kubernetes (portabilidad entre nubes/on-premise), tienes experiencia con su ecosistema, o necesitas sus capacidades avanzadas. Si no, ECS suele ser más simple.
- Relevancia en datos: el caso más común en el examen es EMR on EKS, que permite correr trabajos de Spark sobre un cluster EKS (compartiendo infraestructura con otras cargas).

## AWS Fargate — el modelo serverless

Aquí está el concepto más importante para el examen. Fargate NO es otro orquestador — es un modo de cómputo serverless que funciona con ECS o con EKS.

La decisión clave al correr contenedores es quién gestiona los servidores donde se ejecutan:

- **Modo EC2** (launch type EC2): tú provisionas y gestionas una flota de instancias EC2 que forman el cluster. Tú te encargas del parcheo, escalado, capacidad y utilización de esos servidores. Más control, pero más carga operativa.
- **Modo Fargate**: serverless — tú solo defines CPU y memoria que necesita tu contenedor, y AWS se encarga de todo el servidor subyacente (provisioning, parcheo, escalado). No ves ni gestionas instancias. Pagas solo por los recursos que consume la tarea mientras corre.

```
        ┌─────────────── Orquestadores ───────────────┐
        │           ECS                EKS            │
        └──────────────┬────────────────┬─────────────┘
                       │ corren sobre...│
        ┌──────────────┴────────────────┴──────────────┐
        │   EC2 (tú gestionas)  │  Fargate (serverless)│
        └──────────────────────────────────────────────┘
```

> Fargate encaja con la filosofía serverless que el examen favorece: elimina la gestión de servidores. Es la opción típica para cargas batch o de procesamiento de datos esporádicas/variables donde no quieres mantener un cluster de EC2 encendido. Pagas por uso.

> EC2 mode tiene sentido cuando necesitas control fino, configuraciones especiales (GPU, instancias específicas), o costos optimizados con uso sostenido y alto.

## Cómo encajan en pipelines de datos

- Ejecutar ETL o procesamiento containerizado: si tienes lógica de transformación empaquetada en un contenedor (con dependencias que no encajan bien en Glue o Lambda), puedes correrla como una task de ECS/Fargate. Útil para código custom, librerías especializadas, o migrar cargas existentes ya containerizadas.
- Cargas batch: AWS Batch (que puede usar Fargate o EC2 por debajo) orquesta trabajos batch containerizados a gran escala — procesamiento masivo de archivos, por ejemplo.
- Alternativa a Lambda cuando hay límites: Lambda tiene límites (15 min de ejecución, tamaño del paquete, memoria). Si tu procesamiento excede esos límites o necesita ejecución prolongada, un contenedor en Fargate/ECS es la alternativa natural para tareas de larga duración.
- Spark en Kubernetes: EMR on EKS para correr Spark sobre EKS.
- Orquestación: Step Functions y MWAA (Airflow) pueden disparar tasks de ECS/Fargate como pasos de un pipeline.
