## Tarea 2: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](github.com/santiagohenn/big-data-uab/).

### Objetivo

Analizar, evaluar y discutir una prueba de concepto de contenedores como
muestra de plataformas de virtualización y como encapsular aplicaciones y disponer de
escalabilidad horizontal.

### Instalación de docker

Comandos para instalar docker en Debian (uso mucho el push and pull en las maquinas virtuales en Nebula para copiar comandos)

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



---

### Actividad 1

---

### Actividad 2

IPs

Master
10.10.0.48, 20.20.0.32

Worker
20.20.0.31

En el worker:

```bash
cd /etc/netplan/
nano 50-one-context.yaml
```

agregar:
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
Guardo y luego:

```bash
netplan apply
```

Corroborar con:

```bash
ip r
```

Importante: cortar la inyección de IPs.

```bash
cd ..
cd one-context.d/
```

```bash
nano loc-10-network
```

en la segunda linea le metemos un exit:

```bash
#!/usr/bin...
exit
#...
```

corroborar con ping:

```bash
ping 20.20.0.26
```

Ahora en master ruteamos el worker:

```bash
cd /etc
nano sysctl.conf
```

vamos a la variable del IP forward:

```bash
net.ipv4.ip_forward = 1
```

aplico el IP forwarding:

```bash
sysctl -p
```

Configuro el IP tables. Primero update lulego lo instalo:

```bash
apt update
apt install iptables
```

Agregamos una regla a la tabla de NAT, de postrouting, para que todos los paquetes que deban salir a la internet sean enmascarados:

```bash
iptables -t nat -A POSTROUTING -o <eth0> -j MASQUERADE 
```

<eth0> es la interface que mira a internet.

Probamos haciendo un ping al DNS de google (8.8.8.8):

Y naturalmente deberíamos poder acceder a internet a traves del master:

persistimos las reglas de iptables con iptables-persistent:

```bash
apt install iptables-persistent
```
Guardar las configuraciones actuales
```bash
sudo netfilter-persistent save
```



Creamos un directorio App y un Dockerfile para la imagen que utilizaremos para la actividad:

```Dockerfile
FROM ubuntu
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get -y install apache2
RUN echo "<html><body><h1>Executando en: node X</h1></body></html>" > /var/www/html/index.html
EXPOSE 80
CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
```

Creamos la imagen:

```bash
docker build --tag=apache2 .
```

Corremos la imagen:

```bash
docker run -d -p 8080:80 apache2
```

(8080 porque el 80 esta reservado para root. Podemos usar el 80 con sudo pero no hace falta, por ello mapeamos los puertos).

chequeamos el status con docker ps.

Podemos chequear toda la info de un contenedor con docker inspect. Aca podemos consultar la IP y el gateway! Docker configura todo automaticamente asi no tengo que preocuparme. En nuestro caso la IP es 172.17.0.2 y la gateway 172.17.0.1. Si ponemos 172.17.0.2 en el navegador vemos el front del servicio.

Desde el worker podemos acceder al servicio a través de la IP del worker y el puerto que hayamos designado para el mismo:


Repetimos los pasos para el worker y desplegamos el servicio en el mismo:

docker_running_in_worker

Por último atenderemos las peticiones desde el Master, quien delegará las peticiones escalando el servicio horizontalmente utilizando Swarm. 

Primero detenemos los servicios en master y worker (docker stop <imagen>). Instalamos openssh server en el worker:

```bash
apt install openssh-server
```

Modificamos /etc/ssh/sshd_config para habilitar conexiones (linea 57):

```yaml
...
PasswordAuthentication yes
...
```

no olvidar

```bash
systemctl restart ssh
```

Y controlamos con:

```bash
systemctl status ssh
```

Verificamos la conexión ssh:


Para evitar el uso de passwords (algo molesto para el deployment que estamos buscando), utilizamos un par de llaves. Generamos las mismas con openssh:

```bash
ssh-keygen
```

copio la key al worker:


```bash
ssh-copy-id adminp@20.20.0.31
```

Creamos el swarm

```bash
docker swarm init --advertise-addr 20.20.0.32
```
docker nos va a dar un comando para ejecutar en el worker, que lo una al swarm.

Nos conectamos por ssh al worker y ejecutamos el comando que nos da docker. 

chequeamos los nodos en el master con

```bash
docker node ls
```

Es importante que todas las maquinas tengan la misma version de docker. Con:

```bash
docker swarm join-token worker
```

podemos refrescar el link para sumar mas workers mas adelante

Para crear el servicio ejecutamos:

```bash
docker service create --name swarming --replicas=2 -p 8080:80 apache2
```

(deberiamos ver el proceso de despliegue mientras los servicios se estabilizan)

Verificamos los servicios:

Verificamos que en la misma dirección el servicio puede ser atendido por master o worker:

Por último, instalamos el paquete de utilidades de apache:

```bash
sudo apt install apache2-utils
```

Y probamos nuestro swarm exigiendo el servicio:

```bash
ab -c 100 -n 1000 http://<IP-master>/
```

Tomar metricas y escalar el cluster a 20 replicas:

```bash
docker service scale swarming=20
```

Tomar metricas nuevamente con apache utils.




#### Desplegar la maquina virtual


docker build --tag=app .
docker images

REPOSITORY TAG IMAGE ID
App latest 326387cea398

docker run -d -p 8080:8080 app

---

## Conclusiones



---

## Referencias

Todos los scripts utilizados y código fuente de los informes se pueden encontrar en [mi repositorio personal](github.com/santiagohenn/big-data-uab/).