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
from pyspark.sql.functions import col

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("RecetasCatalunya")\
        .getOrCreate()

    # Leer el archivo csv de recetas
    lines = spark.read.option("header","true").csv("/home/adminp/archivos/recetas_catalunia.csv")

    # Seleccionar columnas relevantes
    myDF = lines.select("grup d'edat", "sexe", "import íntegre")

    # Convertir import íntegre a float
    myDF = myDF.withColumn("import íntegre", col("import íntegre").cast("float"))

    # Agrupar por grupo de edad y sexo, sumar el gasto total
    aggDF = myDF.groupby("grup d'edat", "sexe").agg({'import íntegre': 'sum'}).orderBy("grup d'edat")
    agg_data = aggDF.toPandas()

    # Crear gráfico de barras agrupadas por sexo
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

    # Pie chart: total spending by sex
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

    spark.stop()