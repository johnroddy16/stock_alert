#!/usr/bin/env python3 

import requests 
import os 
from datetime import datetime as dt, timedelta as td 
import smtplib   

stock = 'TSLA'
company_name = 'Tesla Inc'
func = 'TIME_SERIES_DAILY'
stock_url = 'https://www.alphavantage.co/query'
stock_api_key = os.getenv('STOCK_API_KEY')
news_url = 'https://newsapi.org/v2/everything'
news_api_key = os.getenv('NEWS_API_KEY') 
email = os.getenv('EMAIL')
app_password = os.getenv('APP_PASSWORD') 

up_arrow = '🔺'
down_arrow = '🔻'

now = dt.now()
yesterday = now - td(days=1)
current_date = str(now.date())
yester_date = str(yesterday.date())  

stock_params = {
    'function': func,
    'symbol': stock,
    'apikey': stock_api_key,
}

stock_response = requests.get(stock_url, params=stock_params)
stock_response.raise_for_status() 
print(stock_response.status_code) 
stock_data = stock_response.json()
print(stock_data)

yesterday_close = float(stock_data['Time Series (Daily)'][yester_date]['4. close']) 
today_close = float(stock_data['Time Series (Daily)'][current_date]['4. close'])    

news_params = {
    'apiKey': news_api_key,
    'q': company_name,
    'from': '25-02-25', 
    'language': 'en', 
}

news_response = requests.get(news_url, params=news_params)
news_response.raise_for_status()
print(news_response.status_code)
news_data = news_response.json()

titles_and_desc = []

for i in range(3):
    try:
        titles_and_desc.append([news_data['articles'][i]['title'], news_data['articles'][i]['description']])
    except IndexError:
        pass   

# up or down for the day and the percentage change:
up = False 
down = False 

if today_close < yesterday_close:
    down = True 
    percent_change = round(((yesterday_close - today_close) / yesterday_close) * 100, 2) 
else:
    up = True 
    percent_change = round(((today_close - yesterday_close) / yesterday_close) * 100, 2)
    
# if there are any titles and descriptions we will create a message to send with them, else we send the percentage change:
if up:
    message = f'TSLA: {up_arrow}{percent_change}%\n'
if down:
    message = f'TSLA {down_arrow}{percent_change}%\n'

# if we have titles and desciptions we will add to the body of message, else just send the percentage change:
if titles_and_desc:
    for item in titles_and_desc:
        message += f'Headline: {item[0]}\nBrief: {item[1]}\n\n'

# if percent_change >= 1 send an email, might change this to 5 later: 
if percent_change >= 1:
    subject = 'TSLA Stock Alert!'
    body = f'Subject: {subject}\nMIME-Version: 1.0\nContent-Type: text/plain; charset="utf-8"\n\n{message}'
    with smtplib.SMTP('smtp.gmail.com', port=587) as connection:
        connection.starttls() # make the connection secure 
        connection.login(user=email, password=app_password)
        connection.sendmail(from_addr=email, to_addrs='johnroddy.16@gmail.com', msg=body.encode('utf-8'))
        
# pretty cool little program! 