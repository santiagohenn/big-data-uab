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

import sys
from operator import add

from pyspark.sql import SparkSession


if __name__ == "__main__":

    spark = SparkSession\
        .builder\
        .master("local[6]")\
        .appName("PythonWordCount DF")\
        .getOrCreate()

    # Leer el archivo de datos de Gencat sobre registros de positivos Covid-19
    lines = spark.read.option("header","true").csv("/home/adminp/archivos/regi.csv")
    #lines.show(20)
    
    # Selección de las columnas a procesar y creación de DF
    myDF = lines.select("ComarcaDescripcio", "NumCasos", "SexeDescripcio")
    
    #Mostrar las primera 20 filas
    #myDF.show(20)
    
    # Imprimir el Schema del DF
    #myDF.printSchema()

    # Agrupar por ComarcaDescripcio, Contar el NumCasos, Ordenaar y mostrar
    myDF.groupby("ComarcaDescripcio").agg({'NumCasos': 'sum'}).orderBy("ComarcaDescripcio").show(myDF.count())
    
    # Agrupar por dos condiciones
    #myDF.groupby("ComarcaDescripcio", "SexeDescripcio").agg({'NumCasos': 'sum'}).orderBy("ComarcaDescripcio").show(myDF.count())
    

    #Crear un nuevo DF y guardar el resultado como csv. 
    #myDFfinal = myDF.groupby("ComarcaDescripcio").agg({'NumCasos': 'sum'}).orderBy("ComarcaDescripcio")
    #myDFfinal.write.mode("overwrite").format("csv").save("/home/adminp/archivos/results")
    

    spark.stop()
