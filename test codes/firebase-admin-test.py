import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("traxee-pr-301-firebase-adminsdk.json")
t=firebase_admin.initialize_app(cred)

uid='05FuBSGAmQRronbyOKL85Y5m6Em1'
user = auth.get_user(uid)
print('Successfully fetched user data: {0}'.format(user.email))