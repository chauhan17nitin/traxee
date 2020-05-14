from django.shortcuts import render, redirect
from django.contrib import messages

from datetime import timedelta
import datetime
import requests
import json
import firebase_admin
from firebase_admin import auth
from firebase_admin import db
from firebase_admin import credentials

from .forms import UserForm
cred = credentials.Certificate('E:/Projects/PRs/PR-301- AI website/git/traxee/traxee-pr-301-firebase-adminsdk-y22ww-2e5aafb334.json')

token_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCRL8ifllPsdT1gFbu_88-hA82VguTCCPM"

default_app = firebase_admin.initialize_app(cred ,{
    'databaseURL' : 'https://traxee-pr-301.firebaseio.com/'
})

root = db.reference()
curr_user={}
curr_user['uid']=None

# Create your views here.
def index(request):
    # global curr_user
    if curr_user['uid']:
        return render(request, 'flipkart/index.html')
    else:
        return render(request, 'flipkart/home.html')

    

def signup_user(request):

    form = UserForm(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        
        isPremium = 0

        try:
            user = firebase_admin.auth.create_user(email=email, password=password, display_name=name)
            curr_user['uid']=user.uid
            uid = user.uid
            name = user.display_name
    
        except:
            context = {
            "form": form,
            "error_message":"Email already existed",
            }
            return render(request, 'flipkart/signup.html', context)

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
            print(r.json())

            return render(request, 'flipkart/index.html')
    
    context = {
    "form": form,
    }

    return render(request, 'flipkart/signup.html', context)

def login_user(request):

    if request.method == "POST":

        email = request.POST['email']
        password = request.POST['password']

        payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
        })
        
        
        r = requests.post(token_url, data=payload)
        
        if r.status_code == 200:
            l=r.json()
            curr_user['uid']=l['localId']
            return render(request, 'flipkart/index.html')
        else:
            # print('dd')
            return render(request, 'flipkart/login.html', {'error_message': 'Invalid login'})

    return render(request, 'flipkart/login.html')

def logout_user(request):
    uid = curr_user['uid']
    # print(uid)
    auth.revoke_refresh_tokens(uid)
    curr_user['uid']=None
    return render(request, 'flipkart/login.html')
