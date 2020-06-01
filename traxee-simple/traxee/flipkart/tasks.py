from __future__ import absolute_import, unicode_literals
import random
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
        else:
            print('given product does not exists on flipkart')

    return 'Done'

@task(name="daily_email")
def email():

    snapshot = root.child('notifications').get()

    for key, value in snapshot.items():
        current_price = root.child('products').child(key).child('current_price').get()
        amount = current_price['amount']
        subject = 'Tracked Product Updates'
        message = 'Hello Dear, the current price of your tracked product is {}'.format(str(amount))
        for _id in value.keys():
            user = auth.get_user(_id)
            send_mail(subject, message, EMAIL_HOST_USER, [user.email], fail_silently = False)
    return 'Mails Done'
