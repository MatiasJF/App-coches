import requests
import pandas as pd
import urllib.parse
import matplotlib.pyplot as plt
import plotly.express as px
import csv
import bcrypt


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
    print(hashed_password)
    print(salt)
    with open('users.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user.username, salt, hashed_password])
    print("User registered")
    return


def login(user: User):
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
                main_function()
                return
            else:
                print("Invalid password")
                return
    print("User not registered")
    return



def search_car(make: str, model: str, yearMin: int, yearMax: int, kmMin: int, kmMax: int, priceMin: int, priceMax: int):
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
        'search3': model + ' ' + make,
    }
    url_base = 'https://www.coches.com/api/vo/pills/?'
    url_completa = url_base + urllib.parse.urlencode(parametros)
    response = requests.get(url_completa)
    data = response.json()
    df = pd.DataFrame(data['data'])
    df = df[['price', 'make', 'model', 'fuel', 'cv', 'km', 'year', 'url']]
    return df


def main_function():
    make = input("Enter make: ")
    model = input("Enter model: ")
    yearMin = int(input("Enter min year: "))
    yearMax = int(input("Enter max year: "))
    kmMin = int(input("Enter min km: "))
    kmMax = int(input("Enter max km: "))
    priceMin = int(input("Enter min price: "))
    priceMax = int(input("Enter max price: "))
    df = search_car(make, model, yearMin, yearMax, kmMin, kmMax, priceMin, priceMax)

    df['score'] = 0.8 * df['price'] - 0.5 * df['year'] + 0.3 * df['km']

    df = df.sort_values(by='score', ascending=False)

    html_table = df.to_html()

    fig = px.scatter(df, x='km', y='price', color='year', hover_data=['make', 'model', 'url'])
    fig.update_traces(marker=dict(size=12, opacity=0.8))
    fig.update_layout(title='Car Search Results', xaxis_title='Kilometers', yaxis_title='Price')
    fig.show()
    print(html_table)
    return


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
    main_menu()
