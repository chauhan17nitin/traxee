from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SignInSerializers, TokenSerializer, SignUpSerializers, ForgotPasswordSerializer, SearchItemSerializer
from rest_framework import status
from datetime import timedelta
import datetime
import requests
import json
import firebase_admin
from firebase_admin import auth
from firebase_admin import db
from firebase_admin import credentials

# importing tools for scrapping
import requests
from bs4 import BeautifulSoup
import re
import time


cred = credentials.Certificate('/home/nitin/Downloads/traxee-pr-301-firebase-adminsdk-y22ww-2e5aafb334.json')

rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCRL8ifllPsdT1gFbu_88-hA82VguTCCPM"

default_app = firebase_admin.initialize_app(cred ,{
    'databaseURL' : 'https://traxee-pr-301.firebaseio.com/'
})

root = db.reference()





class SignUpView(APIView):

    def post(self, request, format=None):
        serializer = SignUpSerializers(data = request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            name = serializer.validated_data['name']
            password = serializer.validated_data['password']
            isPremium = serializer.validated_data['isPremium']

            user = firebase_admin.auth.create_user(email=email, password=password, display_name=name)
            uid = user.uid
            name = user.display_name
            

            if isPremium:
                data = {"user-type": "Premium"}
                new_user = root.child('users').child(uid).child('subscription').set(data)
            else:
                data = {"user-type": "Basic"}
                new_user = root.child('users').child(uid).child('subscription').set(data)

            message = "Account Created"
            return Response({"mssg": message, "name": name}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)

class SignInView(APIView):

    def post(self, request, format=None):
        serializer = SignInSerializers(data = request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            expires_in = timedelta(days=5)

            payload = json.dumps({
                "email": email,
                "password": password,
                "returnSecureToken": True
            })

            r = requests.post(rest_api_url, data=payload)
            print(r.status_code)
            resp = r.json()

            if r.status_code == 200:
                idToken = str(resp['idToken'])
                expires = datetime.datetime.now() + expires_in
                uid = str(resp['localId'])
                session_cookie = firebase_admin.auth.create_session_cookie(idToken, expires_in)
                request.session['uid'] = idToken
            
                response = Response(r.json(), status=status.HTTP_200_OK)
                response.set_cookie('session', session_cookie, expires=expires)
                print('cookie gain created')
                return response
            else:
                # print(e)
                return Response(r.json(), status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)

class IndexView(APIView):

    def get(self, request, format=None):

        try:
            value = request.COOKIES['session']

            return Response({"mssg": value}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"mssg": "User is Logged Out"}, status=status.HTTP_200_OK)

class LogoutView(APIView):

    def get(self, request, format=None):
        try:
            del request.session['uid']
            response = Response({"mssg": "cookie deleted anna"} ,status=status.HTTP_200_OK)
            response.delete_cookie('session')
            print('session and cookies deleted')
            return response
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_200_OK)

class SearchView(APIView):

    def post(self, request, format=None):
        serializer = SearchItemSerializer(data = request.data)

        if serializer.is_valid():
            item = serializer.validated_data['item']
            # editing string
            item = re.sub(" ", "%20", item)
            item_search = "https://www.flipkart.com/search?q="+item

            page = requests.get(item_search)
            soup = BeautifulSoup(page.content, 'html.parser')

            all_products = soup.find_all('div', class_='_1UoZlX')
            products_list = []
            # there are two common style in which data can exists on a flipkart page
            # so using if and else
            if len(all_products) != 0:
                for product in all_products:

                    for a in product.find_all("a", href=True):
                        product_id = re.findall("\w?pid.*&lid", a['href'])
                        product_id = product_id[0][4: -4]
                        product_link = 'flipkart.com' + a['href']
                    product_name = product.find_all('div', class_="_3wU53n")
                    product_name = product_name[0].text

                    # finding current price
                    price_string = product.find_all('div', class_ = "_1vC4OE _2rQ-NK")
                    price_string = price_string[0].text[1:]
                    current_price = re.sub(",", "", price_string)
                    current_price = int(current_price)

                    cost_price_string = product.find_all('div', class_="_3auQ3N _2GcJzG")

                    try:
                        cost_price_string = cost_price_string[0].text[1:]
                        cost_price = re.sub(",", "", cost_price_string)
                        cost_price = int(cost_price)
                    except:
                        cost_price = current_price
                    
                    discount = ((cost_price-current_price)/cost_price)*100
                    discount = int(discount)

                    configuration = product.find_all('li', class_="tVe95H")
                    conf_list = []
                    for conf in configuration:
                        conf_list.append(conf.text)
                    
                    # as description is coming as lists so just joining it into a string with so that it can be easily stored in firebase
                    # whenever it will be parsed to the frontend we will first convert the string to list and will parse it to frontend
                    # so that we can easily loop through the configurations
                    description = "|||".join(conf_list)
                    timestamp = int(time.time())

                    product_save = {
                        'product_link': product_link,
                        'product_name': product_name,
                        'current_price': current_price,
                        'description': description,
                    }

                    # checking presence of the particular product in the database previously
                    snapshot = root.child('products').child(product_id).get()

                    # adding product information to database
                    if snapshot is None:
                        root.child('products').child(product_id).set(product_save)
                    else:
                        root.child('products').child(product_id).update({
                            'current_price': current_price
                        })
                    
                    history = {
                        'current_price': current_price,
                        'discount': discount,
                        'cost_price': cost_price
                    }
                    
                    # adding price history
                    root.child('history').child(product_id).child(str(timestamp)).set(history)

            else:
                all_products = soup.find_all('div', class_='_3liAhj')
                for product in all_products:
                    for a in product.find_all("a", class_='Zhf2z-', href=True):
                        product_id = re.findall("\w?pid.*&lid", a['href'])
                        product_id = product_id[0][4: -4]
                        product_link = 'flipkart.com' + a['href']
                    product_name = product.find_all("a", class_="_2cLu-l")
                    product_name = product_name[0].text
                    
                    price_string = product.find_all('div', class_ = "_1vC4OE")
                    price_string = price_string[0].text[1:]
                    
                    current_price = re.sub(",", "", price_string)
                    current_price = int(current_price)
                    
                    cost_price_string = product.find_all('div', class_="_3auQ3N")
    
                    try:
                        cost_price_string = cost_price_string[0].text[1:]
                        cost_price = re.sub(",", "", cost_price_string)
                        cost_price = int(cost_price)
                    except:
                        cost_price = current_price
                        
                    discount = ((cost_price-current_price)/cost_price)*100
                    discount = int(discount)
                    
                    
                    configuration = product.find_all('div', class_="_1rcHFq")
                    conf_list = []
                    for conf in configuration:
                        conf_list.append(conf.text)

                    # as description is coming as lists so just joining it into a string with so that it can be easily stored in firebase
                    # whenever it will be parsed to the frontend we will first convert the string to list and will parse it to frontend
                    # so that we can easily loop through the configurations
                    description = "|||".join(conf_list)
                    timestamp = int(time.time())

                    product_save = {
                        'product_link': product_link,
                        'product_name': product_name,
                        'current_price': current_price,
                        'description': description,
                    }

                    snapshot = root.child('products').child(product_id).get()
                    
                    # adding product information to database
                    if snapshot is None:
                        root.child('products').child(product_id).set(product_save)
                    else:
                        root.child('products').child(product_id).update({
                            'current_price': current_price
                        })

                    history = {
                        'current_price': current_price,
                        'discount': discount,
                        'cost_price': cost_price
                    }
                    
                    # adding price history into database
                    root.child('history').child(product_id).child(str(timestamp)).set(history)
            return Response({"mssg": 'done', "name": 'done'}, status=status.HTTP_200_OK)


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

    return None
                    
                                    
