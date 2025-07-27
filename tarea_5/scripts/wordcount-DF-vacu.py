#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#import sys
#from operator import add

from pyspark.sql import SparkSession
import plotly.graph_objs as go
from plotly.offline import plot

if __name__ == "__main__":
#    if len(sys.argv) != 2:
#        print("Usage: wordcount <file>", file=sys.stderr)
#        sys.exit(-1)

    spark = SparkSession\
        .builder\
        .appName("PythonWordCount")\
        .getOrCreate()

    # Leer el archivo csv bajado de Gencat sobre vacuanaciones Covid-19
    lines = spark.read.option("header","true").csv("/home/adminp/archivos/vacu.csv")
    #lines.show(20)
    
    # Seleccionar columnas
    myDF = lines.select("COMARCA", "MUNICIPI", "FABRICANT", "RECOMPTE")
    #myDF.show()
    #myDF.printSchema()
    # Agrupar por Comarca y frabicante sumados, ordenados por comarca y mostrar
    myDF.groupby("COMARCA", "FABRICANT").agg({'RECOMPTE': 'sum'}).orderBy("COMARCA").show(myDF.count())

    # Crear un nuevo DF con fabricante y la suma
    myDV = myDF.groupby("FABRICANT").agg({'RECOMPTE': 'sum'})
    
    # ordenarlo y mostrar.
    myDV.sort("sum(RECOMPTE)").show()
   
    # Convertir a pandas para plotly
    data = myDV.toPandas()

    # Crear gráfico de barras
    fig = go.Figure(go.Bar(
        x=data['FABRICANT'],
        y=data['sum(RECOMPTE)'],
        marker_color='indigo'
    ))
    fig.update_layout(title="Total Vaccinations by Manufacturer", xaxis_title="Manufacturer", yaxis_title="Total Doses")
    plot(fig, filename='vaccinations_by_manufacturer.html')

    # Agrupar por número de dosis y sumar el total de personas

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

    spark.stop()
