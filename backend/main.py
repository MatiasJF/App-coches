import requests
import pandas as pd
import urllib.parse
import matplotlib.pyplot as plt
import plotly.express as px
from IPython.display import HTML
import webbrowser
import csv
import bcrypt
import asyncio


class User():
    def __init__(self, username, password):
        self.username = username
        self.password = password


def register(user: User):
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        users = list(reader)
    if len(users) != 0:
        for u in users:
            if user.username == u[0]:
                print("Usuario ya registrado")
                return

    # Genera una nueva sal para cada usuario
    salt = bcrypt.gensalt()
    # Hashea la contraseña con la sal
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    with open('users.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user.username, salt, hashed_password])
    print("Usuario registrado")
    return

async def login(user: User):
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        users = list(reader)

    for u in users:
        if user.username == u[0]:
            salt = bytes(u[1], 'utf-8')
            salt = salt.decode('utf-8')[2:-1].encode('utf-8')
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
            u2 = bytes(u[2], 'utf-8')
            u2 = u2.decode('utf-8')[2:-1].encode('utf-8')
            if hashed_password == u2:
                print("Sesión iniciada con éxito")
                await main_function()
                return

            else:
                print("Contraseña incorrecta")
                return
    print("Usuario no registrado")
    return

def transform_data(df_com, df_walla):
    comon_names = ['id','image','price','make','model','year','km','fuelType','horsepower','cv','url']
    rename_columns = {
        'web_slug': 'url',
        'engine': 'fuelType',
        'fuel' : 'fuelType',
        'horsepower': 'cv',
        'brand' : 'make',
        'images': 'image'
    }
    delete_columns = ['title']
    df_walla['images'] = df_walla['images'].apply(lambda x: x[0]['original'] if isinstance(x, list) and len(x) > 0 else None)
    df_walla['web_slug'] = 'https://es.wallapop.com/item/' + df_walla['web_slug'].astype(str)

    df_walla.rename(columns=rename_columns, inplace=True)

    df_walla.drop(columns=delete_columns, inplace=True, errors='ignore')

    df_walla['price'] = df_walla['price'].replace({'€': '', '.': '', ',': '', ' ': ''}, regex=True)
    df_walla['km'] = df_walla['km'].replace({'€': '', '.': '', ',': '', ' ': '' }, regex=True)
    df_walla['price'] = pd.to_numeric(df_walla['price'])
    df_walla['km'] = pd.to_numeric(df_walla['km'])

    df_com.rename(columns=rename_columns, inplace=True)

    df_com.drop(columns=delete_columns, inplace=True, errors='ignore')

    df_com['price'] = df_com['price'].str.replace('€', '').str.replace('.', '').str.replace(',', '.').astype(float)
    df_com['km'] = df_com['km'].str.replace(' km', '').str.replace('.', '').str.replace(',', '.').astype(float)

    df_walla = df_walla[[col for col in comon_names if col in df_walla.columns]]
    df_com = df_com[[col for col in comon_names if col in df_com.columns]]

    df_walla['site'] = 'Wallapop'

    df_com['site'] = 'Coches.com'

    df = pd.concat([df_com, df_walla], ignore_index=True)

    df['year'] = df['year'].fillna(0).astype(int)
    peso_price = 0.5
    peso_km = 0.3
    peso_year = -0.2
    mean_price = df['price'].mean()
    std_price = df['price'].std()
    mean_km = df['km'].mean()
    std_km = df['km'].std()
    mean_year = df['year'].mean()
    std_year = df['year'].std()

    score_price = ((df['price'] - mean_price) / std_price) * peso_price
    score_km = ((df['km'] - mean_km) / std_km) * peso_km
    score_year = ((df['year'] - mean_year) / std_year) * peso_year

    # Suma los valores ponderados
    total_score = score_price + score_km + score_year

    # Escala el resultado para que esté en el rango de 0 a 1
    min_score = total_score.min()
    max_score = total_score.max()
    scaled_score = (total_score - min_score) / (max_score - min_score)

    # Asigna el resultado al DataFrame original
    df['score'] = round(scaled_score,4)
    return df



async def get_data_coches_com(make: str, model: str, yearMin: int, yearMax: int, kmMin: int, kmMax: int, priceMin: int, priceMax: int):
    parametros = {
        'tipo_busqueda': '2',
        'seminuevo': '0',
        'ord[]': 'marca_up',
        'searched3': '',
        'color': '',
        'combustible_id': '',
        'precio_desde': priceMin,
        'precio_hasta': priceMax,
        'scf_fee_desde': '',
        'scf_fee_hasta': '',
        'potencia_desde': '',
        'potencia_hasta': '',
        'km_desde': kmMin,
        'km_hasta': kmMax,
        'anyo_desde': yearMin,
        'anyo_hasta': yearMax,
        'cambio': '',
        'puertas': '',
        'plazas': '',
        'vendedor': '',
        'make_list[]': '',
        'transmission_name': '',
        'agent_type_name': '',
        'has_financing': '',
        'reservable': '',
        'search3': model,
    }
    url_base = 'https://www.coches.com/api/vo/pills/?'
    url_completa = url_base + urllib.parse.urlencode(parametros)
    response = requests.get(url_completa)
    df_com = pd.DataFrame()
    if response.ok:
        try:
            data = response.json()
            df_com = pd.DataFrame(data['pills'])
        except Exception as e:
            print("Error", e)
    return df_com
async def get_data_coches_net(make: str, model: str, yearMin: int, yearMax: int, kmMin: int, kmMax: int, priceMin: int, priceMax: int):
    parametros = {
        'make': make,
        'model': model,
        'yearMin': yearMin,
        'yearMax': yearMax,
        'kmMin': kmMin,
        'kmMax': kmMax,
        'priceMin': priceMin,
        'priceMax': priceMax,
    }
    url_base = 'https://www.coches.net/segunda-mano/coches-ocasion/?'
    url_completa = url_base + urllib.parse.urlencode(parametros)
    response = requests.get(url_completa)
    data = response.json()
    df = pd.DataFrame(data['pills'])
    return df

async def get_data_wallapop(make: str, model: str, yearMin: int, yearMax: int, kmMin: int, kmMax: int, priceMin: int, priceMax: int):
    parametros = {
    'filters_source': 'suggester',
    'keywords': make + ' ' + model,
    'category_ids': 100,
    'longitude': -3.69196,
    'latitude': 40.41956,
    'yearMin': yearMin,
    'yearMax': yearMax,
    'kmMin': kmMin,
    'kmMax': kmMax,
    'priceMin': priceMin,
    'priceMax': priceMax
}
    url_base = 'https://api.wallapop.com/api/v3/cars/search?'
    url_completa = url_base + urllib.parse.urlencode(parametros)
    response = requests.get(url_completa)
    df_walla = pd.DataFrame()
    if response.ok:
        try:
            data = response.json()
            rows = []
            for obj in data['search_objects']:
                row = obj['content']
                rows.append(row)
            df_walla = pd.DataFrame(rows)
        except Exception as e:
            print("Error:", e)
    return df_walla

async def search_car(make: str, model: str, yearMin: int, yearMax: int, kmMin: int, kmMax: int, priceMin: int, priceMax: int):
    df = await get_data_coches_com(make, model, yearMin, yearMax, kmMin, kmMax, priceMin, priceMax)
    df3 = await get_data_wallapop(make, model, yearMin, yearMax, kmMin, kmMax, priceMin, priceMax)
    df = transform_data(df , df3)
    df['price'] = df['price'].apply(lambda x: 'No disponible' if pd.isna(x) else x)
    df['km'] = df['km'].apply(lambda x: 'No disponible' if pd.isna(x) else x)
    df['fuelType'] = df['fuelType'].apply(lambda x: 'No disponible' if pd.isna(x) else x)
    
    return df

def generate_html_file(df_html, scatter_plot_html):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Búsqueda de vehículos</title>
        <style>
        body {{
            background-color: #f0f0f0;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        h1 {{
            text-align: center;
            color: #333;
        }}

        table {{
            width: 80%;
            border-collapse: collapse;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }}

        th,
        td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        th {{
            background-color: #f2f2f2;
        }}

        tr:hover {{
            background-color: #f5f5f5;
        }}

        .scatter-plot {{
            width: 80%;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }}
    </style>

    </head>
    <body>
        <h1>Resultados</h1>
        {df_html}
        <h1>Diagrama de dispersión</h1>
        <div class="scatter-plot">
            {scatter_plot_html}
        </div>
    </body>
    </html>
    """

    with open('combined_cars_data.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    webbrowser.open('combined_cars_data.html')



async def main_function():
    while True:
        try:
            make = input("Elige la marca (por ejemplo, Audi): ")
            model = input("Elige el modelo (por ejemplo, A3): ")
            yearMin = int(input("Elige el año mínimo (por ejemplo, 2000): "))
            yearMax = int(input("Elige el año máximo (por ejemplo, 2022): "))
            kmMin = int(input("Elige el kilometraje mínimo (por ejemplo, 0): "))
            kmMax = int(input("Elige el kilometraje máximo (por ejemplo, 1000000): "))
            priceMin = int(input("Elige el precio mínimo (por ejemplo, 0): "))
            priceMax = int(input("Elige el precio máximo (por ejemplo, 100000): "))

            if yearMin < 0 or yearMax < 0 or kmMin < 0 or kmMax < 0 or priceMin < 0 or priceMax < 0:
                raise ValueError("Los valores de precio, año y kilometraje no pueden ser negativos.")
            if yearMin > yearMax:
                raise ValueError("El año mínimo no puede ser mayor que el año maximo.")
            if kmMin > kmMax:
                raise ValueError("El kilometro mínimo no puede ser mayor que el kilometro maximo.")
            if priceMin > priceMax:
                raise ValueError("El precio mínimo no puede ser mayor que el precio maximo.")
            df = pd.DataFrame(await search_car(make, model, yearMin, yearMax, kmMin, kmMax, priceMin, priceMax))

            df = df[(df['make'].str.lower().str.contains(make.lower())) & (df['model'].str.lower().str.contains(model.lower()))]

            print('Se han encontrado ' + str(len(df)) + ' coches')
            if len(df) == 0:
                raise ValueError("No se han encontrado coches con los criterios seleccionados.")
            df = df.sort_values(by='score', ascending=False)
            fig = px.scatter(df, x='price', y='km', color='year', hover_data=['year', 'km', 'price'])
            fig.update_traces(marker=dict(size=12,
                                          line=dict(width=2,
                                                    color='DarkSlateGrey')),
                              selector=dict(mode='markers'))
            fig.update_layout(title='Diagrama de dispersión de los coches encontrados',
                  xaxis_title='Precio',
                  yaxis_title='Km',
                  clickmode='event+select')
            fig.update_layout(legend_title_text='Año')


            df['image'] = df['image'].apply(lambda x: f'<a href="{x}">Link a la imagen</a>')
            df['url'] = df['url'].apply(lambda x: f'<a href="{x}">Link al anuncio</a>')
            df.rename(columns={'id': 'ID', 'image': 'Imagen', 'make': 'Marca', 'model': 'Modelo', 'year': 'Año', 'km': 'Km', 'fuelType': 'Combustible', 'cv': 'CV', 'price': 'Precio', 'url': 'Enlace', 'site': 'Página del anuncio', 'score': 'Puntuación'}, inplace=True)
            df_html = df.to_html(index=False,  escape=False)
            generate_html_file(df_html, fig.to_html())
        except ValueError as ve:
            print(f"Entrada no válida: {ve}")

        webbrowser.open('combined_cars_data.html')
        print("1. Cerrar sesión")
        print("2. Continuar buscando")
        option = input("Elige una opción: ")
        if option == "1":
            return
        if option == "2":
            web = await main_function()
        else:
            return


async def main_menu():
    while True:
        print('-----------------------------------')
        print("Menú principal")
        print('-----------------------------------')
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Salir")
        option = input("Elegir una opción: ")
        if option == "1":
            username = input("Introducir nombre de usuario: ")
            password = input("Introducir contraseña: ")
            user = User(username=username, password=password)
            register(user)
        elif option == "2":
            username = input("Introducir nombre de usuario: ")
            password = input("Introducir contraseña: ")
            user = User(username=username, password=password)
            await login(user)
        elif option == "3":
            break
        else:
            print("Opción no válida")


if __name__ == "__main__":
   asyncio.run(main_menu())
