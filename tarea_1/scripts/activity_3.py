import pandas as pd
import os
import matplotlib.pyplot as plt

# Leer el dataset:
current_path = os.path.dirname(__file__)
parent_path = os.path.dirname(current_path)
file_path = os.path.join(parent_path, 'datasets', 'casos_covid_catalunya.csv')
df = pd.read_csv(file_path)

# Agrupar por comarca
result = df.groupby(['ComarcaDescripcio', 'TipusCasDescripcio'])['NumCasos'].sum().unstack(fill_value=0)

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

# Crear un diccionario inverso para mapear comarca a región sanitaria
comarca_to_region = {}
for region, comarcas in sanitary_regions.items():
    for comarca in comarcas:
        comarca_to_region[comarca] = region

# Añadir columna de región sanitaria al DataFrame original
df['SanitaryRegion'] = df['ComarcaDescripcio'].map(comarca_to_region)

# Agrupar por región sanitaria y sexo
result = df.groupby(['SanitaryRegion', 'TipusCasDescripcio'])['NumCasos'].sum().unstack(fill_value=0)

# Graficar los resultados en un gráfico de barras apiladas (stacked columns)
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(8, 5))

colors = plt.cm.Set2.colors  # Paleta amigable para daltónicos

result.plot(
    kind='bar',
    stacked=True,  # Activar columnas apiladas
    ax=ax,
    width=0.7,
    color=colors,
    edgecolor='black'
)

ax.set_xlabel('Región Sanitaria', fontsize=15, labelpad=12)
ax.set_ylabel('Cantidad de Tests', fontsize=15, labelpad=12)
ax.set_title('Tipos de Test por Región Sanitaria', fontsize=17, pad=18)
ax.tick_params(axis='x', rotation=50, labelsize=11)
ax.tick_params(axis='y', labelsize=13)
ax.legend(title='Tipo de Test', fontsize=12, title_fontsize=11, loc='upper right', frameon=False)

# Centrar etiquetas de x bajo las barras
ax.set_xticks(ax.get_xticks())
ax.set_xticklabels(result.index, ha='center')

# Limpiar bordes superiores y derechos
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Solo grid en eje y
ax.yaxis.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)
ax.xaxis.grid(False)

plt.tight_layout()
plt.savefig('tarea_1/img/casos_covid_por_region.jpg', bbox_inches='tight', dpi=300)
plt.show()

# Resultados en números
print(result)
