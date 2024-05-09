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
                web = await main_function()
                webbrowser.open(web)
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
    comon_names = ['id','image','price','make','model','year','km','fuelType','horsepower','cv','url']
    rename_columns = {
        'engine': 'fuelType',
        'fuel' : 'fuelType',
        'horsepower': 'cv',
        'brand' : 'make',
        'images': 'image',
        'url': 'link'
    }
    delete_columns = ['title']
    df_walla['images'] = df_walla['images'].apply(lambda x: x[0]['original'] if isinstance(x, list) and len(x) > 0 else None)
    df_walla.rename(columns=rename_columns, inplace=True)

    df_walla.drop(columns=delete_columns, inplace=True, errors='ignore')

    df_com.rename(columns=rename_columns, inplace=True)

    df_com.drop(columns=delete_columns, inplace=True, errors='ignore')

    df_walla = df_walla[[col for col in comon_names if col in df_walla.columns]]
    df_com = df_com[[col for col in comon_names if col in df_com.columns]]

    df_walla['site'] = 'walla'

    df_com['site'] = 'com'

    df = df_concatenated = pd.concat([df_walla, df_com], ignore_index=True)
    df['price'] = df['price'].str.replace('€', '').str.replace('.', '').str.replace(',', '.')
    df['year'] = df['year'].str.replace('€', '').str.replace('.', '').str.replace(',', '.')
    df['km'] = df['km'].str.replace('€', '').str.replace('.', '').str.replace(',', '.')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['km'] = pd.to_numeric(df['km'], errors='coerce')
    df = df.dropna(subset=['price', 'year', 'km'])
    df['score'] = 0.8 * df['price'] - 0.5 * df['year'] + 0.3 * df['km']
    df['score'] = (df['score'] - df['score'].min()) / (df['score'].max() - df['score'].min())



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
    data = response.json()
    df = pd.DataFrame(data['pills'])
    print(df.columns)
    return df
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
    print(response)
    df = pd.DataFrame()
    if response.ok:
        try:
            data = response.json()
            rows = []
            for obj in data['search_objects']:
                row = obj['content']
                rows.append(row)

            df = pd.DataFrame(rows)
        except Exception as e:
            print("Error:", e)
    # print(df.columns)
    return df

async def search_car(make: str, model: str, yearMin: int, yearMax: int, kmMin: int, kmMax: int, priceMin: int, priceMax: int):
    df = await get_data_coches_com(make, model, yearMin, yearMax, kmMin, kmMax, priceMin, priceMax)
    df3 = await get_data_wallapop(make, model, yearMin, yearMax, kmMin, kmMax, priceMin, priceMax)
    df = transform_data(df , df3)
    if df.empty:
        print('No data found')
        return
    return df


async def main_function():
    make = input("Enter make: ")
    model = input("Enter model: ")
    yearMin = int(input("Enter min year: "))
    yearMax = int(input("Enter max year: "))
    kmMin = int(input("Enter min km: "))
    kmMax = int(input("Enter max km: "))
    priceMin = int(input("Enter min price: "))
    priceMax = int(input("Enter max price: "))
    df = pd.DataFrame(await search_car(make, model, yearMin, yearMax, kmMin, kmMax, priceMin, priceMax))
    print('Encontrados ' + str(len(df)) + ' coches')

    df = df.sort_values(by='score', ascending=False)
    fig = px.scatter(df, x='price', y='km', color='year', hover_data=['year', 'km', 'price'])

    fig.update_traces(marker=dict(size=12, opacity=0.8), selector=dict(mode='markers'), customdata=df['url'])
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


    df_html = df.to_html(index=False)

    # html_with_data = df_html.replace('<tbody>', '<tbody>' + ''.join([f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td><td><a href="{row[7]}">{row[7]}</a></td><td>{row[8]}</td><td>{row[9]}<td></tr>' for row in df.values]))

    combined_html = f"<h1>DataFrame</h1>{html_with_data}<h1>Scatter Plot</h1>{fig.to_html()}"

    with open('combined_cars_data.html', 'w', encoding='utf-8') as f:
        f.write(combined_html)

    return 'combined_cars_data.html'


def main_menu():
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
            login(user)
        elif option == "3":
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
   asyncio.run(main_menu())
