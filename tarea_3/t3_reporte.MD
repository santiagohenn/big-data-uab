## Tarea 2: Infraestructura software para el procesamiento de Big Data

*Santiago Martín Henn* | *santiagohenn@unc.edu.ar* | [GitHub](http://github.com/santiagohenn/big-data-uab/).

### Objetivo



---

### Actividad 1

![img](img/01_create_VM.jpg)


```Dockerfile
FROM python:3.12-slim-bookworm
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get dist-upgrade -y && apt-get install --only-upgrade -y python3 && pip install --upgrade pip && pip install --trusted-host pypi.python.org -r requirements.txt && apt-get clean && rm -rf /var/lib/apt/lists/*
CMD ["python", "app.py"]
```


---

## Conclusiones



---

## Referencias

Todos los scripts utilizados y código fuente de los informes se pueden encontrar en [mi repositorio personal](github.com/santiagohenn/big-data-uab/).

---