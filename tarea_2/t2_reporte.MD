## Tarea 2: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](http://github.com/santiagohenn/big-data-uab/).

### Objetivo

Analizar, evaluar y discutir una prueba de concepto de contenedores como
muestra de plataformas de virtualización y cómo encapsular aplicaciones y disponer de
escalabilidad horizontal.

---

### Actividad 1

En primer lugar, desplegamos una máquina virtual en el servicio Nebula, en este caso con un SO Debian 12:

![img](img/01_create_VM.jpg)

A esta computadora la llamaremos master, y tendrá dos tarjetas de red, una conectada a internet (internet_v2) y otra conectada a una red local (middle_v2).

![img](img/02_deployed_VM.jpg)

El siguiente paso es instalar Docker para poder construir la imagen que desplegaremos. Los pasos para instalar el software están en el Anexo 1. Una vez instalado Docker y corroborado que todos los módulos necesarios están presentes, construiremos una imagen a partir del siguiente Dockerfile:

```Dockerfile
FROM python:3.12-slim-bookworm
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get dist-upgrade -y && apt-get install --only-upgrade -y python3 && pip install --upgrade pip && pip install --trusted-host pypi.python.org -r requirements.txt && apt-get clean && rm -rf /var/lib/apt/lists/*
CMD ["python", "app.py"]
```
Donde app.py es un script de Python que despliega un servidor web simple utilizando Flask. El script de Python es similar al visto en clase, solo que agregamos otro endpoint (/galeria) que renderiza un front-end aparte. Mantenemos el resto del código en el repo ya que podría ser útil en TPs posteriores.

```python
from flask import Flask, render_template
from redis import Redis, RedisError
import os
import socket

# Connect to Redis
redis = Redis(host="0.0.0.0", db=0, socket_connect_timeout=2, socket_timeout=2)
app = Flask(__name__)

@app.route("/galeria")
def galeria():
    return render_template("galeria.html")

@app.route("/")
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"
        html = "<h3>Hello {name}!</h3>" \
        "<b>Hostname:</b> {hostname}<br/>" \
        "<b>Visits:</b> {visits}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
```

En este caso, la galería de imágenes accede a una serie de imágenes astronómicas almacenadas en un bucket de Firebase (Google). Construimos la imagen (docker build -t app .)

![img](img/03_build_image.jpg)

Y una vez que tenemos la imagen, la corremos:

```bash
docker run -d -p 8080:8080 app
```

En este caso, -d indica que la ejecución es en modo daemon, y -p nos permite mapear puertos dentro de la aplicación cual capa de transporte. Una vez que nuestra imagen esté corriendo (si todo sale bien) tendremos un hash y un nombre de fantasía para referirnos a la misma:

![img](img/04_running_image.jpg)

Si accedemos al endpoint raíz en el navegador, veremos algo similar a las demostraciones de clase:

![img](img/05_docker_running.jpg)

En el endpoint /galeria veremos la galería de imágenes:

![img](img/06_docker_running_galeria.jpg)

### Actividad 2

Para la actividad 2 necesitaremos dos máquinas virtuales, una que cumplirá el rol de master y otra que cumplirá el rol de worker:

![img](img/07_master_worker.jpg)

Las capacidades (RAM, procesador, almacenamiento) de ambas son iguales, los nombres son solo por un tema de rol. En el caso de la computadora worker, la misma no tendrá conexión a internet, sino que utilizará a la computadora master como gateway. Para ello, tendremos que configurar una serie de cosas. 

#### Configuraciones en el worker

En primer lugar, modificaremos las configuraciones de red del worker. Utilizando netplan:

```bash
cd /etc/netplan/
nano 50-one-context.yaml
```

En este caso, nuestro worker está en la dirección 20.20.0.31, con una máscara de 21 bits y el master se encuentra en la dirección 20.20.0.32. Agregaremos la ruta:

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
Guardamos y aplicamos:

```bash
netplan apply
```

Corroboramos la configuración con:

```bash
ip r
```

Importante: tenemos que desactivar la inyección automática de IPs, para ello modificaremos el archivo loc-10-network:

```bash
cd ..
cd one-context.d/
nano loc-10-network
```

En la segunda línea pondremos un exit:

```bash
#!/usr/bin...
exit
#...
```
#### Configuraciones en master

Rutearemos los paquetes desde el worker hacia internet utilizando ipv4 forwarding. Para ello, activaremos el reenvío de paquetes ipv4 en los controles del sistema:

```bash
cd /etc
nano sysctl.conf
```

Vamos a la variable del IP forward:

```bash
net.ipv4.ip_forward = 1
```

Aplico el IP forwarding:

```bash
sysctl -p
```

Luego utilizaremos iptables para configurar el enmascarado de paquetes (cual NAT o VPN). Primero ejecuto un update de las direcciones de los repositorios y luego instalo el framework:

```bash
apt update
apt install iptables
```

Agregamos una regla a la tabla de NAT, de postrouting, para que todos los paquetes que deban salir a internet sean enmascarados:

```bash
iptables -t nat -A POSTROUTING -o <interface> -j MASQUERADE 
```

<interface> es la interfaz que mira a internet, en mi caso es eth0. Probamos haciendo un ping desde el worker a la NIC conectada a internet en el master:

![img](img/09_worker_reaches_master_eth0.jpg)

Y verificamos conexión a internet haciendo un ping al DNS de Google (8.8.8.8):

![img](img/10_worker_reaches_googledns.jpg)

Y naturalmente deberíamos poder acceder a internet a través del master:

![img](img/11_worker_reaches_googledns.jpg)

Las direcciones cambian dado que, tocando configuraciones y solucionando problemas, en un momento rompí suficientes cosas como para empezar con unas PCs nuevas (larga vida a las máquinas virtuales!). Por último, persistimos las reglas de iptables con iptables-persistent, así no tenemos que reconfigurar todo nuevamente cada vez que reiniciamos las computadoras:

```bash
apt install iptables-persistent
sudo netfilter-persistent save
```

#### Despliegue de la app

Creamos un directorio App y un Dockerfile para la imagen que utilizaremos para la actividad. Construiremos la siguiente aplicación, en este caso utilizando apache2 para el webserver:

```Dockerfile
FROM ubuntu
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get -y install apache2
RUN echo "<html><body><h1>Ejecutando en: master/worker</h1></body></html>" > /var/www/html/index.html
EXPOSE 80
CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
```

Creamos la imagen:

```bash
docker build --tag=apache2 .
```

![img](img/12_docker_apache2_created.jpg)

Corremos la imagen:

```bash
docker run -d -p 8080:80 apache2
```

(8080 porque el 80 está reservado para el root. Podemos usar el 80 con sudo pero no hace falta, por ello mapeamos los puertos).

![img](img/13_docker_apache2_image_running.jpg)

Podemos ingresar al navegador y corroborar la ejecución del servicio web.

![img](img/14_docker_apache2_image_running_browser.jpg)

Podemos chequear toda la info de un contenedor con docker inspect. Acá podemos consultar la IP y el gateway! Docker configura todo automáticamente así no tengo que preocuparme. En nuestro caso la IP es 172.17.0.2 y la gateway 172.17.0.1. Si ponemos 172.17.0.2 en el navegador vemos el front del servicio.

![img](img/15_docker_inspect.jpg)

Desde el worker podemos acceder al servicio a través de la IP del worker y el puerto que hayamos designado para el mismo:

![img](img/16_accessing_master_from_worker.jpg)

Repetimos los pasos para el worker y desplegamos el servicio en el mismo:

![img](img/17_worker_running_docker.jpg)

Por último, atenderemos las peticiones desde el Master, quien delegará las peticiones escalando el servicio horizontalmente utilizando Swarm. Primero detenemos los servicios en master y worker (docker stop <imagen>). Para no lidiar con credenciales utilizaremos el estándar para conexiones seguras, SSH. Instalamos openssh-server en el worker:

```bash
apt install openssh-server
```
Modificamos /etc/ssh/sshd_config para habilitar conexiones (línea 57):

```yaml
...
PasswordAuthentication yes
...
```

No olvidar resetear el servicio ssh para aplicar los cambios:

```bash
systemctl restart ssh
```

Y controlamos con:

```bash
systemctl status ssh
```

Verificamos la conexión ssh:

![img](img/18_successful_ssh.jpg)

Para evitar el uso de passwords (algo molesto para el deployment que estamos buscando), utilizamos un par de llaves, también estándar en las conexiones seguras de hoy en día. Generamos las mismas con openssh:

```bash
ssh-keygen
```

Copio la key al worker:

```bash
ssh-copy-id adminp@20.20.0.31
```

Corroboramos la conexión con las llaves:

![img](img/19_successful_ssh_with_keys.jpg)

Y finalmente creamos el swarm:

```bash
docker swarm init --advertise-addr 20.20.0.32
```

Docker nos va a dar un comando para ejecutar en el worker, que lo una al swarm. Nos conectamos por ssh al worker y ejecutamos el comando que nos da docker:

![img](img/20_successful_swarm_join.jpg)

Chequeamos los nodos en el master con

```bash
docker service ls
```

![img](img/21_docker_service_ls.jpg)

Es importante que todas las máquinas tengan la misma versión de docker. Para refrescar el link para sumar más workers (sobre todo si no lo tengo a mano): 

```bash
docker swarm join-token worker
```

Para crear el servicio ejecutamos:

```bash
docker service create --name swarming --replicas=2 -p 8080:80 apache2
```

(deberíamos ver el proceso de despliegue mientras los servicios se estabilizan). Verificamos los servicios con ```docker node ls```:

![img](img/21_docker_swarm_ls.jpg)

Vemos que tenemos un contenedor atendido por la computadora master y otro atendido por la computadora worker. Si accedemos al servicio web desde un navegador, verificaremos que a veces nos atiende el master y a veces el worker, balanceando la carga:

![img](img/22_master_worker_verification.jpg)

Por último, queremos exigir nuestro servicio para testearlo. Instalamos el paquete de utilidades de apache:

```bash
sudo apt install apache2-utils
```

Y probamos nuestro swarm exigiendo el servicio con 10000 llamadas:

```bash
ab -c 100 -n 10000 http://<IP-master>:<puerto>/
```

Escalamos el cluster a 4 réplicas:

```bash
docker service scale swarming=4
```

Tomamos métricas:

![img](img/23_metrics_4_workers.jpg)

Escalamos el cluster a 20 réplicas:

```bash
docker service scale swarming=20
```
Tomamos métricas nuevamente:

![img](img/23_metrics_20_workers.jpg)

Y desescalamos el cluster nuevamente a 4 réplicas:

```bash
docker service scale swarming=4
```

![img](img/23_metrics_4_workers_again.jpg)

La principal diferencia la notamos en el throughput de transferencia de datos y los tiempos de conexión mínimos. Este servicio, después de todo, es bastante liviano. Para exigir un poco más a la computadora, desplegamos una página web más pesada, que carga una imagen, y realizamos las pruebas con 2 nodos y 20 nodos:

![img](img/24_swarm_heavier_site_2_replicas.jpg)

Corremos la prueba con 2 nodos:

![img](img/25_test_swarm_heavier_site_2_replicas.jpg)

Escalamos a 20 nodos y ejecutamos la misma prueba:

![img](img/26_test_swarm_heavier_site_20_replicas.jpg)

Notando también mejoras en el throughput (transfer rate) y tiempos de conexión máximos (tiempo de respuesta del servidor).

---

## Conclusiones

El trabajo permitió poner en práctica conceptos fundamentales sobre virtualización y despliegue de aplicaciones utilizando contenedores. Se logró construir y ejecutar imágenes Docker (repasé un montón de Docker, me sirvió muchísimo), así como desplegar servicios tanto en modo individual como en clúster utilizando Docker Swarm. A través de las pruebas realizadas, se pudo observar la mejora del rendimiento y la capacidad de respuesta del sistema al realizar un escalamiento horizontal. Me quedé con ganas de hacer algo que exija mucho más a las computadoras, pero sé que las actividades que siguen van por ese camino.

También se evidenció la importancia de una correcta configuración de red y de la automatización en el despliegue, así como la utilidad de herramientas de monitoreo y testeo para evaluar el comportamiento de los servicios bajo distintas cargas. Tuve que resolver varios problemas, pero la actividad solo me requirió "tirar a la basura" dos computadoras, más por el tiempo que me implicaría el troubleshooting que otra cosa.

En resumen, fue una experiencia útil para afianzar conceptos y ver en la práctica cómo escalar servicios y cómo responde la infraestructura ante diferentes demandas.

---

## Referencias

Todos los scripts utilizados y código fuente de los informes se pueden encontrar en [mi repositorio personal](github.com/santiagohenn/big-data-uab/).

---

### Anexo 1: Instalación de docker

Comandos para instalar docker en Debian (uso mucho el push and pull en las máquinas virtuales en Nebula para copiar comandos)

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Instalo todos los paquetes de docker:
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Tenemos que editar los permisos de usuario:

```bash
nano /etc/group
```

Y agregamos adminp a docker:

```yaml
docker:...:adminp
```

Y rebooteamos:

```bash
reboot
```
