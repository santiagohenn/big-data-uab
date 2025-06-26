import pandas as pd
import os
import matplotlib.pyplot as plt

# Leer el dataset:
current_path = os.path.dirname(__file__)
parent_path = os.path.dirname(current_path)
file_path = os.path.join(parent_path, 'datasets', '2024_hormona_tiroidea.csv')
df = pd.read_csv(file_path)

# Agrupar por region y sexo 
result = df.groupby(['codi de la regio sanitaria', 'sexe'])['nombre de receptes'].sum().unstack(fill_value=0)

# Graficar los resultados en un gráfico de barras agrupadas (columnas dobles)
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(8, 5))

# Filtrar solo las regiones 75, 76 y 79
filtered_result = result.loc[["75", "76", "79"]]

filtered_result.plot(
    kind='bar',
    ax=ax,
    width=0.8
)

ax.set_xlabel('Region sanitaria', fontsize=14, labelpad=10)
ax.set_ylabel('Numero de recetas', fontsize=14, labelpad=10)
ax.set_title('Recetas por región', fontsize=16, pad=15)
ax.tick_params(axis='x', rotation=45, labelsize=12)
ax.tick_params(axis='y', labelsize=12)
ax.legend(title='Sexo')

# Remove top and right spines for a cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('tarea_1/img/tiroides_por_region.jpg', bbox_inches='tight')
plt.show()

# Resultados en números
print(result)
