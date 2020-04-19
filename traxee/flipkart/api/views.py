from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SignInSerializers, TokenSerializer, SignUpSerializers, ForgotPasswordSerializer, SearchItemSerializer
from rest_framework import status
from datetime import timedelta
import requests
import json
import firebase_admin
from firebase_admin import auth
from firebase_admin import db
from firebase_admin import credentials


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

            session_time = timedelta(days=5)

            payload = json.dumps({
                "email": email,
                "password": password,
                "returnSecureToken": True
            })

            r = requests.post(rest_api_url, data=payload)
            
            # print(resp)
            # if resp["idToken"]:
            #     session_string = firebase_admin.auth.create_session_cookie(r['idToken'], session_time)
            #     print(session_string)
            # else:
            #     pass
            return Response(r.json(), status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)

