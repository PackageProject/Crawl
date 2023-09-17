import requests

location = "서울특별시 도봉구 삼양로144길 33" # 덕대 위치 ########여기다가 각 음식점의 주소 넣기#######
url = f"https://dapi.kakao.com/v2/local/search/address.json?query={location}"
kakao_key = "f3-----------------" 
result = requests.get(url, headers={"Authorization":f"KakaoAK {kakao_key}"})
json_obj = result.json()
#print(json_obj)
x = json_obj['documents'][0]['x']
y = json_obj['documents'][0]['y']
print(x , y)
