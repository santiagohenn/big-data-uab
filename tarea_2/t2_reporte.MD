## Tarea 2: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](github.com/santiagohenn/big-data-uab/).

### Objetivo

Analizar, evaluar y discutir una prueba de concepto de contenedores como
muestra de plataformas de virtualización y como encapsular aplicaciones y disponer de
escalabilidad horizontal.

---

### Actividad 1

#### Desplegar la maquina virtual


docker build --tag=app .
docker images

REPOSITORY TAG IMAGE ID
App latest 326387cea398

docker run -d -p 8080:8080 app

---

## Conclusiones



---

## Referencias

Todos los scripts utilizados y código fuente de los informes se pueden encontrar en [mi repositorio personal](github.com/santiagohenn/big-data-uab/).