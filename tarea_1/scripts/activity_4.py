import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'time_series_covid19_confirmed_global.csv')
df = pd.read_csv(csv_path)

# Drop de las columnas que no me interesan
df = df.drop(['Lat', 'Long'], axis=1)

# Sumar todas las columnas después de la tercera (incluida)
suma_casos = df.iloc[:, 2:].sum(axis=1)

# Drop las columnas despues de la tercera (incluida)
df = df.iloc[:, :2]

# agrego la columna con la suma de casos
df['suma_casos'] = suma_casos

agregado_datos = df.groupby('Country/Region')['suma_casos'].sum().reset_index()

# Guardar el DataFrame como CSV en la carpeta /datasets/
# output_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'agregado_datos.csv')
# agregado_datos.to_csv(output_path, index=False)

# Controlar el agregado de datos
# print(agregado_datos.head())