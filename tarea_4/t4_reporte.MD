## Tarea 4: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](http://github.com/santiagohenn/big-data-uab/).

### Objetivo

Analizar, evaluar y discutir una prueba de concepto de Hadoop.

---

### Actividad 1

En primer lugar, crearemos una máquina virtual con la imagen BigDataV3.4:

![img](img/00_create_hadoop_machine.jpg)

Pasamos a modo admin y configuramos "hadoop" como nombre de host:

```bash
su -
<pnimda>
hostnamectl set-hostname hadoop
```

Configuramos el hostname en la máquina:

```bash
nano /etc/hosts
```

Comentamos 127.0.1.1 y agregamos la IP de nuestra VM:
10.10.0.144 hadoop.hpc.org hadoop

Reseteamos la VM para aplicar correctamente las configuraciones:

```bash
sudo reboot
```

Iniciamos los distributed file systems, resource manager y nodemanagers:

```bash
start-dfs.sh
start-yarn.sh
```

### Ejercicio con las recetas

Lo primero a tener en cuenta es la preparación de los datos a ser ingestados. En este caso, la existencia de comas en tipos de dato String que podrían entenderse como delimitadores en un CSV. Debemos asegurarnos de que el mapper reemplace las <,> dentro de una String delimitada con <""> por algún otro símbolo.

Realizamos un map-reduce de las recetas y mostramos los resultados ordenados. Ejecutamos además "time" para tener una noción del tiempo que tarda el script y almacenamos los resultados en results.txt:

```bash
time cat rece.csv | ./mapper-rec.py | sort -k1,1 | ./reducer-rec.py > results.txt
sort -k2n results.txt
```

Ejecutamos:

![img](img/03_rece_timed.jpg)

Visualizamos los resultados:

![img](img/04_rece_results.jpg)

Podemos observar que los derivados de las benzodiazepinas (antidepresivos, ansiolíticos) ocupan el primer puesto de medicamentos recetados durante 2022, seguidos de corticosteroides y antiinfecciosos en combinación (quizás para el tratamiento del COVID), seguido por antibióticos.

Corriendo el mismo análisis con Hadoop:

![img](img/05_rece_results_hadoop.jpg)

Vemos que tardó 28.6 segundos en todos los procesadores (4), es decir, ~7 segundos por procesador, frente a los 27.2 de Python.

### Ejercicio con los codones

[Descargaremos el dataset de un gen relacionado al habla y el lenguaje, FOXP2](https://www.ncbi.nlm.nih.gov). Este es un gen presente en humanos y otros mamíferos, relacionado con el desarrollo del lenguaje y el habla. Las mutaciones en FOXP2 pueden causar trastornos del lenguaje. En humanos, este gen tiene una versión ligeramente diferente respecto a otros primates, lo que sugiere que pudo haber influido en la evolución del lenguaje humano. Los datos resumidos del gen, obtenidos de la página del NCBI (National Center of Biotechnology Information) de los Estados Unidos:

| Campo                      | Valor                                         |
|----------------------------|-----------------------------------------------|
| Ensamblaje NCBI RefSeq     | GCF_000001405.40                              |
| Ensamblaje GenBank enviado | GCA_000001405.29                              |
| Taxón                      | Homo sapiens (humano)                         |
| Sinónimo                   | hg38                                          |
| Tipo de ensamblaje         | haploide con loci alternativos                |
| Remitente                  | Genome Reference Consortium                   |
| Fecha                      | 3 de febrero de 2022                          |

El archivo del gen completo tiene un tamaño de 3.3GB. Analizaremos el primer cromosoma, que tiene un tamaño de 252MB. Primero eliminamos los metadatos del archivo:

```bash
tail -c +$((74)) sequence.fa > foxp2.fa
```

Luego realizamos el análisis:

```bash
time cat foxp2.fa | ./mapper.py | sort -k1,1 | ./reducer.py > results_foxp2.txt
sort -k2n results_foxp2.txt
```

El análisis con Python toma alrededor de 15.2 segundos. Los resultados del análisis de codones repetidos, ordenados, son los siguientes:

![img](img/06_foxp2_results_python.jpg)

El codón ```ACAGAGTTTAACCTTTCTTTTCATAGAGCAGTTAGGAAACACTCTGTTTGTAAAGTCTGCAAGTGGATAT``` se repite 21 veces, siendo el más repetido de toda la secuencia.

### Actividad 2

En primer lugar, generamos un directorio para trabajar, donde colocamos [el dataset descargado](https://analisi.transparenciacatalunya.cat/Salut/Registre-de-casos-de-COVID-19-a-Catalunya-per-muni/jj6z-iyrp/about_data), de alrededor de 41.2 MB. Quitamos la primera línea de metadatos y procedemos a modificar el código Python para realizar el análisis.

Codificaremos los campos, por ejemplo la línea:

```csv
08/10/2020,21,MARESME,08121,MATARÓ,,No classificat,1,Dona,Positiu per Test Ràpid,1
```

Deberá generar una tupla: MARESME_PTR 1

Para ello implementamos el siguiente código Python:
```python
import sys

# Diccionario para codificar las pruebas
prueba_codigos = {
    "Positiu per Test Ràpid": "PTR",
    "PCR probable": "PCRP",
    "Epidemiològic": "E",
    "Positiu per ELISA": "PPE",
    "Positiu PCR": "PPCR",
    "Positiu TAR": "PTAR"
}

for line in sys.stdin:
    line = line.strip()
    words = line.split(",")
    if len(words) < 10:
        continue

    prueba = words[9]
    codigo_prueba = prueba_codigos.get(prueba, "OTRO")

    comarca = words[2].replace(" ", "_")
    comarca_codigo = f"{comarca}_{codigo_prueba}"

    try:
        num_casos = int(words[10])
    except ValueError:
        num_casos = 0

    for i in range(num_casos):
        print('%s\t%s' % (comarca_codigo, 1))

```

Luego realizamos el análisis con Python:

```bash
time cat casos_covid.csv | ./mapper.py | sort -k1,1 | ./reducer.py > results_covid.txt
sort -k2n results_covid.txt
```

Obtenemos:

![img](img/07_covid_results_python.jpg)

Lo que toma aproximadamente 7.8 segundos. Modificamos el bash to-execute para ejecutar el trabajo en Hadoop:

```bash
hadoop jar /home/hadoop/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.0.jar -mapper "mapper.py" -file ./mapper.py -reducer "reducer.py" -file ./reducer.py -input "input/casos_covid.csv" -output output
```

Nos aseguramos de borrar el output de Hadoop:

```bash
hdfs dfs -rm -r output
```

Y añadimos el input:

```bash
hdfs dfs -put casos_covid.csv input
```

La ejecución toma alrededor de 26 segundos, en 4 procesadores son ~6 segundos. Leemos y ordenamos el output:
```bash
hdfs dfs -cat output/* | sort -k2rn | more
```

![img](img/08_covid_results_hadoop.jpg)

Podemos observar, tanto en los resultados con "plain" Python como en Hadoop, que la mayor cantidad de casos de COVID detectados fueron en la comuna de Barcelonès, 499042 tests con Tests Rápidos (TAR) y 258862 con tests PCR.

---

## Conclusiones

El trabajo permitió comparar el procesamiento de grandes volúmenes de datos utilizando herramientas tradicionales como Python y soluciones distribuidas como Hadoop. Se observó que, aunque Hadoop requiere una configuración inicial más compleja, ofrece ventajas significativas en escalabilidad y tiempos de procesamiento cuando se trabaja con datasets voluminosos. Esta diferencia debería ser mucho mas notable con más nucleos de proceso en procesadores que lo permitan. 

Como en todos los trabajos hubo desafíos importantes que exigieron revisitar varios de los temas, pero menos problemas que en trabajos anteriores, lo que atribuyo a una familiarización con el entorno y con Linux.

---

## Referencias

Todos los scripts utilizados y el código fuente de los informes se pueden encontrar en [mi repositorio personal](https://github.com/santiagohenn/big-data-uab/).

---

### Anexo 1: Prácticas

En este anexo hago algunas prácticas derivadas de los temas vistos en clase. Lo dejo aquí a modo documental y para revisitar algunos comandos útiles.

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

![img](img/01_hadoop_running.jpg)

La cantidad de bytes es en este caso la cantidad de palabras, ya que los símbolos están en ASCII (8-bits por símbolo). _Aclaración: el directorio de salida no deberá ser sobreescribible, para mantener la coherencia del sistema de archivos y la ejecución_. Para borrar el directorio de output:

```bash
hdfs dfs -rm -r output
```

Podemos ver en el dashboard de análisis y control de Hadoop las tareas realizadas:

```bash
localhost:8088/cluster
```

![img](img/02_hadoop_dashboard.jpg)

Contar palabras y líneas del archivo:
```bash
wc -c <file-name>
wc -l <file-name>
```

Leer y ordenar el output (sort):
```bash
hdfs dfs -cat output/* | sort -k2rn | more
```

Administración de Hadoop
```bash
localhost:50070
```

Administración de YARN

Tirar abajo todo el ecosistema
```bash
stop-all.sh
```

Probar map-reduce con Python, agregar time para medir performance
```bash
time cat war-and-peace.txt | ./mapper.py | sort -k1,1 | ./reducer.py | sort -k2n
```

Ejecutar todo scripteado:
```bash
./to-execute
time ./to-execute
```
