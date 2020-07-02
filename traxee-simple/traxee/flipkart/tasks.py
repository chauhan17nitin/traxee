from __future__ import absolute_import, unicode_literals
import random
import requests
from celery.decorators import task
# firebase authentication and db reference
from .views import root
# imports for mailing facility
from django.core.mail import send_mail
from traxee.settings import EMAIL_HOST_USER
import time
HEADERS = {
            "Fk-Affiliate-Id": "shaikhajw",
            "Fk-Affiliate-Token": "431799c9268040bebdb683698d6736da"
            }

from threading import Thread

def email_notify(product_id, current_price, product_name):
    snapshot = root.child('notifications').child('product_id').get()
    if snapshot is not None:
        for key, value in snapshot.items():
            if float(current_price['amount']) < value:
                user = auth.get_user(key)
                subject = 'Update for {}'.format(product_name)
                message = 'Hello Dear, the current price of your tracked product is {} which is less than the amount set by you'.format(str(current_price['amount']))
                send_mail(subject, message, EMAIL_HOST_USER, [user.email], fail_silently = False)
                print('Here we will have to mail to notify the person')
            else:
                pass

@task(name="fetch_every_day")
def fetch():
    URL = "https://affiliate-api.flipkart.net/affiliate/1.0/product.json"

    snapshot = root.child('products').get()

    for key, value in snapshot.items():
        PARAMS = {
                "id": key,
                }

        r = requests.get(url = URL, params = PARAMS, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            current_price = data['productBaseInfoV1']['flipkartSpecialPrice']
            cost_price = data['productBaseInfoV1']['flipkartSellingPrice']
            product_name = data['productBaseInfoV1']['title']

            discount = ((cost_price['amount']-current_price['amount'])/cost_price['amount'])*100
            discount = int(discount)

            history = {
                'current_price': current_price,
                'cost_price': cost_price,
                'discount': discount,
            }
            timestamp = int(time.time())

            # adding price history
            product_id = key
            root.child('history').child(product_id).child(str(timestamp)).set(history)
            product_ref = root.child('products').child(product_id)
            product_ref.update({
            'current_price': current_price
            })

            Thread(target=email_notify, args=(product_id, current_price, product_name)).start()
        else:
            print('given product does not exists on flipkart')

    return 'Done'
