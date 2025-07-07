# big-data-uab
## Cheatsheet de Scripts

Exportar Markdown a PDF

```bash
Ctrl + Shift + P  # Abrir paleta de comandos
# Buscar: "Markdown export (pdf)"
```

Cambiar nombre del host

```bash
sudo -i
hostnamectl set-hostname master
```

Ver procesos de systemd

```bash
systemd-cgls
```

## Comandos útiles de Docker

Instalar Docker y Docker Compose

```bash
sudo apt update
sudo apt install docker.io docker-compose
```

Comandos básicos

```bash
docker ps                             # Listar contenedores en ejecución
docker ps -a                          # Listar todos los contenedores
docker images                         # Listar imágenes locales
docker pull <imagen>                  # Descargar una imagen
docker run -d --name <nombre> <imagen> # Ejecutar contenedor en segundo plano
docker run -d -p 8080:8080 <imagen> # Ejecutar en deaemon y mapear puertos
docker exec -it <nombre> bash         # Acceder a la terminal de un contenedor
docker stop <nombre>                  # Detener un contenedor
docker rm <nombre>                    # Eliminar un contenedor
docker rmi <imagen>                   # Eliminar una imagen
docker logs <nombre>                  # Ver logs de un contenedor
docker node ls                       # Listar nodos del cluster
docker swarm leave                   # Salir del swarm
docker node rm <nodeid>              # Eliminar nodo por ID
docker node ps                       # Ver procesos en el nodo
docker swarm join-token worker       # Obtener token para unir workers
docker service ls                    # Listar servicios
docker service ps <servicename>      # Ver tareas de un servicio
docker service inspect <servicename> # Inspeccionar servicio
docker service rm <servicename>      # Eliminar servicio
```

Crear un servicio

```bash
docker service create --name swarm_cluster --replicas=2 -p 8080:80 apache2
docker service ls
docker service inspect swarm_cluster --pretty
docker service ps swarm_cluster
```

Escalar un servicio

```bash
docker service scale swarm_cluster=4
docker service ps swarm_cluster
```

Ejecutar una linea de comandos dentro del contenedor:

```bash
docker exec -it <nro contenedor> /bin/bash
```
(esto captura la terminal)