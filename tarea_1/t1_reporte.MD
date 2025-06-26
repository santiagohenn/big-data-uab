# Tarea 1

### Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar*

### Objetivo

Analizar, evaluar y discutir una prueba de concepto de que podrían ser una
muestra de Big Data (aunque se trabajaran con datos grandes la conclusiones son válidas
para la discusión).

---

### Actividad 1

Considere el archivo los datos abiertos de la Generalitat de Catalunya y la recetas de
medicamentos dispensadas por el sistema publico de salud y analice con las herramientas
propias de la plataforma que tipo de medicamentos es el más vendido en 2024 para
hombres y para mujeres. Realice por lo menos un par de preguntas más y obtenga la
respuestas de los datos.

#### ¿Cuáles son los medicamentos más vendidos durante 2024 para hombres y para mujeres?

Consultando la herramienta de visualización, configurando como dimensión *Codi del grup ATC nivell 3* (desagregación de tercer nivel para el código del medicamento), tomando la suma de recetas emitidas y filtrando para el año 2024, obtenemos que el código N02B con algo mas de 14 millones de recetas se encuentra encabezando el ranking.

![Caption](img/ranking_2024.jpg)

Consultando los datasets vemos que la categoría N02B corresponde a "Otros Analgésicos y Antipiréticos (antifebriles)". Por ejemplo: 

| Código nivel 4 | Tipo                          | Ejemplo      |
|----------------|-------------------------------|--------------|
| N02BA          | Ácido salicílico y derivados  | Aspirina     |
| N02BB          | Pirazolonas                   | Dipirona     |
| N02BE          | Anilidas                      | Paracetamol  |

En segundo lugar tenemos al grupo C10A, correspondiente a medicamentos relacionados al sistema cardiovascular, en particular estatinas para reducir el colesterol en sangre y en tercer lugar tenemos al grupo N06A, correspondiente a formulaciones utilizadas comúnmente como antidepresivos. 

#### ¿Como evolucionó el consumo de antidepresivos en adolescentes y adultos jóvenes en los últimos años?

Tomando la cantidad de recetas de antidepresivos emitidas para el rango de años 2016-2024 y filtrando para el rango etario entre 14 y 24 años, podemos observar que la cantidad de recetas incrementó mas del 200% en un lapso de 9 años:

![Caption](img/N06A_2016_2024.jpg)

El gráfico evidencia un incremento en la derivada temporal para el rango 2020-2022, correspondiente a los peores años de la pandemia de COVID-19.

#### ¿Cómo es el consumo desagregado por hombres y mujeres de hormona tiroidea en la región de Barcelona?

Desagregando por género y filtrando para las tres regiones sanitarias que componen Barcelona, podemos observar una fuerte disparidad entre la cantidad de recetas de hormona tiroidea para hombres y mujeres:

![Caption](img/tiroidismo_BCN.jpg)

### Actividad 2

Para descargar los datasets y realizar el análisis fuera del aplicativo web, recurrimos a reducir la cantidad de datos a lo estrictamente necesario para la actividad. Al exportar los datos hay mucha información redundante e innecesaria para los análisis numéricos (por ejemplo, tener el código de la región y además el nombre de la región). A su vez, filtramos para incluir datos solamente del año 2024. El dataset es descargado en formato CSV; un extracto del mismo se puede observar a continuación:

```csv
codi ATC nivell 3,codi ATC nivell 4,nombre de receptes,sexe,codi de la regió
A01A,A01AB,2,Dona,79
A01A,A01AB,1,Dona,63
A01A,A01AB,14,Home,75
A01A,A01AB,2,Home,79
...
```

Utilizando python 3.4 y las librerias pandas y matplotlib, podemos realizar el análisis de suma por categoría de medicamente. Ordenando y graficando los primeros 20 del ranking obtenemos el mismo resultado que mediante el aplicativo web:

![Caption](img/ranking_2024_py.jpg)

El ranking, en números:

| Código del medicamento | Cantidad de recetas |
|-----------------------|---------------------|
| N02B                  | 14,216,280          |
| C10A                  | 9,577,425           |
| N06A                  | 9,189,792           |
| A02B                  | 7,854,937           |

Siguiendo un razonamiento similar para el segundo análisis realizado en la Actividad 1, se descargó un dataset filtrado según los datos necesarios. Los resultados se procesaron de forma análoga, utilizando pandas y matplotlib, obteniendo resultados consistentes. También es evidente el aumento del consumo de antidepresivos en adolescentes a lo largo del tiempo, con un incremento notable durante la pandemia de COVID-19:

![Caption](img/N06A_2016_2024_py.jpg)

Para el tercer análisis, primero vamos a descargar el dataset correspondiente y analizarlo de manera análoga a los anteriores. Los resultados son consistentes con lo obtenido anteriormente:

![Caption](img/tiroides_por_region.jpg)

Agregando los datos de Barcelona y utilizando el servicio de datos estadísticos de Catalunya https://www.idescat.cat/indicadors/ podemos obtener la cantidad de habitantes de las regiones de Alt Pirineu i Aran (71) y Barcelona (75, 76, 79), y obtener la relación entre habitantes y recetas de preparados de hormona tiroidea:


| Código de la región | Habitantes | Total de recetas | % Recetas / habitante |
|---------------------|------------|------------------|-----------------------|
| 71                  | 76,543     | 12,799           | 16.72 %               |
| 75 + 76 + 79        | 5,877,672  | 774,480          | 13.17 %               |

El objetivo de este análisis es investigar la posible relación entre la cantidad de recetas de preparados de hormona tiroidea por habitante y la ingesta de yodo en distintas regiones de Catalunya. La ingesta de yodo está directamente relacionada con la cantidad de yodo presente en la dieta, la cual depende en gran medida de la ubicación geográfica y la cercanía al mar [1,2]. Si bien las poblaciones son bastante dispares, resulta interesante encontrar que en la región de los Pirineos hay 3.54% más de recetas por habitante que en la región de Barcelona.



## Referencias

[1]: Vila L, Castell C, Wengrovicz S, de Lara N, Casamitjana R. "Urinary iodide assessment of the adult population in Catalonia." *Med Clin (Barc)*. 2006;127:730–3.

[2]: Vila L, Serra-Prat M, de Castro A, Palomera E, Casamitjana R, Legaz G, Barrionuevo C, Muñoz JA, García AJ, Lal-Trehan S, García A, Durán J, Puig-Domingo M. "Iodine nutritional status in pregnant women of two historically different iodine-deficient areas of Catalonia, Spain." *Nutrition*. 2011;27(10):1029-1033. [https://doi.org/10.1016/j.nut.2010.11.012](https://doi.org/10.1016/j.nut.2010.11.012)
