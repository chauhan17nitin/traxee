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
            return Response({"mssg": "USer is Logged Out"}, status=status.HTTP_200_OK)

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

class CheckView(APIView):
    def get(self, request, format=None):
        
        id_token ="eyJhbGciOiJSUzI1NiIsImtpZCI6IjBiYWJiMjI0NDBkYTAzMmM1ZDAwNDJjZGFhOWQyODVjZjhkMjAyYzQiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiTml0aW4iLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdHJheGVlLXByLTMwMSIsImF1ZCI6InRyYXhlZS1wci0zMDEiLCJhdXRoX3RpbWUiOjE1ODc0MTY5MzYsInVzZXJfaWQiOiJ4TUdDeEp6M1RJYVREaXRRUHZxbUVtSk50WTQzIiwic3ViIjoieE1HQ3hKejNUSWFURGl0UVB2cW1FbUpOdFk0MyIsImlhdCI6MTU4NzQxNjkzNiwiZXhwIjoxNTg3NDIwNTM2LCJlbWFpbCI6Im5pdG5oYW4xOUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsibml0bmhhbjE5QGdtYWlsLmNvbSJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.UY3fCtRiSqa4tLPuXMft4Mjl5CLPkN2McIS_bka-QyEIkQaH5nblHuwHjRHUUWDavixtRfD9CraVINvInTFjH2z3nYF1i_Q4pSE56Tjfani2Yd-VlrH-EDe7GhgJd_4tEmGseZ6j9ng730F7QY2DlmJguDh6YSShoadEMXalvuqJWg4ZFnV6jAIrTpVFINgkoBTYnFkrIF5L5LVg9Q3bUV8f8jqJLbBZ5o5xKuXl2etVVzGaDX2j7vrQ0NNEYlpTm6sbnitPYZZUHOn6VXL5qUcdrOVMf6O-EvacxWzcb4MAYjbJNO4i9LuTFxQfsgLVYCFh0uREEBIGWbeyzqMCxQ"
        user = firebase_admin.auth.verify_id_token(id_token, app=None, check_revoked=True)
        session_cookie = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjBwUjNXdyJ9.eyJpc3MiOiJodHRwczovL3Nlc3Npb24uZmlyZWJhc2UuZ29vZ2xlLmNvbS90cmF4ZWUtcHItMzAxIiwibmFtZSI6Ik5pdGluIiwiYXVkIjoidHJheGVlLXByLTMwMSIsImF1dGhfdGltZSI6MTU4NzQxNjkzNiwidXNlcl9pZCI6InhNR0N4SnozVElhVERpdFFQdnFtRW1KTnRZNDMiLCJzdWIiOiJ4TUdDeEp6M1RJYVREaXRRUHZxbUVtSk50WTQzIiwiaWF0IjoxNTg3NDE2OTM4LCJleHAiOjE1ODc4NDg5MzgsImVtYWlsIjoibml0bmhhbjE5QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJuaXRuaGFuMTlAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.B9LyHwJOmIbZ1XE68QbyzEJb69mXZ66IPkvWnbahfYA8Ub9OZV0AgSspKf-fae6f3weAlEdsdCKnxO_ZXI3VCSpwWY5uhtfSbP-7dZ0BZ0LLGpViosP8YDquKzI2D68OISDdf-kSLQdWOy06sOGiUKNNSUryrxv4MVdkqMu6HigCzkKMU7svPbR4BikccAwwKcgvmZmL-jlDTCgQifVf6v7LcPEDHAzaLkGZN3LfVaHB1lO_kghM2hWg_2BB_Nnqa7BotOZnrY4M_wojIp4II3UWv79naHfGo05yQK4-RL6reBfyl7OVJSOVK8iksNwelNB6bPTUX2fMs7MOEmB1Dg"
        cookie = firebase_admin.auth.verify_session_cookie(session_cookie, check_revoked=True, app=None)
        return Response({"mssg": user, "cookie": cookie}, status=status.HTTP_200_OK)
