# EC2

Consideraciones al lanzar una instancia EC2

- AMI (Amazon Machine Image) 
    * Ubuntu
    * Windows
    * Amazon Linux
    * AMIs propias
    * etc
- Instance type (CPU, Memory, disk)
- Network configuration
- Role IAM
- Datos de usuario (script de iniciación)
- Storage
- Tags
- Security group (manejo de puertos, tipo de comunicación, redes, etc)
- public and private keys

## Instance types

[Instances types](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html)

## Instance purchasing options

> the Saving Plans reduce the EC2 costs by making a commitment to a consistent amount of usage for a temt of 1 or 3 years.

* **On-demand Instances**: 
    * Pay by the second, with a 60-second minimum..
    * Pay only for the seconds that the On-Demand Instance is in the **running state**
    * There are quotas for the number of **running On-Demand** instances per account and per region. The quota specifies the maximum number of vCPUs for one or more instance families.
* **Reserved Instances**: 
    * Commitment to a consistent instance configuration, including instance type and Region, for a term of 1 or 3 years.
    * It is executed on a VPC dedicated
* **Spot Instances**: Request unused EC2 instances
* **Dedicated Hosts**: 
    * Pay for a physical host that is fully dedicated to running yout instances
    * Allow you to use your existing per-socket, per-core, or per-VM software licenses, including Windows Server, Microsoft SQL Server, SUSE, and Linux Enterprise Server.
* **Dedicated Instances**: Pay by the hour, for instances that run on single-tenant hardware.



# Lambda

Servicio de ejecución de código **Serverless**. El código se puede ejecutar de forma programada (cron) o por eventos (s3, aplicaciones moviles, etc)

* Se paga solo por el tiempo de cómputo que se utiliza
* 1000 ejecuciones concurrentes
* Hasta 75 GB del archivo .zip (lo que pesa el código + versiones)
* Memoria desde 128 MB hasta 10240 MB (in 1 MB increments)
* 15 minutos máximos de ejecución
* 1 millón de solicitudes gratis