#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  13 2024

@author: adminp
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot

#spark = SparkSession.builder.appName("Recetas").getOrCreate()
spark = SparkSession.builder.master("local[*]").getOrCreate()

# Abrir el archivo , mirar el esquema 
recetas = spark.read.option("inferSchema","true").option("header","true").csv("/home/adminp/Downloads/recetas24.csv")
#recetas.printSchema()
#recetas.show()

# Reorganizo el DataFrame y selecciono las columnas que interesan:
recetas2 = recetas.select(recetas["regió sanitària"].alias("rsanitaria"), recetas["sexe"].alias("sexe"), recetas["grup ATC nivell 4"].alias("medicamento"), recetas["nombre de receptes"].alias("nrecetas"),recetas["import íntegre"].alias("importe") )
#recetas2.show()

# Responder a preguntas directamente del dataframe 
# Cuantas regiones sanitarias diferentes hay y cuantos medicamentos diferents se han dispensado?
recetas2.select("rsanitaria").distinct().show()
med = recetas2.select("medicamento").distinct().count()
print("Nro de medicamentos diferentes dispensados", med)

# Cuantas recetas se han dispensado?  
recetas2.groupBy("medicamento").agg(sum("nrecetas").alias("sum_recetas")).orderBy(col("sum_recetas").desc()).show(50, False)

DFFinal = recetas2.groupBy("medicamento").agg(sum("nrecetas").alias("sum_recetas")).orderBy(col("sum_recetas").desc())

data = DFFinal.toPandas().head(30)
#print(data)
data2 = px.bar(x=data.medicamento, y=data.sum_recetas, labels={"x":"Medicamento", "y":"Nro recetas"})
fig = go.Figure(data2, layout_title_text="Nro de recetas dispensadas por medicamento")
plot(fig, filename='plot.html')

#Ref: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/index.html 
#SQL Syntax: https://spark.apache.org/docs/latest/sql-ref-syntax.html 
#Spark-SQL  utilitzant l’API
#Crear una taula temporal: 

recetas2.createOrReplaceTempView("my_table")

#Crear una sentencia SQL: 
spark.sql("SELECT * FROM my_table WHERE sexe = 'Dona'").show()

#Mostrar l’schema de la taula:
spark.sql("DESCRIBE my_table").show() 

#Exemples de sentencies Spark-SQL:
consulta_sql = """
SELECT *
FROM my_table
where cast(nrecetas as int) > 8
"""
spark.sql(consulta_sql).show()

#Altre:
consulta_sql = """
SELECT rsanitaria, medicamento, COUNT(*) AS numero_filas, SUM(cast(nrecetas as INT)) AS total_recetas, SUM(cast(importe as INT)) AS total_import
FROM my_table
WHERE medicamento LIKE 'Derivados de la benzodi%'
GROUP BY rsanitaria, medicamento
ORDER BY total_recetas DESC
"""
spark.sql(consulta_sql).show()

spark.stop()