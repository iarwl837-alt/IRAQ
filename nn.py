import requests
import re
import json
import time
import random
import base64
import hashlib
import uuid
from bs4 import BeautifulSoup
from faker import Faker
from user_agent import generate_user_agent

def gdata():
    fnames = ["john","james","robert","michael","william","david","richard","joseph","thomas","charles"]
    lnames = ["smith","johnson","williams","brown","jones","garcia","miller","davis","rodriguez","martinez"]
    domains = ["gmail.com","yahoo.com","outlook.com","hotmail.com","protonmail.com","icloud.com"]
    f = random.choice(fnames)
    l = random.choice(lnames)
    num = random.randint(10, 999)
    email = f"{f}.{l}{num}@{random.choice(domains)}"
    name = f"{f.capitalize()} {l.capitalize()}"
    add = f"{random.randint(100,9999)} {random.choice(['Main','Oak','Pine','Maple','Cedar'])} St"
    city = random.choice(["New York","Los Angeles","Chicago","Houston","Phoenix"])
    zip = str(random.randint(10000, 99999))
    phone = f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}"
    return email, name, add, city, zip, phone

email, name, add, city, zip, phone = gdata()
r = requests.Session()
u = generate_user_agent()

headers = {
    'authority': 'backend.al.fan',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://alfan.link',
    'platform_type': 'Web',
    'referer': 'https://alfan.link/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': u,
    'x-api-version': '2026-03-09',
}

json_data = {
    'linkId': 'a1717225-65a6-453d-9fd1-88105f6b98a3',
    'currency': 'usd',
    'amount': 400,
    'productType': 'Link',
    'sectionItemPriceValue': 'default',
    'countryCode': 'FR',
}

response = r.post('https://backend.al.fan/finance/api/stripe/paymentIntent', headers=headers, json=json_data)

xxxp = response.json()['clientSecret']
xxp = xxxp
xp = xxp.split('_secret')[0]

headers = {
    'authority': 'api.stripe.com',
    'accept': 'application/json',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': u,
}

data = f'return_url=https%3A%2F%2Falfan.link%2Fahmad_farajallah%3Femail%3Dwee%2540tmzil.com%26linkType%3DsellProductGuide%26bookUrl%3D%26name%3DTommy%2520wlros%26notes%3D%26contentType%3D%26monetizeID%3Da1717225-65a6-453d-9fd1-88105f6b98a3&payment_method_data[billing_details][name]={name}&payment_method_data[billing_details][email]={email}&payment_method_data[billing_details][phone]={phone}&payment_method_data[billing_details][address][line1]=&payment_method_data[billing_details][address][country]=FR&payment_method_data[type]=card&payment_method_data[card][number]=5570+9850+4407+8500&payment_method_data[card][cvc]=485&payment_method_data[card][exp_year]=29&payment_method_data[card][exp_month]=11&payment_method_data[allow_redisplay]=unspecified&payment_method_data[payment_user_agent]=stripe.js%2F03270cb259%3B+stripe-js-v3%2F03270cb259%3B+payment-element&key=pk_live_51KqEwKAg5UWiBn5yZ9tQb5Uy4Wy58k74q6hT7nXuxLoQeAiD8P8JEUhDZDgvDQxvFITX9sj4dRz4Tud1r1vvhxOC00M5fToUYy&client_secret={xxxp}'

response = r.post(
    f'https://api.stripe.com/v1/payment_intents/{xp}/confirm',
    headers=headers,
    data=data,
)

headers = {
    'authority': 'api.stripe.com',
    'accept': 'application/json',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': u,
}

params = {
    'is_stripe_sdk': 'false',
    'client_secret': xxxp,
    'key': 'pk_live_51KqEwKAg5UWiBn5yZ9tQb5Uy4Wy58k74q6hT7nXuxLoQeAiD8P8JEUhDZDgvDQxvFITX9sj4dRz4Tud1r1vvhxOC00M5fToUYy',
}

response = r.get(f'https://api.stripe.com/v1/payment_intents/{xp}', params=params, headers=headers)

print(response.text)