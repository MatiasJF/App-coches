



# Herramienta de Búsqueda de Coches de Segunda Mano

Esta herramienta es una aplicación que permite buscar coches de segunda mano en sitios web populares como coches.com y wallapop. Proporciona visualizaciones de datos y la capacidad de asignar puntajes a los coches para agregar valor a los datos.

## Cómo Funciona

La herramienta recopila datos de coches de segunda mano de varios sitios web utilizando técnicas de web scraping. Luego, estos datos se procesan y se muestran en una interfaz de usuario amigable. Los usuarios pueden filtrar y buscar coches según sus preferencias y ver visualizaciones de datos para ayudar en su decisión de compra.

Además, los usuarios tienen la opción de asignar puntajes a los coches en función de diferentes criterios como precio, kilometraje, año, etc. Estos puntajes se utilizan para clasificar y destacar los coches que mejor se ajusten a las preferencias del usuario.

## Requisitos

- Python 3.9: [Descargar](https://www.python.org/downloads/)
- pip (se incluye con la instalación de Python)

## Instalación

1. Clona este repositorio en tu máquina local:

```bash
git clone https://github.com/MatiasJF/app-coches.git
cd backend
```

2. Crear un entorno virtual

# En Windows
```bash
python -m venv venv
```

# En Mac/Linux
```bash
python3 -m venv venv
```
3. Activar el entorno virtual

# En Windows
```bash
venv\Scripts\activate
```

# En Mac/Linux
```bash
source venv/bin/activate
```
4. Dirigirse a la carpeta backend e instalar las librerias necesarias
```bash
cd backend
pip install -r requirements.txt
```

5. Ejecutar el archivo
```bash
python main.py
```




