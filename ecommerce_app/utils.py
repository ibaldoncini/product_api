import requests


DOLAR_API_URL = "https://www.dolarsi.com/api/api.php?type=valoresprincipales"


def get_blue_price():
    api_response = requests.get(DOLAR_API_URL)
    payload = api_response.json()
    price = get_specific_dolar_price(payload, 'Dolar Blue')
    return price


def get_specific_dolar_price(prices_dict, dolar_name):
    price = None
    for dolar_type in prices_dict:
        data = dolar_type['casa']
        if data['nombre'] == dolar_name:
            buy = parse_price_str(data['compra'])
            sell = parse_price_str(data['venta'])
            price = (buy + sell) / 2

    return price


def parse_price_str(price_str):
    return float(price_str.replace(',', '.'))
