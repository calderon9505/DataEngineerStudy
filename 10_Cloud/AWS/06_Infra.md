# Region

Physical location around the world where cluster data centers are grouped. 


# Availability Zone (AZ)

An Availability Zone is one or more discrete data centers with redundant power, networking, and connectivity in an AWS Region.


## AWS Local Zone

AWS Local Zones place compute, storage, database, and other select AWS services closer to end-users (close to large population and industry centers).


## AWS Wavelength

Service to enable developers to build applications that deliver single-digit millisecond latencies to **mobile devices** and **end-users**. AWS developers deploy their applications to **Wavelength Zones** that provide datacenters at the edge of the 5G networks


## AWS Outposts

bring native AWS services, infrastructure, and operating models to virtually any data center, co-location space, or on-premises facility. You can use the same AWS APIs, tools, and infrastructure across **on-premises** and the AWS cloud to deliver a truly consistent **hybrid experience**.


## Point of Presence (PoP)

Son centros de datos ubicados donde el tránsito es alto. En dichos sitios las empresas tienen sus servidores para servir de **Cache** y así reducir la latencia de los contenidos y la velocidad de transferencia.

Los PoP están más orientados a los contenidos, los Local Zones están más orientados a los servicios

PoPs host:
* Amazon CloudFront (is a CDN)
* Amazon Route 53 (is a DNS)
* AWS Global Accelerator (AGA) (es un servicio de optimización de redes perimetrales)

Los puntos de presencia tienen Edge Locations que se conectan a las AWS Regions 