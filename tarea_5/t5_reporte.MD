## Tarea 5: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](http://github.com/santiagohenn/big-data-uab/).

### Objetivo

Analizar, evaluar y discutir una prueba de concepto de Spark.

---

### Actividad 1: Familiarización con Spark

Creamos una máquina virtual utilizando la imagen BigDataSparkV2.0 con 8 GB de RAM y 20 GB de disco. Trabajamos con Spyder:

```bash
spyder
```

Spyder se conecta automáticamente con el kernel de Python, permitiendo su uso interactivo en la consola (¡muy útil!).

![img](img/00_deploying_spyder.jpg)

Descargamos los archivos Python del aula virtual, descomprimimos la carpeta y cargamos los scripts `wordcount-DF-registre.py`, `wordcount-DF-registre-plotly.py` y `wordcount-DFvacu.py` en la IDE. Ejecutamos `wordcount-DF-registre.py` y corroboramos que todo se ejecuta correctamente:

![img](img/01_testing_spyder.jpg)

Ejecutamos `wordcount-DF-registre-plotly.py`, instalando previamente las dependencias plotly y pandas (las instalamos de forma global, ya que la VM se utiliza solo para esto):

```bash
pip install plotly
pip install pandas
```

Al ejecutar, obtenemos un gráfico de la cantidad de casos positivos de Covid desagregados por comarca:

![img](img/02_covid_casos_por_comarca.jpg)

Explorando un poco más, podemos obtener esta información desagregada por sexo:

```python
grouped = myDF.groupby("ComarcaDescripcio", "SexeDescripcio").agg({'NumCasos': 'sum'}).orderBy("ComarcaDescripcio")
data = grouped.toPandas()
fig = go.Figure()
for sex in data['SexeDescripcio'].unique():
    subset = data[data['SexeDescripcio'] == sex]
    fig.add_trace(go.Bar(x=subset['ComarcaDescripcio'], y=subset['sum(NumCasos)'], name=sex))
fig.update_layout(title="Covid-19 Cases by Comarca and Sex", barmode='group')
plot(fig, filename='cases_by_comarca_and_sex.html')
```

![img](img/03_covid_casos_por_comarca_sexo.jpg)

También es posible visualizar la distribución de tipos de test efectuados:

```python
grouped = lines.groupby("TipusCasDescripcio").agg({'NumCasos': 'sum'})
data = grouped.toPandas()
fig = go.Figure(go.Pie(labels=data['TipusCasDescripcio'], values=data['sum(NumCasos)']))
fig.update_layout(title="Distribution of Covid-19 Case Types")
plot(fig, filename='case_type_distribution.html')
```

![img](img/04_covid_tipos_de_test.jpg)

La primera conclusión parcial es la facilidad con la que estas herramientas permiten analizar y graficar datos, generando visualizaciones interactivas de gran calidad.

A continuación, incluimos algunos gráficos en el script `wordcount-DF-vacu.py` para visualizar los datos sobre fabricantes de vacunas:

```python
data = myDV.toPandas()

fig = go.Figure(go.Bar(
    x=data['FABRICANT'],
    y=data['sum(RECOMPTE)'],
    marker_color='indigo'
))
fig.update_layout(title="Total Vaccinations by Manufacturer", xaxis_title="Manufacturer", yaxis_title="Total Doses")
plot(fig, filename='vaccinations_by_manufacturer.html')
```

![img](img/05_vacunas_fabricantes.jpg)

También obtenemos datos de interés como la cantidad de población con 1 o 2 dosis, desagregada por sexo:

```python
dose_sexDF = lines.select("DOSI", "SEXE", "RECOMPTE")
dose_sexDF = dose_sexDF.groupby("DOSI", "SEXE").agg({'RECOMPTE': 'sum'}).orderBy("DOSI")
dose_sex_data = dose_sexDF.toPandas()

fig_dose_sex = go.Figure()
for sex in dose_sex_data['SEXE'].unique():
    subset = dose_sex_data[dose_sex_data['SEXE'] == sex]
    fig_dose_sex.add_trace(go.Bar(
        x=subset['DOSI'],
        y=subset['sum(RECOMPTE)'],
        name=sex
    ))
fig_dose_sex.update_layout(
    title="Total Population by Number of Doses and Sex",
    xaxis_title="Dose Count",
    yaxis_title="Total People",
    barmode='group'
)
plot(fig_dose_sex, filename='population_by_dose_and_sex.html')
```

![img](img/06_dosis_por_sexo.jpg)

Se observa que existe un porcentaje de población que no ha recibido un refuerzo de la vacuna, y este fenómeno no parece estar exacerbado por el sexo.

### Actividad 2: Más procesamiento con Spark

Nos planteamos la pregunta: ¿Cómo es el gasto en medicamentos para hombres y mujeres (biológicos, según la base de datos)? Obtenemos la información por rango etario y sexo, y la graficamos:

```python
lines = spark.read.option("header","true").csv("/home/adminp/archivos/recetas_catalunia.csv")

myDF = lines.select("grup d'edat", "sexe", "import íntegre")

from pyspark.sql.functions import col
myDF = myDF.withColumn("import íntegre", col("import íntegre").cast("float"))

aggDF = myDF.groupby("grup d'edat", "sexe").agg({'import íntegre': 'sum'}).orderBy("grup d'edat")
agg_data = aggDF.toPandas()

fig = go.Figure()
for sex in agg_data['sexe'].unique():
    subset = agg_data[agg_data['sexe'] == sex]
    fig.add_trace(go.Bar(
        x=subset["grup d'edat"],
        y=subset["sum(import íntegre)"],
        name=sex
    ))
fig.update_layout(
    title="Total Medication Spending by Age Group and Sex",
    xaxis_title="Age Group",
    yaxis_title="Total Spending (€)",
    barmode='group'
)
plot(fig, filename='spending_by_age_and_sex.html')
```

El gráfico resultante:

![img](img/07_gastos_por_sexo.jpg)

Se observa cierta disparidad en el gasto según el rango etario: entre los 50 y los 74 años los hombres gastan más en medicamentos, mientras que a partir de los 75 años las mujeres adquieren mayor relevancia. Esto puede explicarse, en parte, por la mayor esperanza de vida femenina respecto a la masculina, aunque no es objetivo de este trabajo profundizar en ese aspecto. Podemos agregar la información total por género para ver el porcentaje de gasto total en todas las recetas emitidas por sexo:

```python
pieDF = myDF.groupby("sexe").agg({'import íntegre': 'sum'})
pie_data = pieDF.toPandas()

fig_pie = go.Figure(go.Pie(
    labels=pie_data['sexe'],
    values=pie_data['sum(import íntegre)'],
    hole=0.3
))
fig_pie.update_layout(
    title="Total Medication Spending by Sex"
)
plot(fig_pie, filename='spending_by_sex_pie.html')
```

Obteniendo:

![img](img/08_gastos_total_por_sexo.jpg)

Se observa que un 52% del mercado es femenino, un 47.5% masculino, dejando un 0.5% sin especificar y un 0.01% no identificado en el binarismo M/F.

---

## Conclusiones

El análisis realizado demuestra la capacidad de Spark y Plotly para procesar y visualizar grandes volúmenes de datos de manera eficiente, flexible y bastante estética: el dataset de las recetas tiene más de un gigabyte y entre proceso y gráfico fueron unos pocos segundos!. Pudimos, con relativamente pocas líneas de código, obtener información sobre vacunación, cantidad de dosis, gastos en medicamentos desagregada por sexo, en las distintas actividades. Nunca había utilizado Spyder (en general uso VSC), la interfáz me gustó mucho, seguramente considere utilizarla en la PC que destino a dar clases donde voy a instalar un Debian para reemplazar el lentísimo Windows que tiene en este momento.

---

## Referencias

Todos los scripts utilizados y el código fuente de los informes se pueden encontrar en [mi repositorio personal](https://github.com/santiagohenn/big-data-uab/).

---