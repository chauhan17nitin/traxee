import firebase_admin
from firebase_admin import auth
from firebase_admin import db
from firebase_admin import credentials


cred = credentials.Certificate('E:/Projects/PRs/PR-301- AI website/git/traxee/traxee-pr-301-firebase-adminsdk-y22ww-2e5aafb334.json')

default_app = firebase_admin.initialize_app(cred ,{
    'databaseURL' : 'https://traxee-pr-301.firebaseio.com/'
})

root = db.reference()
print(default_app)
email='fas@gmail.com'
password='fsdffs'
name='sdas'
isPremium=0
user = firebase_admin.auth.create_user(email=email, password=password, display_name=name)
uid = user.uid
print(user.display_name)
if isPremium:
    data = {"user-type": "Premium"}
    new_user = root.child('users').child(uid).child('subscription').set(data)
else:
    data = {"user-type": "Basic"}
    new_user = root.child('users').child(uid).child('subscription').set(data)








