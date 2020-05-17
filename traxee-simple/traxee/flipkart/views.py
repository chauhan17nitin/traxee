from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse

from datetime import timedelta
import datetime
import requests
import json
import firebase_admin
from firebase_admin import auth
from firebase_admin import db
from firebase_admin import credentials

from .forms import UserForm
cred = credentials.Certificate('/home/nitin/Downloads/traxee/github/traxee/traxee-pr-301-firebase-adminsdk-y22ww-2e5aafb334.json')

token_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCRL8ifllPsdT1gFbu_88-hA82VguTCCPM"

default_app = firebase_admin.initialize_app(cred ,{
    'databaseURL' : 'https://traxee-pr-301.firebaseio.com/'
})

root = db.reference()
curr_user={}
curr_user['uid']=None

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
            request.session['uid'] = uid

            response = HttpResponseRedirect(reverse('flipkart:index'))
            response.set_cookie('session', session_cookie, expires=expires)
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


            session_cookie = firebase_admin.auth.create_session_cookie(idToken, expires_in)
            request.session['uid'] = uid
            print(session_cookie)
            response = HttpResponseRedirect(reverse('flipkart:index'))

            response.set_cookie('session', session_cookie, expires=expires)
            print('cookie created successfully')
            return response
        else:
            # print('dd')
            
            return render(request, 'flipkart/authentication.html', {'error_message': 'Invalid login', 'error_in': 'login'})

    return render(request, 'flipkart/authentication.html')

def logout_user(request):

    if request.method == 'GET':
        try:
            del request.session['uid']
            response = HttpResponseRedirect(reverse('flipkart:login'))
            response.delete_cookie('session')
            print('cookie deleted')
            return response
        except Exception as e:
            print(e)
            return render(request, 'flipkart/authentication.html')
