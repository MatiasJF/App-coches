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
                print("User already registered")
                return

    # Genera una nueva sal para cada usuario
    salt = bcrypt.gensalt()
    # Hashea la contraseña con la sal
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    with open('users.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user.username, salt, hashed_password])
    print("User registered")
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
                print("User logged in")
                await main_function()
                return

            else:
                print("Invalid password")
                return
    print("User not registered")
    return

def get_url_walla(id):

    return

def get_url_com(id):
    return

def transform_data(df_com, df_walla):
    same_columns_wallapop = ['id', 'title', 'images', 'price', 'brand', 'model', 'year', 'km', 'engine', 'horsepower']
    same_columns_coches_com = ['id','image', 'price', 'url' , 'make', 'model' , 'fuel', 'cv', 'km', 'year']
    comon_names = ['id','image','price','make','model','year','km','fuelType','horsepower','cv']
    rename_columns = {
        'engine': 'fuelType',
        'fuel' : 'fuelType',
        'horsepower': 'cv',
        'brand' : 'make',
        'images': 'image',
        'url': 'link'
    }
    delete_columns = ['title', 'url']
    df_walla['images'] = df_walla['images'].apply(lambda x: x[0]['original'] if isinstance(x, list) and len(x) > 0 else None)
    df_walla.rename(columns=rename_columns, inplace=True)

    df_walla.drop(columns=delete_columns, inplace=True, errors='ignore')

    df_com.rename(columns=rename_columns, inplace=True)

    df_com.drop(columns=delete_columns, inplace=True, errors='ignore')

    df_walla = df_walla[[col for col in comon_names if col in df_walla.columns]]
    df_com = df_com[[col for col in comon_names if col in df_com.columns]]
    df_walla['site'] = 'walla'
    df_com['site'] = 'com'
    print(len(df_walla)), print(len(df_com))
    df = pd.concat([df_com, df_walla], ignore_index=True)
    df['price'] = df['price'].fillna(0).replace({'\€': '', '\.': '', ',': ''}, regex=True).astype(int)
    df['km'] = df['km'].fillna(0).replace({'\€': '', '\.': '', ',': ''}, regex=True).astype(int)
    df['year'] = df['year'].fillna(0).astype(int)
    score = (df['price'] - df['price'].mean()) / df['price'].std() + (df['km'] - df['km'].mean()) / df['km'].std() + (df['year'] - df['year'].mean()) / df['year'].std()
    df['score'] = score
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
    # print(df.columns)
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
    if len(df) == 0:
        print('No data found')
        return
    df = transform_data(df , df3)
    return df


async def main_function():
    while True:
        try:
            make = input("Elige la marca (e.g., Audi): ")
            model = input("Elige el modelo (e.g., A3): ")
            yearMin = int(input("Elige el año mínimo (e.g., 2000): "))
            yearMax = int(input("Elige el año máximo (e.g., 2022): "))
            kmMin = int(input("Elije el minimo kilometraje (e.g., 0): "))
            kmMax = int(input("Elije el maximo kilometraje (e.g., 1000000): "))
            priceMin = int(input("Elije el precio mínimo (e.g., 0): "))
            priceMax = int(input("Elige el precio máximo (e.g., 100000): "))

            if yearMin < 0 or yearMax < 0 or kmMin < 0 or kmMax < 0 or priceMin < 0 or priceMax < 0:
                raise ValueError("Los valores de precio, año y kilometraje no pueden ser negativos.")
            if yearMin > yearMax:
                raise ValueError("El año minimo no puede ser mayor que el año maximo.")
            if kmMin > kmMax:
                raise ValueError("El kilometro minimo no puede ser mayor que el kilometro maximo.")
            if priceMin > priceMax:
                raise ValueError("El precio minimo no puede ser mayor que el precio maximo.")
            df = pd.DataFrame(await search_car(make, model, yearMin, yearMax, kmMin, kmMax, priceMin, priceMax))

            df = df[(df['make'].str.lower().str.contains(make.lower())) & (df['model'].str.lower().str.contains(model.lower()))]

            print('Encontrados ' + str(len(df)) + ' coches')
            if len(df) == 0:
                raise ValueError("No se han encontrado coches con los criterios seleccionados.")
            df = df.sort_values(by='score', ascending=False)
            fig = px.scatter(df, x='price', y='km', color='year', hover_data=['year', 'km', 'price'])

            fig.update_traces(marker=dict(size=12, opacity=0.8), selector=dict(mode='markers'), customdata=df['image'])
            fig.update_traces(hoverinfo='skip', selector=dict(mode='markers'))
            fig.update_layout(clickmode='event+select')

            def update_url(trace, points, selector):
                if points.point_inds:
                    url = trace.customdata[points.point_inds[0]]
                    if url:
                        import webbrowser
                        webbrowser.open(url)

            for trace in fig.data:
                trace.on_click(update_url)

            df['image'] = df['image'].apply(lambda x: f'<a href="{x}">{x}</a>')
            df_html = df.to_html(index=False,  escape=False)

            combined_html = f"<h1>DataFrame</h1>{df_html}<h1>Scatter Plot</h1>{fig.to_html()}"

            with open('combined_cars_data.html', 'w', encoding='utf-8') as f:
                f.write(combined_html)
                webbrowser.open('combined_cars_data.html')
        except ValueError as ve:
            print(f"Invalid input: {ve}")

        webbrowser.open('combined_cars_data.html')
        print("1. Logout")
        print("2. Continuar Buscando")
        option = input("Elige una opción: ")
        if option == "1":
            return
        if option == "2":
            web = await main_function()
        else:
            return


async def main_menu():
    while True:
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        option = input("Choose an option: ")
        if option == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            user = User(username=username, password=password)
            register(user)
        elif option == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            user = User(username=username, password=password)
            await login(user)
        elif option == "3":
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
   asyncio.run(main_menu())
