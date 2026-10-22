# EBS

EBS (Elastic Block Store) es el servicio de almacenamiento en bloques de AWS. Básicamente, son "discos duros virtuales" que se adjuntan a instancias EC2.

Un EBS es una unidad de red (no es una unidad física), por tanto, se usa la red para comunicar la ec2 con la unidad, generando una pequeña latencia.

Características clave:

- **Persistente**: los datos sobreviven si detienes o reinicias la instancia EC2 (a diferencia del almacenamiento efímero / instance store).
- **Volúmenes en bloque**: el sistema operativo lo ve como un disco normal, lo formateas y montas (ext4, NTFS, etc.).
- **Atado a una AZ**: un volumen solo puede adjuntarse a instancias de la misma AZ. Para moverlo a otra AZ, creas un snapshot y lo restauras allí.
- **Uno a uno por defecto**: un volumen se adjunta a una instancia a la vez (salvo con Multi-Attach en volúmenes io1/io2). Un EBS se puede desconectar de una ec2 y conectar a otra sin problema.
- **Snapshots**: respaldos incrementales que se guardan en S3, útiles para backups, clonar volúmenes o crear AMIs.
- **Redimensionable en vivo**: puedes aumentar (no disminuir) tamaño o cambiar tipo sin apagar la instancia.

Tipos principales:

| Tipo      | Uso típico                                                     |
|-----------|----------------------------------------------------------------|
| gp3 / gp2 | SSD de propósito general — el default para la mayoría de casos |
| io2 / io1 | SSD de alto IOPS — bases de datos exigentes                    |
| st1       | HDD optimizado para throughput — big data, logs                |
| sc1       | HDD de bajo costo — datos de acceso infrecuente                |

> Un detalle de costo: los volúmenes EBS se cobran por GB provisionado por mes, estén en uso o no. Es muy común dejar volúmenes huérfanos tras terminar instancias y seguir pagándolos.

# EFS

EFS (Elastic File System) es un sistema de archivos NFS gestionado por AWS. A diferencia de EBS, se comporta como una carpeta de red compartida: muchas instancias EC2 (o contenedores, o funciones Lambda) pueden montarlo y leer/escribir al mismo tiempo.

Características clave:

- **Compartido y concurrente**: miles de clientes pueden montar el mismo sistema de archivos simultáneamente.
- **Regional, no zonal**: vive en varias Availability Zones de una región. Creas "mount targets" en cada subnet y cualquier instancia de esa VPC lo monta.
- **Elástico de verdad**: crece y se encoge automáticamente según los datos que guardes. No provisionas tamaño.
- **Pago por uso**: cobras por GB realmente almacenado (más throughput en algunos modos), no por capacidad reservada.
- **Protocolo NFSv4.1**: solo Linux. Windows no lo soporta nativamente — para eso existe FSx for Windows File Server.
- **Clases de almacenamiento**: Standard, Infrequent Access y Archive, con políticas de lifecycle para mover archivos viejos a clases más baratas.

Cómo se monta, en la práctica:

`sudo mount -t nfs4 -o nfsvers=4.1 fs-0123456789abcdef.efs.us-east-1.amazonaws.com:/ /mnt/efs`

Cuándo usarlo frente a las alternativas:

| Necesidad                                               | Servicio        |
|---------------------------------------------------------|-----------------|
| Disco dedicado para una instancia, baja latencia        | EBS             |
| Carpeta compartida entre varias instancias/contenedores | EFS             |
| Objetos accesibles por API/HTTP, web assets, data lake  | S3              |
| Recurso compartido SMB para Windows                     | FSx for Windows |

> Casos típicos: directorios home compartidos, almacenamiento persistente para pods de EKS/ECS, contenido compartido de servidores web, pipelines de CI/CD.

> Un par de advertencias prácticas: EFS tiene latencia mayor que EBS (es red, no disco local), así que no es buena idea poner ahí la base de datos de una app transaccional. Y el control de acceso depende de dos capas que hay que configurar bien: los security groups de los mount targets (puerto 2049) y las políticas de file system / access points. Vale la pena habilitar cifrado en tránsito y en reposo desde el inicio.