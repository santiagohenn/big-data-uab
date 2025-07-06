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

Workers


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
                - 20.20.0.30/21
            routes:
                - to: "0.0.0.0/0"
                  via: 20.20.0.26
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

creamos un directorio APP e instalamos la imagen que utilizaremos para la actividad:

```bash
FROM ubuntu
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get -y install apache2
RUN echo "<html><body><h1>Executando en: node X</h1></body></html>" > /var/www/html/index.html
EXPOSE 80
CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
```



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