# -*- coding: cp1251 -*-
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import openpyxl

df= pd.read_excel('RZD.xlsx')
excel_file = openpyxl.open('RZD.xlsx',read_only=False)
sheet=excel_file.active
rows = df.shape[0]+2
headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'DNT': '1',
        'Accept-Encoding': 'gzip, deflate, lzma, sdch',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
    }
#responce = requests.get("https://company.rzd.ru/ru/9395/page/4893?f1465_pagesize=25&&tender_type=&deal_type_id=1&status_type=&date_to=&client_id=&publish_date_from=&date_start_to=&name=&cod=&publish_date_to=&search_expanded=1&city_id=&date_start_from=&date_from=&msp_subject=&f1465_pagenumber=1", headers=headers)
#soup = bs(responce.text, 'html.parser')

#last_page = int(soup.select('body > div.body-content > main > div > div.pager.print-hide.pager_bottom > ul.pager__list.pager__list_desktop > li.pager__extr.pager__extr_last > a > span')[0].text)#последняя страница
mas_links = []#список ссылок
titles = []#список названий процедур
values = []#список значений процедур
summa = []#сумма цен договора
all = []#все процецуры
procedure = []#значения процедуры
procedure_titles = []
product = ""
#для проверки наличия значений
number = True
name = True
view = True
customer = True
public_flag = True
place_flag = True
finish_flag = True
area_flag = True
price_flag = True

for begin_page in range(1,100):
        res = requests.get(f"https://company.rzd.ru/ru/9395/page/4893?f1465_pagesize=100&&tender_type=&deal_type_id=1&status_type=&date_to=&client_id=&publish_date_from=&date_start_to=&name=&cod=&publish_date_to=&search_expanded=1&city_id=&date_start_from=&date_from=&msp_subject=&f1465_pagenumber={begin_page}",
                                headers=headers)
        newsoup = bs(res.text, 'html.parser')
        links = newsoup.find_all('a', class_="table2__row")#все ссылки со страницы

        for link in links:
                link = link.get('href')
                mas_links.append("https://company.rzd.ru" + link)


for link in mas_links:
        res = requests.get(link,headers=headers)
        newsoup = bs(res.text, 'html.parser')
        product = newsoup.find_all('td')[1].text

        for title, value in zip(newsoup.find_all('dt'), newsoup.find_all('dd')):
                titles.append(title.text)
                values.append(value.text)

        for title in range(len(titles)):
                if 'номер' in titles[title].lower():
                        number = False
                        procedure.append(values[title])

                if 'наименование' in titles[title].lower():
                        name = False
                        procedure.append(values[title])

                if 'вид' in titles[title].lower():
                        view = False
                        procedure.append(values[title])

                if 'заказчик' in titles[title].lower():
                        customer = False
                        procedure.append(values[title])

                if 'цена' in titles[title].lower():
                        price_flag = False
                        for price in newsoup.find_all('td'):
                                if 'ндс' in price.text.lower():
                                        price = price.text.lower()
                                        price = price.replace(' ', '')
                                        for simvol in range(len(price)):
                                                if price[simvol].isdecimal() == False and price[0:simvol].isdigit()==True:
                                                        new_number = int(price[0:simvol])
                                                        summa.append(new_number)
                                                        break



                        procedure.append(sum(summa))

                if 'публикации' in titles[title].lower():
                        procedure.append(values[title])
                        public_flag = False

                if 'место' in titles[title].lower():
                        procedure.append(values[title])
                        place_flag = False

                if 'подачи' in titles[title].lower():
                        procedure.append(values[title])
                        finish_flag = False

                if 'площадка' in titles[title].lower():
                        procedure.append(values[title])
                        area_flag = False

        if number:
                procedure.insert(0,'Не указано')

        if name:
                procedure.insert(1,'Не указано')

        if view:
                procedure.insert(2,'Не указано')

        if customer:
                procedure.insert(3,'Не указано')

        if price_flag:
                procedure.insert(4,'Не указано')

        if public_flag:
                procedure.insert(5, 'Не указано')

        if place_flag:
                procedure.insert(6, 'Не указано')

        if finish_flag:
                procedure.insert(7, 'Не указано')

        if area_flag:
                procedure.insert(8, 'Не указано')

        procedure.append(product)


        titles=[]
        values=[]




        all.append(procedure)
        number = True
        name = True
        view = True
        customer = True
        price_flag = True
        public_flag = True
        place_flag = True
        finish_flag = True
        area_flag = True
        procedure = []
        summa=[]

for procedure in all:
            sheet[f'A{rows}'] = procedure[-10]
            sheet[f'B{rows}'] = procedure[-9]
            sheet[f'C{rows}'] = procedure[-8]
            sheet[f'D{rows}'] = procedure[-7]
            sheet[f'E{rows}'] = procedure[-6]
            sheet[f'F{rows}'] = procedure[-5]
            sheet[f'G{rows}'] = procedure[-4]
            sheet[f'H{rows}'] = procedure[-3]
            sheet[f'I{rows}'] = procedure[-2]
            sheet[f'J{rows}'] = procedure[-1]
            excel_file.save('RZD.xlsx')
            rows+=1


















