import sys

# Diccionario para codificar las pruebas
prueba_codigos = {
    "Positiu per Test Ràpid": "PTR",
    "PCR probable": "PCRP",
    "Epidemiològic": "E",
    "Positiu per ELISA": "PPE",
    "Positiu PCR": "PPCR",
    "Positiu TAR": "PTAR"
}

with open("./test_data/casos_covid.csv", "r", encoding="utf-8") as f:
    casos_covid_data = f.read()

for line in casos_covid_data.splitlines():
# for line in sys.stdin:
    line = line.strip()
    words = line.split(",")
    if len(words) < 10:
        continue  # skip incomplete lines

    prueba = words[9]
    codigo_prueba = prueba_codigos.get(prueba, "OTRO")

    comarca = words[2].replace(" ", "_")
    comarca_codigo = f"{comarca}_{codigo_prueba}"

    try:
        num_casos = int(words[10])
    except ValueError:
        continue  # skip lines with invalid case numbers

    # with open("test_data/procesado.txt", "a", encoding="utf-8") as f:
    #     for _ in range(num_casos):
    #         output_line = f"{comarca_codigo}\t1{num_casos}\n"
    #         f.write(output_line)

    with open("test_data/procesado_2.txt", "a", encoding="utf-8") as f:
        for _ in range(num_casos):
            output_line = f"{comarca_codigo}\t{1}\n"
            f.write(output_line)

# 0         ,1 ,2                ,3    ,4                   ,5,6             ,7,8   ,9                ,10
# 12/11/2020,40,VALLES OCCIDENTAL,08266,CERDANYOLA DEL VALLÈS,,No classificat,1,Dona,Positiu per ELISA,1