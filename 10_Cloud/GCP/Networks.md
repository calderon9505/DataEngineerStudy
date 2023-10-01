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

[Subneteo (Tutorial rápido) Fórmula 2^n - 2](https://www.youtube.com/watch?v=7vS9cwzn3vQ&ab_channel=LoboTecnoKu)

[Subneteo (Ejemplo visual)](https://www.youtube.com/watch?v=zeoNe18V_Jo&ab_channel=LoboTecnoKu)

Una dirección IP es un número de 32 bits (4 bytes). Cuando se separa en bytes y se transforma en decimal se llama *Notación Decimal Punteada*.

## Clases de direcciones IPV4

Definen cuantos bits son de red (los primeros) y cuantos son de host (los últimos).

Para determinar la clase se analiza el primer octeto (primer byte).

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

### Direccionamiento

1. Cálculo de las máscaras

Cada máscara debe permitir máximo 2^n-2 hosts. n es la cantidad de bits de host. 100 hosts requiere la máscara 255.255.255.128.

1. Cálculo de redes

El identificador de red permite saber en qué grupo está la máquina y es la primera IP de la red. La dirección de broadcast es la última de la red.

## Direcciones públicas y privadas

El organismo Internet Assigned Numbers Authority (IANA) ha asignado varios rangos de direcciones para utilizar con las redes privadas. Los rangos de direcciones para utilizar con redes privadas son:

* Clase A: 10.0.0.0 a 10.255.255.255 (es decir, una sola red clase A)
* Clase B: 172.16.0.0 a 172.31.255.255 (es decir, 16 redes clase B)
* Clase C: 192.168.0.0 a 192.168.255.255 (es decir, 256 redes clase C)

Una dirección IP dentro de estos rangos se considera, por lo tanto, **no direccionable**, debido a que no es exclusiva. Cualquier red privada que necesite utilizar direcciones IP de forma interna puede utilizar cualquier dirección dentro de estos rangos sin tener que coordinarse con el IANA o un registro de Internet. Las direcciones dentro de este espacio de direcciones son solo exclusivas dentro de una determinada red privada.

Todas las direcciones fuera de estos rangos se consideran públicas.

# NAT (Network Address Translation)

La traducción de direcciones de red, también llamado enmascaramiento de IP o NAT, es un mecanismo utilizado por routers IP para cambiar paquetes entre dos redes que asignan mutuamente direcciones incompatibles. Consiste en convertir, en tiempo real, las direcciones utilizadas en los paquetes transportados. 

En palabras mías, permite conectar redes que usan direcciones privadas (repetidas) por medio de direcciones públicas (únicas).

Las NAT pueden ser Estáticas (un IP privada tiene siempre la misma IP pública), Dinámica (se tienen ciertas IP públicas y se asignan a las privadas según la que esté disponible) y sobrecarga (todas las IP privadas de un red usan la misma IP pública, así es como funciona en los hogares)

# ACL (Access Control List)

Permiten limitar el tráfico que va de una red a otra. Tienen sentido como una implementación física de una política de seguridad.

- Las reglas se evalúan una a una en el orden en que fueron configuradas.
- Una vez se encuentra el primer match se aplica la regla y se omiten las demás.
- Lo anterior implica que deben construirse de lo particular a lo general.
- Al final de toda lista existe una regla implícita de negar todo.

> Todo lo que no esté explícitamente permitido, va a estar implícitamente negado.

## Tipos de listas

* **Estándar**: Filtra según la IP de origen. Se ubican lo más cerca posible del DESTINO del tráfico.
* **Extendida**: Filtra de varias formas. Se ubican lo más cerca posible del ORIGEN del tráfico.
    * IP Origen
    * IP Destino
    * Puerto UDP/TCP Origen
    * Puerto UDP/TCP Destino
    * Protocolo