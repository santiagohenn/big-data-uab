import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'covid_casos_por_pais.csv')
df = pd.read_csv(csv_path)
df.iloc[:, 1] = df.iloc[:, 1] / 1e6

# Guardar el DataFrame como CSV en la carpeta /datasets/
output_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'covid_casos_por_pais_procesado.csv')
df.to_csv(output_path, index=False)

# Controlar el agregado de datos
# print(agregado_datos.head())