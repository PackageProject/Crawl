from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
browser = webdriver.Chrome(options=options)

def extract_restaurant(html):
    title = html.find("span", class_="place_bluelink TYaxT").get_text()
    link = html.select_one("a")["href"]
    return {"title": title, "link": link}

def extract_additional_info(soup):
    menu_button = soup.find('span', class_='veBoZ', string='메뉴')
    menulink = menu_button.find_parent('a')['href']
    return {"menulink": menulink}

def extract_add_additional_info(soup):
    menu_items = soup.select('.item_info')

    data = []
    for item in menu_items:
        title = soup.find("h1", class_="title").text.strip()
        menu_name = item.find('div', class_='tit').text.strip()
        menu_price = item.find('div', class_='price').text
        data.append({"title": title, "menu_name": menu_name, "menu_price": menu_price})
    return data

def final_location(location, word):
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={location}"
    kakao_key = "f-----------------------------" 
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

    data = []
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    restaurants = soup.select('li.UEzoS')
    print(len(restaurants)) 
    for restaurant in restaurants:
        information = extract_restaurant(restaurant)
        link = "https://m.place.naver.com" + information["link"]
        browser.get(link)
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        additional_info = extract_additional_info(soup)
        information.update(additional_info)
        link2 = information["menulink"]
        browser.get(link2)
        time.sleep(3)
        soup2 = BeautifulSoup(browser.page_source, 'html.parser')
        additional_data = extract_add_additional_info(soup2)
        data.extend(additional_data)
    
    return data

location = "서울특별시 도봉구 삼양로144길 33"  # 덕성여대 주소임
word = "음식점"
menu_data = scrap_restaurant(location, word)

df = pd.DataFrame(menu_data)
df.to_csv('menu_crawling.csv', index=False, encoding='utf-8-sig')
print("fin")
