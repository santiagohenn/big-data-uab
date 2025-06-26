import pandas as pd
import os
import matplotlib.pyplot as plt

# Leer el dataset:
current_path = os.path.dirname(__file__)
parent_path = os.path.dirname(current_path)
file_path = os.path.join(parent_path, 'datasets', '2024_recetas_facturadas.csv')
df = pd.read_csv(file_path)

# Agrupar por 'codi del grup ATC nivell 3' y sumar 'nombre de receptes'
result = df.groupby('codi del grup ATC nivell 3')['nombre de receptes'].sum()

# Ordenar los resultados en orden descendente y truncar a los primeros 20 valores
result = result.sort_values(ascending=False).head(20)

# Graficar los resultados en un gráfico de barras
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(6, 4))

bars = result.plot(
    kind='bar',
    ax=ax,
    color='#4B8BBE',
    edgecolor='black',
    width=0.8
)

ax.set_xlabel('Código del medicamento (N3)', fontsize=14, labelpad=10)
ax.set_ylabel('Número de recetas', fontsize=14, labelpad=10)
# ax.set_title('Suma de receptes per grup ATC nivell 3', fontsize=16, pad=15)
ax.tick_params(axis='x', rotation=45, labelsize=12)
ax.tick_params(axis='y', labelsize=12)

# Remove top and right spines for a cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('atc_nivell3_receptes.png', bbox_inches='tight')
plt.show()

# Resultados en números
print(result)