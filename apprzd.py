#streamlit run animals.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import date
import plotly.express as px
import pandas as pd
import nltk
import re
nltk.download('stopwords')
import pickle
from nltk.corpus import stopwords

st.set_page_config(page_title='Данные о закупках РЖД',page_icon=":bar_chart",layout="wide")

#data = pd.read_excel('RZD1.xlsx')
#data = data[data['Цена_договора']!='Не указано']
#data = data[data['Дата_окончания_подачи_заявок'] != 'Не указано']
#data = data[data['Дата_окончания_подачи_заявок'] != 'Не предусмотрена']
data = pd.read_excel('RZD1.xlsx')
data_test = pd.read_excel('RZD2.xlsx')

# data['Цена_договора'] = data['Цена_договора'].astype('int64')

for stroka in range(len(data['Цена_договора'])):
    if str(data['Цена_договора'][stroka]).isdecimal() == False:
        data = data.drop(index=[stroka])

for stroka in range(len(data_test['Цена_договора'])):
    if str(data_test['Цена_договора'][stroka]).isdecimal() == False:
        data_test = data_test.drop(index=[stroka])

data['Цена_договора'] = data['Цена_договора'].astype('int64')
data_test['Цена_договора'] = data_test['Цена_договора'].astype('int64')

product_categories = []
# elif (('услуг' in product.lower()) or (('работ'  in product.lower()) and ('выполн' in product.lower())) or (('ремонт'  in product.lower()) and ('выполн' in product.lower()))) or (('услуг' in category.lower()) or (('работ'  in category.lower()) and ('выполн' in category.lower())) or (('ремонт'  in category.lower()) and ('выполн' in category.lower()))):
# product_categories.append('Услуги')

for product, price, category in zip(data['Наименование_процедуры'], data['Цена_договора'], data['Продукт']):
    if ((('строител' in category) and ('работ' in category) and ('поставк') not in category) or (
            ('капитал' in category) and ('ремонт' in category) and ('поставк' not in category))) or (
            (('строител' in product) and ('работ' in product) and ('постав') not in product) or (
            ('капитал' in product) and ('ремонт' in product) and ('поставк' not in product))):
        product_categories.append('Работы')

    elif (('услуг' in product.lower()) or (('ремонт' in product.lower()) and ('поставк' not in product.lower())) or (
            ('работ' in product.lower()) and ('поставк' not in product.lower()))) or (('услуг' in category.lower()) or (
            ('ремонт' in category.lower()) and ('поставк' not in category.lower())) or ((
                                                                                                'работ' in category.lower()) and (
                                                                                                'поставк' not in category.lower()))):
        product_categories.append('Услуги')

    elif (('поставк' in product.lower()) and (price > 100000) and (
            ('включ' not in product.lower()) and ('выполн' not in product.lower()))) or (
            (('поставк' in category.lower()) and (price > 100000)) and (
            ('включ' not in category.lower()) and ('выполн' not in category.lower()))):
        product_categories.append('Товары')

    else:
        product_categories.append('Прочие')

data['Категория_предмета_закупки'] = product_categories

mas_pub = []#даты публикации
mas_finish = []#даты окончания
documents = []

from nltk.stem import WordNetLemmatizer

stemmer = WordNetLemmatizer()

def normalize(massiv):
    for sen in range(len(massiv)):
    # Remove all the special characters
        document = re.sub(r'\W', ' ', str(massiv[sen]))

        # remove all single characters
        document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)

        # Remove single characters from the start
        document = re.sub(r'\^[a-zA-Z]\s+', ' ', document)

        # Substituting multiple spaces with single space
        document = re.sub(r'\s+', ' ', document, flags=re.I)

        # Removing prefixed 'b'
        document = re.sub(r'^b\s+', '', document)

        # Converting to Lowercase
        document = document.lower()

        # Lemmatization
        document = document.split()

        document = [stemmer.lemmatize(word) for word in document]
        document = ' '.join(document)

        documents.append(document)

normalize(data['Продукт'].tolist())
data["clean_text"] = documents
data = data[["clean_text","Категория_предмета_закупки"]]

from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(stop_words=stopwords.words('russian'))
X = vectorizer.fit_transform(data['clean_text'].tolist()).toarray()
y = data['Категория_предмета_закупки'].tolist()

from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(random_state = 0)
clf.fit(X,y)

machine_categories = []
for sentence,price in zip(data_test['Продукт'],data_test['Цена_договора']):
    if price<100000 and clf.predict(vectorizer.transform([sentence]))[0]=='Прочие':
        machine_categories.append('Прочие')
    else:
        machine_categories.append(clf.predict(vectorizer.transform([sentence]))[0])

data_test["Категория_предмета_закупки"] = machine_categories

for date_pub,date_finish in zip(data_test['Дата_публикации_процедуры'],data_test['Дата_окончания_подачи_заявок']):
    mas_pub.append(f"{date_pub[len(date_pub)-4:len(date_pub)]}-{date_pub[3:5]}-{date_pub[0:2]}")
    mas_finish.append(f"{date_finish[len(date_finish)-4:len(date_finish)]}-{date_finish[3:5]}-{date_finish[0:2]}")

data_test['Дата_публикации_процедуры'] = mas_pub
data_test['Дата_окончания_подачи_заявок'] = mas_finish

st.title(":bar_chart: Статистика и диаграммы")
st.subheader('Категории закупок')

st.write(
    """
- ✔️ Работы (строительство или капитальный ремонт)
- ✔️ Услуги (услуги и работы)
- ✔️ Поставки (поставки стоимостью больше 100 000 рублей)
- ✔️ Прочие (все остальное)
"""
)
st.markdown("##")

st.sidebar.header("Пожалуйста, фильтруйте здесь:")

date_start= st.sidebar.date_input(
    "Выберите промежуток дат",
    pd.to_datetime(data_test.iloc[-1]['Дата_публикации_процедуры'], format="%Y-%m-%d")
)

date_end= st.sidebar.date_input(
    "Выберите промежуток дат",
    pd.to_datetime(data_test.iloc[0]['Дата_публикации_процедуры'], format="%Y-%m-%d")
)

button_show = st.button('Показать статистику')

category = st.sidebar.multiselect(
    "Выберите категорию предмета закупки:",
    options=data_test["Категория_предмета_закупки"].unique(),
    default=data_test["Категория_предмета_закупки"].unique()
)

customer = st.sidebar.multiselect(
    "Выберите заказчика:",
    options=data_test["Заказчик"].unique(),
    default=data_test["Заказчик"].unique()
)

df_selection = data_test[(data_test['Дата_публикации_процедуры']>=str(date_start)) & (data_test['Дата_публикации_процедуры']<=str(date_end))]

df_selection = df_selection.query(
    "Категория_предмета_закупки == @category & Заказчик == @customer"
)

st.markdown("""---""")

total_sum = df_selection['Цена_договора'].sum()
average_sum = round(df_selection['Цена_договора'].mean(),2)
left_column, right_column = st.columns(2)

if button_show:
    with left_column:
        st.subheader("Сумма закупок:")
        st.subheader(f"RUB {total_sum:,}")

    with right_column:
        st.subheader("Средня сумма закупок:")
        st.subheader(f"RUB {average_sum:,}")

    st.markdown("""---""")

    price_product = (
        df_selection.groupby(by=["Категория_предмета_закупки"]).sum()[["Цена_договора"]]
    )

    #product_count = df_selection['Категория_предмета_закупки'].value_counts()
    product_count = df_selection.groupby(['Категория_предмета_закупки'])['Категория_предмета_закупки'].count()

    customer_count = df_selection.groupby(['Заказчик'])['Заказчик'].count()

    category_sum = px.bar(
        price_product,
        x="Цена_договора",
        y=price_product.index,
        orientation="h",
        title="<b>Сумма закупок по категориям</b>",
        color_discrete_sequence=["#0083B8"] * len(price_product),
        template="plotly_white",
    )

    category_sum.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title = "Сумма закупок",
        yaxis_title="Категория предмета закупки"
    )

    category_count = px.bar(
        product_count,
        x="Категория_предмета_закупки",
        y=product_count.index,
        orientation="h",
        title="<b>Количество закупок по категориям</b>",
        color_discrete_sequence=["#0083B8"] * len(price_product),
        template="plotly_white"
    )

    category_count.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Количество закупок",
        yaxis_title="Категория предмета закупки"
    )

    customer_count_show = px.pie(
        customer_count,
        values=customer_count.values.tolist(), names=customer_count.index.tolist()
    )

    customer_count_show.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Заказчики",
        yaxis_title="Количество закупок"
    )

    st.plotly_chart(category_sum)
    st.plotly_chart(category_count)
    st.plotly_chart(customer_count_show)
    st.dataframe(df_selection)







