## Tarea 2: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](http://github.com/santiagohenn/big-data-uab/).

### Objetivo

Analizar, evaluar y discutir una prueba de concepto del despliegue de un clúster sobre OpenNebula.

---

### Actividad 1

Implementaremos la siguiente arquitectura de clúster:

![img](img/01_cluster_schema.jpg)

Desplegamos las MV y las configuramos con netplan (si llegáramos a utilizar Ubuntu, tendremos que editar las interfaces). Es posible editar el archivo one-context.d para cambiar el orden en el cual Debian ejecuta distintos aplicativos para configurar la red (algo como cambiar el boot order de discos de inicio).

En cada worker configuramos el Frontend como gateway, editando el archivo 50-one-context.yaml:

```bash
cd /etc/netplan/
nano 50-one-context.yaml
```

En este caso, nuestros workers están en las direcciones 20.20.0.31 y 20.20.0.12, con una máscara de 21 bits, y el master se encuentra en la dirección 20.20.0.32. Agregaremos la ruta:

```yaml
network:
    version: 2
    renderer: networkd
    ethernets:
        eth0:
            addresses:
                - 20.20.0.31/21
            routes:
                - to: "0.0.0.0/0"
                  via: 20.20.0.32
                  metric: 0
```

Guardamos, aplicamos y reseteamos la red:

```bash
netplan apply
```

Considerando que el Frontend está configurado para rutear los paquetes a Internet, deberíamos tener conexión a Internet desde ambos workers. Verificar esto con un ping a un DNS externo o una URL.

Importante: recordar desactivar la inyección automática de IPs, modificando el archivo loc-10-network:

```bash
cd ..
cd one-context.d/
nano loc-10-network
```

Con un exit:

```bash
#!/usr/bin...
exit
#...
```

Verificamos que el Nodo 2 (worker3 en mi caso) llega a Internet:

![img](img/02_node2_reaches_internet.jpg)

Actualizamos la lista de paquetes en cada máquina:

```bash
sudo apt update
```

(No hemos tenido warnings). Instalamos y/o verificamos que tenemos openssh y firefox:

```bash
sudo apt install openssh-server
```

Recordemos habilitar e iniciar el servicio SSH y verificar funcionamiento:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
firefox --version
```

### Actividad 3

Modificamos las siguientes opciones en /etc/ssh/sshd_config para habilitar conexiones:

```yaml
...
PasswordAuthentication yes
RSAAuthentication yes
PubKeyAuthentication yes
UseDNS no
PermitRootLogin yes
...
```

No olvidar reiniciar el servicio ssh para aplicar los cambios:

```bash
systemctl restart ssh
```

Comprobamos conectividad desde frontend (reciclamos nuestra computadora master) hacia el nodo2 (worker3 en nuestro caso). Copio la key al worker:

```bash
ssh-copy-id adminp@20.20.0.12
```

(Aca tuve problemas y copié la clave manualmente a authorized_keys).

Y ejecuto:

```bash
ssh adminp@20.20.0.12
```

Para corroborar conexión con el nodo 2:

![img](img/03_master_reaches_node2.jpg)

Probamos el protocolo de ejecución con interfaz gráfica:

```bash
ssh -X adminp@20.20.0.12
...
xeyes
xclock
```

![img](img/04_xprotocol_eyes.jpg)

![img](img/05_xprotocol_clock.jpg)

### Actividad 2

Instalar sobre Frontend el servicio dnsmasq (recordar parar y deshabilitar el servicio systemd-resolved), configurar y verificar su funcionalidad, configurar nodeX para que Frontend sea su DNS y verificar su funcionalidad.

En master:

```bash
cd /etc
nano hosts
```

Tendremos los namespace por defecto, agregaremos las direcciones de nuestro master y nodos con nombres de dominio:

```bash
...
10.10.0.48  mastergw.hpc.org mastergw
20.20.0.32  master.hpc.org master
20.20.0.31  worker2.hpc.org worker2
20.20.0.12  worker3.hpc.org worker3
```

![img](img/06_conf_dominios.jpg)

Probemos hacer ping a alguno de los alias:

```bash
ping worker2
```

![img](img/07_ping_dominios.jpg)

Instalaremos dnsmasq:

```bash
apt update
apt install dnsmasq
```

Veremos con:

```bash
systemctl status dnsmasq
```

![img](img/08_dnsmasq_troubles.jpg)

Que tenemos que hacer varias configuraciones. Si tenemos conflictos de puertos, paramos el servicio que esté usando el puerto:

```bash
systemctl stop [nombre del servicio]
systemctl disable [nombre del servicio]
systemctl restart dnsmasq
systemctl status dnsmasq
```

Configuramos el servicio en /etc/dnsmasq.conf:

```bash
…
domain-needed
…
local=/hpc.org/
…
server=158.109.0.1@ensX
…
interface=eth1
….
domain=hpc.org
```

Reiniciamos el servicio:

```bash
systemctl restart dnsmasq
```

Corroboramos con paquetes icmp a Internet:

![img](img/09_ping_google.jpg)

Editamos los nameserver:

```bash
nano /etc/resolv.conf
```

Insertamos el nameserver local en la primera línea:

```bash
nameserver 127.0.0.1
...
```
(Podemos comentar los de la UAB). Chequeamos:

```bash
host master.hpc.org
...
```

Y deberíamos ver la IP resuelta:

![img](img/10_host_Resolved.jpg)

Probamos resolver a Internet con un ping:

![img](img/11_ping_after_dns.jpg)

¡Hurra! Tenemos resolución DNS interna y externa. Probamos la resolución DNS desde el worker:

![img](img/12_resolucion_dns_desde_worker.jpg)

Por último, instalaremos netdata para monitorear las máquinas virtuales. Nos hacemos una cuenta en https://app.netdata.cloud e instalamos sobre las MV el software de netdata con la configuración indicada en app.netdata.cloud.

![img](img/13_netdata_account.jpg)

En la PC a monitorear ejecutamos el comando provisto. Instalará un montón de cosas, si todo va OK, el servicio estará ejecutándose:

![img](img/14_netdata_master_success.jpg)

Y podremos monitorear el nodo en la interfaz visual:

![img](img/15_netdata_master_metrics.jpg)

Repetimos por cada máquina virtual (cada comando para agregar una PC es distinto de la anterior) y tendremos nuestro dashboard desplegado:

![img](img/16_all_nodes_working.jpg)

---

## Conclusiones

Este trabajo me permitió experimentar de manera práctica el despliegue y la configuración de un clúster (pequeño) sobre OpenNebula, con enfoque en el direccionamiento de datos entre las distintas VM. Si bien es un experimento a escala pequeña, los mismos procedimientos se podrían usar para agregar más computadoras a la red. Abordé aspectos importantes como la gestión de accesos por SSH y la resolución DNS, teniendo que resolver varias dificultades durante la configuración y testeo.

Hacia lo último desplegamos un sistema de monitoreo de métricas (Performance, State of Health, etc.) basado en netdata. ¡Está muy bueno! Intuyo que las gráficas están hechas con Grafana. Si bien nos permite centralizar la información de status y performance de un número elevado de instancias en un solo lugar, la instalación de esta herramienta en cada computadora me hizo notar que el impacto en términos de memoria y performance que el mismo programa tiene no es trivial. En una nanocomputadora con recursos muy limitados habría que hacer una evaluación costo-beneficio en cuanto al despliegue de este tipo de herramientas.

---

## Referencias

Todos los scripts utilizados y código fuente de los informes se pueden encontrar en [mi repositorio personal](https://github.com/santiagohenn/big-data-uab/).

---
