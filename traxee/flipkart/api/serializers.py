from rest_framework import serializers
from django.db.models.fields import EmailField
from django.db.models.fields import PositiveIntegerField

class SignUpSerializers(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField()
    password = serializers.CharField()
    isPremium = serializers.BooleanField()



class SignInSerializers(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class SearchItemSerializer(serializers.Serializer):
    item = serializers.CharField()