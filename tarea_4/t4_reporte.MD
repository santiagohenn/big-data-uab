## Tarea 2: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](http://github.com/santiagohenn/big-data-uab/).

### Objetivo

Analizar, evaluar y discutir una prueba de concepto de Hadoop.

---

### Actividad 1

En primer lugar crearemos una maquina virtual con la imágen BigDataV3.4:

![img](img/01_create_hadoop_machine.jpg)

Pasamos a modo admin y seteamos hadoop como nombre de host:

```bash
su -
<pnimda>
hostnamectl set-hostname hadoop
```

Configurar mi hostname en la máquina:

```bash
nano /etc/hosts
```

Comentar 127.0.1.1, y agregar la IP de nuestra VM:
10.10.0.144 hadoop.hpc.org hadoop

Resetear la VM asi no tenemos problemas con las configuraciones que aplicamos:

```bash
sudo reboot
```

Iniciar los distributed file systems, resource manager y nodemanagers:

```bash
start-dfs.sh
start-yarn.sh
```

Practica con los libros:

Para ver los libros cargados:
```bash
cd wordcount/
hdfs dfs -ls input
```

Para cargar archivos:
```bash
hdfs dfs -put <file-name> input
```

Por ejemplo, para contar palabras de uno de los libros:

```bash
hadoop jar wc.jar WordCount input/alice.txt <directorio-de-salida>
```

Aclaración: el directorio de salida no deberá ser sobreescribible, para mantener la coherencia del sistema de archivos y la ejecución.

Contar palabras y lineas del archivo:
```bash
wc -c <file-name>
wc -l <file-name>
```

leer y ordenar el output (sort):
```bash
hdfs dfs -cat output/* | sort -k2rn | more
```



---

## Conclusiones



---

## Referencias

Todos los scripts utilizados y código fuente de los informes se pueden encontrar en [mi repositorio personal](https://github.com/santiagohenn/big-data-uab/).

---
