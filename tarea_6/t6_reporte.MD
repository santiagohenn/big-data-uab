## Tarea 6: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](http://github.com/santiagohenn/big-data-uab/).

### Objetivo

Analizar, evaluar y discutir una prueba de concepto de Spark sobre Docker.

---

### Actividad 1

Clonamos el repositorio: [Spark cluster on docker](https://github.com/cluster-apps-on-docker/spark-standalone-cluster-on-docker.git).

![img](img/00_spark_standalone_clone.jpg)

Si queremos agregar workers: en el archivo docker-compose.yml agregamos secciones spark-worker-N tal como están en el yml.

Instalamos Docker y Docker Compose y ejecutamos sobre el directorio:

```bash
sudo docker compose up
```

Para construir la imagen. Abrimos un navegador en localhost:8888 y deberíamos poder ver el Jupyter Lab:

![img](img/01_jupyter_working.jpg)

Éxito! Trabajamos con un kernel de Python3 en la nube. Podemos ver los workers de Spark en localhost:8080:

![img](img/02_spark_workers.jpg)

Y podemos acceder a los nodos worker desde ahí, o en localhost:<puerto_del_nodo>. Para subir archivos al árbol local accedemos a localhost:8888/tree, de otra forma el notebook nos limitará a 15MB. Subimos el registro de datos de covid en /data. Utilizando el notebook, leemos el archivo de datos de covid provisto en la actividad y monitoreamos el master y los workers:

![img](img/03_covid_data_read.jpg)

![img](img/03_covid_data_read_b.jpg)

![img](img/03_covid_data_read_c.jpg)

Seleccionamos un subconjunto de los datos, en este caso Comarca, sexo y número de fallecimientos:

```python
data = data.select("Comarca","Sexe","Nombre defuncions")
data.show(20)
```

![img](img/03_covid_data_read_d.jpg)

Mientras o luego de ejecutar estas tareas podemos monitorear el estado del Master:

![img](img/04_master_at_work.jpg)

Y los workers:

![img](img/05_worker_1.jpg)

![img](img/06_worker_2.jpg)

Y también visualizarlos en la terminal como procesos de Docker:

```bash
docker ps
```
![img](img/07_docker_ps.jpg)

### Actividad 2

Descargaremos un dataset de recetas restringido (filtrado) al año 2025 para analizarlo con Spark+Docker. El mismo pesa ~93MB, lo llamaremos recetas_2025.csv y lo cargaremos en el árbol del hdfs simulado.

Primero instalamos las librerías plotly y pandas:

```bash
pip install plotly
pip install pandas
```

Importamos las librerías que utilizaremos e inicializamos la sesión de Spark:

```python
from pyspark.sql import SparkSession
import plotly.graph_objs as go
from plotly.offline import plot

print("Estadísticas de recetas utilizando spark-docker")

spark = SparkSession.\
    builder.\
    appName("pyspark-notebook").\
    master("spark://spark-master:7077").\
    config("spark.executor.memory", "512m").\
    getOrCreate()

data = spark.read.csv(path="data/recetas_2025.csv", sep=",", header=True)
```

Mostramos las primeras 20 líneas del archivo cargado y consultamos algunos datos del dataset para corroborar la carga correcta:

```python
print("Archivo cargado.", data.count(), "líneas,",len(data.columns),"columnas.")
data.show(20)
```

![alt text](img/08_recetas_cargado.jpg)

Seleccionamos un subconjunto de datos, en este caso la región sanitaria, sexo, código del grupo de recetas y el número de recetas:

```python
data = data.select("regió sanitària", "sexe", "codi del grup ATC nivell 3", "nombre de receptes")
data.show(20)
```

![alt text](img/09_recetas_desagregado.jpg)

Agregamos la cantidad de recetas emitidas por cada región:

```python
data.groupby("codi del grup ATC nivell 3","sexe","nombre de receptes").agg({'nombre de receptes': 'sum'}).orderBy("codi del grup ATC nivell 3").show(10)
```

![alt text](img/09_recetas_agregado_region.jpg)

Y volvemos a agregar la información según la cantidad de recetas emitidas por cada sexo:

```python
data = data.groupby("sexe").agg({'sum(nombre de receptes)': 'sum'})
data.show(10)
```
![alt text](img/09_recetas_agregado_sexo.jpg)

Finalmente, podemos graficar esta información enriquecida utilizando plotly:

```python
dataFrame = data.toPandas()

fig = go.Figure(go.Bar(
    x=dataFrame['sexe'],
    y=dataFrame['sum(sum(nombre de receptes))'],
    marker_color='indigo'
))
fig.update_layout(title="Recetas totales emitidas por sexo", xaxis_title="Sexo", yaxis_title="Num. Recetas")
plot(fig, filename='recetas_por_sexo.html')
```

![alt text](img/10_recetas_grafico_total.jpg)

Y detenemos Spark:

```python
spark.stop()
```

---

## Conclusiones

La utilización de Spark sobre Docker facilita la creación y gestión de clústeres para el procesamiento distribuido de datos, permitiendo escalar recursos de manera sencilla y reproducible. No tuve mayores inconvenientes, la práctica sobre jupyter es muy fluida despues de haber trabajado en spyder. El entorno Jupyter integrado mejora la experiencia de análisis y visualización, aún cuando trabajar sobre una máquina virtual es un poco tedioso por el delay de las acciones (e ingresar los acentos graves del catalán, que no me los tomaba desde mi teclado local), pero sin dudas voy a portar esta práctica a mi setup local. Tengo una computadora en desuso que incluso estoy pensando en destinar como worker para hacer unos experimentos.

---

## Referencias

Todos los scripts utilizados y el código fuente de los informes se pueden encontrar en [mi repositorio personal](https://github.com/santiagohenn/big-data-uab/).

---
