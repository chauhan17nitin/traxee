from django.urls import path

from .views import  SignUpView, SignInView, IndexView, LogoutView, CheckView
urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('signin/', SignInView.as_view(), name="signin"),
    path('index/', IndexView.as_view(), name="index"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('check/', CheckView.as_view(), name="check"),
    
]