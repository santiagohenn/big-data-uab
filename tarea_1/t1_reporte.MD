## Tarea 1: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](github.com/santiagohenn/big-data-uab/).

### Objetivo

Analizar, evaluar y discutir una prueba de concepto de que podrían ser una
muestra de Big Data (aunque se trabajara con datos grandes la conclusiones son válidas
para la discusión).

---

### Actividad 1

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

---

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

El objetivo de este análisis es investigar la relación entre la cantidad de recetas de preparados de hormona tiroidea por habitante y la ingesta de yodo en distintas regiones de Catalunya. La ingesta de yodo está directamente relacionada con la cantidad de yodo presente en la dieta, la cual depende en gran medida de la ubicación geográfica y la cercanía al mar [1,2]. Si bien las poblaciones son bastante dispares, resulta interesante encontrar que en la región de los Pirineos hay 3.54% más de recetas por habitante que en la región de Barcelona.

---

### Actividad 3

Para esta actividad, el dataset provisto desagrega la información de tipos de PCR por comarca, y no por región sanitaria. Primero agregamos la información por comarca. Esto nos da la suma de casos para cada tipo de test distinto, por comarca. Luego construímos un dataset de comarcas por región sanitaria (en este caso en forma de diccionario):

```python
sanitary_regions = {
    "Lleida": {"NOGUERA", "PLA D'URGELL", "URGELL", "SEGARRA", "GARRIGUES", "SEGRIA"},
    "Alt Pirineu I D'ARAN": {"ALT URGELL", "PALLARS SOBIRA", "PALLARS JUSSA", "ALTA RIBAGORÇA", "CERDANYA", "VALL D'ARAN"},
    "Catalunya Central": {"ANOIA", "BAGES", "BERGUEDA", "MOIANÈS", "OSONA", "SOLSONES"},
    "Girona": {"ALT EMPORDA", "BAIX EMPORDA", "GARROTXA", "GIRONES", "PLA DE L'ESTANY", "RIPOLLES", "SELVA"},
    "Ambit Metropolita Nord": {"MARESME", "VALLES OCCIDENTAL", "VALLES ORIENTAL"},
    "Barcelona Ciutat": {"BARCELONES"},
    "Ambit Metropolita Sud": {"ALT PENEDES", "BAIX LLOBREGAT", "GARRAF"},
    "Camp de Tarragona": {"ALT CAMP", "BAIX CAMP", "BAIX PENEDES", "CONCA DE BARBERA", "PRIORAT", "TARRAGONES"},
    "Terres de L'Ebre": {"BAIX EBRE", "MONTSIA", "RIBERA D'EBRE", "TERRA ALTA"}
}
```

En el siguiente mapa podemos las comarcas agrupadas por cada región sanitaria:

![Caption](img/regiones_sanitarias.png)

Los resultados obtenidos para cada región, procesados con pandas y matplotlib:

![Caption](img/casos_covid_por_region.jpg)

Podemos ver que el test TAR (Test Rápido de Antígenos) ocupa el primer lugar, siendo el test más efectuado sin importar la región. El segundo lugar lo ocupa el test PCR (reacción en cadena de polimerasa). El tercer lugar son tests ELISA (Ensayo por Inmunoabsorción Ligado a Enzimas). Los otros tipos de test se efectuaron en un número órdenes de magnitud menor que estos.

---

### Actividad 4

En primer lugar se descargó y adecuó el dataset de casos confirmados por país del link propuesto por el trabajo: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/
csse_covid_19_time_series. Esta adecuación fue necesaria para asignar los códigos de dos dígitos de cada país a la fila correspondiente, además de eliminar a mano algunas filas de datos no pertinentes (datos sobre los contagios en las olimpiadas 2022 y en un crucero). 

El CSV con los datos se cargó a la página propuesta y se visualizaron los casos en una escala de colores con 9 segmentos:

![Caption](img/mapa_captura.png)

Fué necesario resolver algunos Bugs en el aplicativo, que no resultó demasiado intuitivo de utilizar. No fué posible añadir una leyenda. Los datos de casos totales, al ser un número absoluto, no transmiten información sobre incidencia como lo haría un análisis porcentual sobre población total, que no se realiza por una cuestión de tiempo.  

---

## Conclusiones

El trabajo realizado permitió explorar y analizar datasets de datos sanitarios utilizando herramientas de procesamiento y visualización, tanto las provistas en los aplicativos que nos brindó el docente, como utilizando pandas y matplotlib (herramientas propias del estudiante). Según lo discutido en clase, estos datasets no caen dentro de lo que podríamos categorizar como "big data", no obstante, son archivos pesados para lo que cotidianamente estaríamos acostumbrados si no trabajamos cerca de la ciencia de datos. No es trivial trabajar con un CSV de 100Mb, o planillas con cerca de un millón de filas: la forma en la que se procesan los datos empieza a notarse cuando uno ejecuta un script.

Se aprovechó la oportunidad del trabajo para tratar de identificar algunos patrones interesantes, como el aumento sostenido en la prescripción de antidepresivos en adolescentes y jóvenes (con un claro pico en la época de la pandemia de 2020-2022), y la disparidad de consumo de hormona tiroidea entre hombres y mujeres, y entre en diferentes regiones. El autor padece de hipotiroídismo y escuchó alguna vez acerca de estos últimos datos, por lo que fué interesante analizar algunas evidencias de ello.

Se identificaron limitaciones en la herramienta de visualización para la Actividad 4, como la dificultad para añadir leyendas o trabajar con datos relativos a la población, resultando clara la necesidad de complementar los análisis absolutos con indicadores normalizados, y explorar como resolver algunas cosas del aplicativo (que se sospecha tienen que ver con el navegador).

---

## Referencias

Todos los scripts utilizados y código fuente de los informes se pueden encontrar en [mi repositorio personal](github.com/santiagohenn/big-data-uab/).

[1] Vila L, Castell C, Wengrovicz S, de Lara N, Casamitjana R. "Urinary iodide assessment of the adult population in Catalonia." *Med Clin (Barc)*. 2006;127:730–3.

[2] Vila L, Serra-Prat M, de Castro A, Palomera E, Casamitjana R, Legaz G, Barrionuevo C, Muñoz JA, García AJ, Lal-Trehan S, García A, Durán J, Puig-Domingo M. "Iodine nutritional status in pregnant women of two historically different iodine-deficient areas of Catalonia, Spain." *Nutrition*. 2011;27(10):1029-1033. [https://doi.org/10.1016/j.nut.2010.11.012](https://doi.org/10.1016/j.nut.2010.11.012)
