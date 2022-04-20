import json
import requests
import numpy as np
from re import sub
import pandas as pd
from datetime import time
from fastapi import FastAPI
from decimal import Decimal

app = FastAPI()

@app.get("/zoltv/{token}")
def zomato_orders_ltv(token: str, cookie:str):
    url = 'https://www.zomato.com/webroutes/user/orders'
    
    headers = {
        'Connection': 'keep_alive',
        'Cookie': cookie,
        'dnt': '1',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "macOS",
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'sec-ch-ua': 'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-gpc': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'x-zomato-csrft': token,
    }

    total_cost = 0

    params = {'page': 1}
    r = requests.get(url, headers=headers, params=params)
    raw = json.loads(r.text)
    page_no = raw["sections"]["SECTION_USER_ORDER_HISTORY"]["totalPages"]

    li=[]
    for i in range(1, page_no+1):
        params = {'page': i}
        r = requests.get(url, headers=headers, params=params)

        raw = json.loads(r.text)
        orders = raw["entities"]["ORDER"]

        for k, v in orders.items():
            status = int(v['status'])
            if status == 6:
                total_cost += Decimal(sub(r'[^\d.]', '', v['totalCost']))
                a=tuple((k, v['orderDate'], v['totalCost'], v['dishString'],v['resInfo']['name'],v['resInfo']['rating']['aggregate_rating'],v['resInfo']['establishment']))
                li.append(a)

    df = pd.DataFrame(li, columns =['Order_Id', 'Order_Date', 'Order_Price','Items','Restaurant_Name','Restaurant_Rating','Restaurant_Type'])
    
    df[['Order_Date','Order_Time']] = df['Order_Date'].str.split('at',expand=True)
    df['Order_Date'] = df['Order_Date'].str.strip()
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Order_Month'] = df['Order_Date'].dt.month_name()
    df['Order_Day'] = df['Order_Date'].dt.day_name()
    df['Order_Year'] = pd.DatetimeIndex(df['Order_Date']).year
    df['Restaurant_Type'] = df['Restaurant_Type'].apply(lambda x: x[1:-1])
    df.loc[df['Items'].str.contains("Chicken","Egg"),'Meal_Type'] = 'Non Veg'
    df.loc[~df['Items'].str.contains("Chicken","Egg"),'Meal_Type'] = 'Veg'
    df['Order_Time'] = df['Order_Time'].str.strip()
    df['Order_Time'] = pd.to_datetime(df['Order_Time']).dt.time

    conditions = [
        (df['Order_Time'] >= time(hour=8, minute=0, second=0)) & (df['Order_Time'] < time(hour=12, minute=0, second=0)),
        (df['Order_Time'] >= time(hour=12, minute=0, second=0)) & (df['Order_Time'] < time(hour=16, minute=0, second=0)),
        (df['Order_Time'] >= time(hour=16, minute=0, second=0)) & (df['Order_Time'] < time(hour=19, minute=0, second=0)),
        (df['Order_Time'] >= time(hour=19, minute=0, second=0))]
    choices = ['Breakfast','Lunch', 'Snacks', 'Dinner']
    df['Meal'] = np.select(conditions, choices, default='Dinner')
    df['Restaurant_Rating'] = df['Restaurant_Rating'].astype(float)
    df['Rating >= 4'] = np.where(df['Restaurant_Rating'] >= 4 , 'Yes', 'No')
    df = df.replace(r'^\s*$', 'NA', regex=True)

    df.to_csv('data.csv',index=False)
    return {"पैसा बर्बाद on Zomato": total_cost}