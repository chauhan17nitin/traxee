from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task

# firebase authentication and database reference
import firebase_admin
from firebase_admin import auth
from firebase_admin import db
from firebase_admin import credentials

# scrapping tools
import requests
from bs4 import BeautifulSoup
import re
import time

cred = credentials.Certificate('/home/nitin/Downloads/traxee-pr-301-firebase-adminsdk-y22ww-2e5aafb334.json')
default_app = firebase_admin.initialize_app(cred ,{
    'databaseURL' : 'https://traxee-pr-301.firebaseio.com/'
})

root = db.reference()


# Defining scrapping function can be run by parsing url of the product
def scrape(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    product_id = re.findall("\w?pid.*&lid", url)
    product_id = product_id[0][4: -4]

    product_information = soup.find_all('div', class_='_1HmYoV _35HD7C col-8-12')
    if len(product_information) == 0:
        return "Error in Scrapping or may be rate limit reached"
    current_price = product_information[0].find_all('div', class_='_1vC4OE _3qQ9m1')

    current_price = current_price[0].text[1:]
    current_price = re.sub(",", "", current_price)
    current_price = int(current_price)

    cost_price = product_information[0].find_all('div', class_='_3auQ3N _1POkHg')
    if len(cost_price) == 0:
        cost_price = cost_price[0].text[1:]
        cost_price = re.sub(",", "", cost_price)
        cost_price = int(cost_price)
    else:
        cost_price = current_price
    
    discount = ((cost_price-current_price)/cost_price)*100

    timestamp = int(time.time())
    history = {
        'current_price': current_price,
        'cost_price': cost_price,
        'discount': int(discount)
    }

    root.child('history').child(product_id).child(str(timestamp)).set(history)

    root.child('products').child(product_id).update({
                            'current_price': current_price
                        })

    return True

@task(name="scrape_regulary")
def scrape_regulary():

    products = root.child('products').get()
    for product in products:
        url = products[products]['product_link']
        scrape(url)
    return 

def notification_mail():
    return

@task(name="sum_two_numbers")
def add(x, y):
    print('addition done')
    return x + y

@task(name="multiply_two_numbers")
def mul(x, y):
    print('multiplication done')
    total = x * y
    # total = x * (y * random.randint(3, 100))
    return total

@task(name="sum_list_numbers")
def xsum(numbers):
    print('list sum done')
    return sum(numbers)