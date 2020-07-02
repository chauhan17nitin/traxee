from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from datetime import timedelta
import datetime
import requests
import json
import firebase_admin
from firebase_admin import auth
from firebase_admin import db
from firebase_admin import credentials
from django.http import JsonResponse

import time

from .forms import UserForm

# imports for mailing facility
from django.core.mail import send_mail
from traxee.settings import EMAIL_HOST_USER

cred = credentials.Certificate('./../../traxee-pr-301-firebase-adminsdk-y22ww-2e5aafb334.json')

token_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCRL8ifllPsdT1gFbu_88-hA82VguTCCPM"

default_app = firebase_admin.initialize_app(cred ,{
    'databaseURL' : 'https://traxee-pr-301.firebaseio.com/'
})

root = db.reference()
curr_user={}
curr_user['uid']=None

def signup_email(email_id, name):
    subject = "Welcome {} to traXee".format(name)
    message = "Hi {}, Welcome to traXee.\n A all time solution for tracking flipkart products. All your shoppings problems are ours now.\n Enjoying Using traXee \n Regards \n Founder \n Tanzeel Alam".format(name)
    send_mail(subject, message, EMAIL_HOST_USER, [email_id], fail_silently = False)

    return None

def index(request):

    if request.method == "GET":
        if request.COOKIES.get('session'):
            return render(request, 'flipkart/index.html')
        else:
            return render(request, 'flipkart/authentication.html')


def signup_user(request):

    if request.method == "POST":
        name = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        isPremium = 0

        try:
            user = firebase_admin.auth.create_user(email=email, password=password, display_name=name)
            curr_user['uid']=user.uid
            uid = user.uid
            name = user.display_name

        except Exception as e:
            if type(e).__name__=='ValueError':
                context = {
                    "error_message": "Provide Valid Email or Password",
                    "error_in": 'signup'
                    }
            if type(e).__name__=='EmailAlreadyExistsError':
                context = {
                    "error_message": "Email Already Existed",
                    'error_in': 'signup'
                    }
            # print(e)
            return render(request, 'flipkart/authentication.html', context)

        if isPremium:
            data = {"user-type": "Premium"}
            new_user = root.child('users').child(uid).child('subscription').set(data)
        else:
            data = {"user-type": "Basic"}
            new_user = root.child('users').child(uid).child('subscription').set(data)

        if user:
            # sending a signup email to the new user
            signup_email(email, name)

            payload = json.dumps({
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
            })

            r = requests.post(token_url, data=payload)
            resp = r.json()
            idToken = str(resp['idToken'])
            expires_in = timedelta(days=5)
            expires = datetime.datetime.now() + expires_in
            uid = str(resp['localId'])


            session_cookie = firebase_admin.auth.create_session_cookie(idToken, expires_in)
            # request.session['uid'] = uid

            response = HttpResponseRedirect(reverse('flipkart:index'))
            response.set_cookie('session', session_cookie, expires=expires)
            response.set_cookie('uid', uid, expires=expires)
            print('cookie created successfully')
            return response

    context = {
        'error_in': 'signup'
        }
    return render(request, 'flipkart/authentication.html', context)

def login_user(request):

    if request.method == "POST":

        email = request.POST['email']
        password = request.POST['password']

        expires_in = timedelta(days=5)

        payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
        })

        r = requests.post(token_url, data=payload)
        resp = r.json()
        if r.status_code == 200:
            idToken = str(resp['idToken'])
            expires = datetime.datetime.now() + expires_in
            uid = str(resp['localId'])
            print(uid)

            session_cookie = firebase_admin.auth.create_session_cookie(idToken, expires_in)
            # request.session['uid'] = uid

            response = HttpResponseRedirect(reverse('flipkart:index'))

            response.set_cookie('session', session_cookie, expires=expires)
            response.set_cookie('uid', uid, expires=expires)
            print('cookie created successfully')
            return response
        else:
            print(r.status_code)
            return render(request, 'flipkart/authentication.html', {'error_message': 'Invalid login', 'error_in': 'login'})

    return render(request, 'flipkart/authentication.html')

def logout_user(request):

    if request.method == 'GET':
        try:
            # del request.session['uid']
            response = HttpResponseRedirect(reverse('flipkart:login'))
            response.delete_cookie('session')
            response.delete_cookie('uid')
            print('cookie deleted')
            return response
        except Exception as e:
            print(e)
            return render(request, 'flipkart/authentication.html')

def search_product(request):

    if request.method == 'GET':
        query = request.GET.get("q", False)
        print(query)
        HEADERS = {
            "Fk-Affiliate-Id": "shaikhajw",
            "Fk-Affiliate-Token": "431799c9268040bebdb683698d6736da"
            }

        PARAMS = {
                "query": query,
                "resultCount": 5
                }
        URL = "https://affiliate-api.flipkart.net/affiliate/1.0/search.json"

        r = requests.get(url = URL, params = PARAMS, headers=HEADERS)

        if r.status_code == 200 :
            data = r.json()
            products = []
            for product in data['products']:
                product_id = product['productBaseInfoV1']['productId']
                product_name = product['productBaseInfoV1']['title']
                product_link = product['productBaseInfoV1']['productUrl']
                current_price = product['productBaseInfoV1']['flipkartSpecialPrice']
                cost_price = product['productBaseInfoV1']['flipkartSellingPrice']
                description = product['categorySpecificInfoV1']['keySpecs']
                # print(product_id)
                # in future to add try except may be the particular size not present
                image_link = product['productBaseInfoV1']['imageUrls']['400x400']

                discount = ((cost_price['amount']-current_price['amount'])/cost_price['amount'])*100
                discount = int(discount)

                timestamp = int(time.time())

                product_save = {
                    'product_link': product_link,
                    'product_name': product_name,
                    'current_price': current_price,
                    'description': description,
                    'image_link': image_link
                }

                # checking presence of the particular product in the database previously
                snapshot = root.child('products').child(product_id).get()

                if snapshot is None:
                    root.child('products').child(product_id).set(product_save)
                    history = {
                            'current_price': current_price,
                            'discount': discount,
                            'cost_price': cost_price
                        }
                    # adding price history for first time
                    root.child('history').child(product_id).child(str(timestamp)).set(history)
                else:
                    root.child('products').child(product_id).update({
                            'current_price': current_price
                        })

                product_save['product_id'] = product_id
                products.append(product_save)

            return render(request, 'flipkart/searched.html', {'result': products})

        else:
            return render(request, 'flipkart/index.html')


def add_track(request, product_id):

    if request.method == 'GET':
        if request.COOKIES.get('session'):
            # check how long session variable stays this is in testing mode
            # user_id = request.session['uid']
            user_id = request.COOKIES.get('uid')
            check = root.child('users').child(user_id).child('favourites').child(product_id).get()
            if check:
                messages.success(request, 'The product is being tracked already')
                return display_track(request)
            else:
                root.child('notifications').child(product_id).child(user_id).set(1)
                root.child('users').child(user_id).child('favourites').child(product_id).set(1)
                return display_track(request)
        else:
            return render(request, 'flipkart/authentication.html')

def add_trackapi(request):
    if request.method == "POST":
        if request.COOKIES.get('session'):
            user_id = request.COOKIES.get('uid')
            product_id = request.POST.get('product_id')
            check = root.child('users').child(user_id).child('favourites').child(product_id).get()
            if check:
                return JsonResponse({'message': 'Already on Track'}, status=403)
            else:
                root.child('notifications').child(product_id).child(user_id).set(1)
                root.child('users').child(user_id).child('favourites').child(product_id).set(1)
                return JsonResponse({'message': 'Added to tracks'}, status=200)
        else:
            return JsonResponse({'message': 'Login First'}, status=401)
    else:
        return JsonResponse({'message': 'Invalid Access'}, status=422)

def remove_trackapi(request):
    if request.method == "POST":
        if request.COOKIES.get('session'):
            user_id = request.COOKIES.get('uid')
            product_id = request.POST.get('product_id')
            ref = root.child('notifications').child(product_id).child('users').child(user_id)
            ref.delete()
            root.child('users').child(user_id).child('favourites').child(product_id).delete()
            return JsonResponse({'message': 'Deleted'}, status = 200)
        else:
            return JsonResponse({'message': 'Login First'}, status=401)
    else:
        return JsonResponse({'message': 'Invalid Access'}, status=422)

def remove_track(request, product_id):

    # if request.method == 'GET':
    if request.COOKIES.get('session'):
        # check session variable stays how long
        # user_id = request.session['uid']
        user_id = request.COOKIES.get('uid')
        ref = root.child('notifications').child(product_id).child('users').child(user_id)
        ref.delete()

        root.child('users').child(user_id).child('favourites').child(product_id).delete()
        return display_track(request)
    else:
        return render(request, 'flipkart/authentication.html')





def display_track(request):
    if request.method == 'GET':
        if request.COOKIES.get('session'):
            user_id = request.COOKIES['uid']
            p = root.child('users').child(user_id).child('favourites').get()        
            print('...')    
            # user_id = request.session['uid']
            user_id = request.COOKIES.get('uid')
            p = root.child('users').child(user_id).child('favourites').get()
            products=[]
            if p is None:
                messages.success(request, 'Your Tracking Cart is Empty Please Search Products and add them to track')
                return render(request, 'flipkart/tracked.html')
            for key,_ in p.items():
                detail={}
                d = root.child('products').child(key).get()
                detail['product_id'] = key
                detail['product_price'] = d['current_price']['amount']
                detail['product_name'] = d['product_name']
                if 'image_link' in d:
                    detail['image_link'] = d['image_link']
                detail['product_link'] = d['product_link']

                products.append(detail)

            return render(request, 'flipkart/tracked.html', {'products':products})
        else:
            return render(request, 'flipkart/authentication.html')

def details(request, product_id):
    if request.method == 'GET':
        if request.COOKIES.get('session'):
            ref_history = root.child('history').child(product_id).get()
            ref_product = root.child('products').child(product_id).get()
            return render(request, 'flipkart/history.html', context = {'history_json' : json.dumps(ref_history), 'product' : ref_product})
    if request.method == 'POST':
        price = request.POST.get('price_input')
        if price.isdigit():
            user_id = request.COOKIES.get('uid')
            root.child('notifications').child(product_id).child(user_id).set(price)
            print(price, user_id, product_id)
            return HttpResponseRedirect(request.path_info)




