# **Redes informáticas**

una red informática son computadoras autónomas interconectadas mediante una sola tecnología.


# Tecnologías de transmisión

* **Broadcast**(uno a todos). Todas las máquinas en la red comparten el canal de comunicación.
* **Multicast**(uno a varios). Sólo las máquinas interesadas reciben el mensaje.
* **Unicast**(uno a uno). El mensaje puede visitar máquinas intermedias entre el origen y el destino.


# Tipos de redes

* **PAN**(Personal Area Network). Abarcan el espacio alrededor de las personas. (Bluetooth)
* **LAN**(Local Area Network). Abarcan desde una habitación hasta un edificio. (Wifi)
* **MAN**(Metropolitan Area Network). Abarcan areas como ciudades.
* **WAN**(Wide Area Network). Abarcan varias redes MAN.
* **Internet**. La red de redes.


# Protocolos de red

> Un protocolo es un conjunto de reglas.

Los protocolos de red son estándares que definen el intercambio de paquetes de información para lograr la comunicación entre dos o más dispositivos.

## Protocolos de comunicación de red

* **TCP/IP** (Transmission Control Protocol / Internet Protocol)
* **HTTP** (HyperText Transfer Protocol)

## Protocolos de seguridad de red

* **HTTPS** (HyperText Transfer Protocol Secure)
* **SSL** (Secure Sockets Layer)
* **SFTP** (Secure File Transfer Protocol)

## Protocolos de gestion de red

* **SNMP**
* **ICMP**

El modelo OSI (Open Systems Interconnection) organiza conceptualmente a las familias de protocolos de red en capas de red específicas. [Explicación modelo OSI y TCP](https://www.youtube.com/watch?v=jdKRx2BxSMs&ab_channel=GabrielMarcano)


# Direccionamiento IPV4 y Subredes

[Explicación Direccionamiento IPV4 y Subredes](https://www.youtube.com/watch?v=SHbBso63X38&ab_channel=GabrielMarcano)

Una dirección IP es un número de 32 bits (4 bytes). Cuando se separa en bytes y se transforma en decimal se llama *Notación Decimal Punteada*.

## Clases de direcciones IPV4

Definen cuantos bits son de red (los primeros) y cuantos son de host (los últimos).

Para determinar la clase de analiza el primer octeto (primer byte).

| Clase | descripción | desde | hasta | cantidad de redes | cantidad de hosts | Aplicación |
| ----- | ----------- | ----- | ----- | ----------------- | ----------------- | ---------- |
| A | 8 bits de red | 0.0.0.0 | 127.255.255.255 | 128 | 16777214 | Redes grandes |
| B | 16 bits de red | 128.0.0.0 | 191.255.255.255 | 16384 | 65534 | Redes medianas |
| C | 24 bits de red | 192.0.0.0 | 223.255.255.255 | 2097152 | 254 | Redes pequeñas |
| D | ----------- | 224.0.0.0 | 239.255.255.255 | NA | NA | Multicast |
| E | ----------- | 240.0.0.0 | 255.255.255.255 | NA | NA | Investigation |

* El intervalo 127.0.0.0 a 127.255.255.255 está reservado como dirección loopback y no se utiliza.
* 128 es 10000000
* 192 es 11000000
* 224 es 11100000
* 240 es 11110000
* Las máscaras de red nos indican los **bits de red**. Entonces, la máscara 255.255.255.0 denota 24 bits de red y 8 de host. Todas las direcciones IP tienen una máscara por defecto, la cual depende de la clase de red.
* El prefijo de red es una forma de **expresar explicitamente los bits de red**. Entonces, la IP *200.100.210.200/24* indica 24 bits de red y 8 de host. 

## Subredes

Cuando se tienen muchas direcciones de host pero no se van a usar, estas se pierden. Para ahorrar los espaciones de direcciones de host, se crean subredes (division de una red más grande). Se toman bits que corresponden a host y se reasignan a la porción de red (la máscara cambia y pasa a ser una máscara de subred).

Si tenemos una red clase C (ej. 192.168.168.0), y se toman prestados 3 bits de la porción de host, se crean 8 subredes (mascara 255.255.255.224). Por tanto las subredes creadas serían:
* 192.168.168.0 (el primer host sería 192.168.168.1)
* 192.168.168.32 (el primer host sería 192.168.168.3)
* 192.168.168.64 (el primer host sería 192.168.168.65)
* 192.168.168.96 y así

La última dirección de host de la subred 192.168.168.0 es 192.168.168.30, esto porque la IP 192.168.168.31 es la **dirección de difusión** (dirección de broadcast).

