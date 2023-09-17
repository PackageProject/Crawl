from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
browser = webdriver.Chrome(options=options)

def extract_restaurant(html):
    distance = html.select(".h69bs")[-1].text
    title = html.find("span", class_="place_bluelink TYaxT").get_text()
    category = html.find("span", class_="KCMnt").get_text()
    link = html.select_one("a")["href"]
    print(title)
    return {"title": title, "distance": distance, "category": category, "link": link}

def extract_additional_info(link):
    browser.get(link)
    time.sleep(3)

    soup = BeautifulSoup(browser.page_source, 'html.parser')
    address= soup.select_one(".vV_z_ > a > span.LDgIH").get_text()
    phone = soup.select_one("span.xlx7Q").get_text()

    saletime_element = soup.select_one('span.U7pYf time[aria-hidden="true"]')
    saletime = saletime_element.get_text() if saletime_element else None
    if saletime is None:
        print("Saletime: 정보없음")
    else:
        print("Saletime:", saletime)

    return {"address": address, "phone": phone, "saletime": saletime}

def final_location(location, word):
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={location}"
    kakao_key = "f3b-----------------" 
    result = requests.get(url, headers={"Authorization": f"KakaoAK {kakao_key}"})
    json_obj = result.json()
    x = json_obj['documents'][0]['x']
    y = json_obj['documents'][0]['y']
    final_url = f"https://m.place.naver.com/restaurant/list?x={x}&y={y}&query={word}"
    return final_url

def scrap_restaurant(location, word):
    URL = final_location(location, word)
    browser.get(URL)
    time.sleep(3)

    # "포장주문" 누르기
    package = browser.find_element('xpath','//*[@id="app-root"]/div/div[1]/div/div/div/div/div/span[5]/a')
    package.click()
    time.sleep(3)

    # "가까운" 누르기
    short_way = browser.find_element('xpath', '//*[@id="_list_scroll_container"]/div/div/div[1]/div/div/div/div/span[12]/a')
    short_way.click()
    time.sleep(5)

    inf = []
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    restaurants = soup.select('li.UEzoS')
    print(len(restaurants)) 
    for restaurant in restaurants:
        information = extract_restaurant(restaurant)
        additional_info = extract_additional_info("https://m.place.naver.com" + information["link"])
        information.update(additional_info)
        inf.append(information)
    return inf
       

location = "서울특별시 도봉구 삼양로144길 33" #덕성여대 주소임
word = "음식점"
restaurant_list = scrap_restaurant(location, word)
df = pd.DataFrame(columns=["title", "distance", "category", "link", "address","phone","saletime"])
df_list = []
for restaurant in restaurant_list:
    df_list.append(pd.DataFrame([restaurant]))

df = pd.concat(df_list, ignore_index=True)
df.to_csv('store_crawling.csv', mode='a', index=False, encoding='utf-8-sig')

for restaurant in restaurant_list:  #터미널에 찍어서 확인용
    print("Name:", restaurant["title"])
    print("distance:", restaurant["distance"])
    print("category:", restaurant["category"])
    print("Link:", restaurant["link"])
    print("address:", restaurant["address"])
    print("phone:", restaurant["phone"])
    print("saletime:", restaurant["saletime"])
    print("---------------------")
print("fin")
