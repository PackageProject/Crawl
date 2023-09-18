import pandas as pd
import requests

#매장정보가 담긴 csv명이 stores.csv일 경우
df = pd.read_csv('stores.csv', encoding='cp949')

kakao_key = "f3b121a900d2f12872ba8c70acff4995"

def get_coordinates(address):
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={address}"
    result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
    json_obj = result.json()
    if json_obj.get('documents'):
        x = json_obj['documents'][0]['x']
        y = json_obj['documents'][0]['y']
        return x, y
    else:
        return None, None

x_coordinates = []
y_coordinates = []

for address in df['storesaddress']:
    x, y = get_coordinates(address)
    x_coordinates.append(x)
    y_coordinates.append(y)

df['x'] = x_coordinates
df['y'] = y_coordinates

df.to_csv('stores_with_xy.csv', index=False, encoding='utf-8-sig')
