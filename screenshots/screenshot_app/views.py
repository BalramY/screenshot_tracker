from rest_framework.decorators import api_view,permission_classes
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.shortcuts import render,redirect
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from rest_framework.views import APIView
from datetime import datetime, timedelta
from django.shortcuts import render
from rest_framework import status
from django.conf import settings
from .models import *
import os
import re

# Create your views here.
@api_view(['GET'])
def csrf(request):
    return Response({'csrfToken':get_token(request)})

@api_view(['GET','POST'])
def user_login(request):
    """
    Api for login a user

    Returns
    -------
        User id, user token and login mode
    """
    
    if request.method == 'POST':
        username = request.data['username']
        password = request.data['password']
        try:
            user = authenticate(username=username, password=password)
            print(user,'user')
            if user:
                if user.is_active:
                    login(request, user)
                    token = Token.objects.get_or_create(user=user)
                    return Response({'login_mode':'user','id':user.id,'message':'verified','token':token[0].key})
        except ObjectDoesNotExist:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return Response({'message':'Invalid login details given'})
    else:
        return Response()


@api_view(['POST'])
def user_logout(request):
    """
    Api for user logout

    Returns
    -------
        Success message
    """
    
    if request.method == 'POST':
        username = request.data['username']
        user_obj = User.objects.get(username=username,is_staff=False)
        try:
            Token.objects.get(user=user_obj).delete()
        except:
            pass
        logout(request)
        return Response({'message':'Successfullay Logout'})


@api_view(['POST'])
def upload_screenshot(request):
    """
    Api for upload captured screenshots on server

    Returns
    -------
        List of uploaded images
    """

    if 'token' in request.headers:
        token = Token.objects.get(user=User.objects.get(username=request.headers['username']))
        if token.key == request.headers['token']:

            if request.method == 'POST':
                print(request.data)
                print(request.FILES)
                today = datetime.now().strftime('%Y-%m-%d')
                data_dict ={}
                image_list = []

                user_obj = User.objects.get(username=request.data['username'])
                images = request.FILES.getlist('image')
                images.reverse()
                file_path = 'media/images/'
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                    os.chmod(file_path, 0o777)
                    
                for obj in images:

                    img = ImageUploader()
                    img.user = user_obj
                    img.image=obj
                    img.save()
                    image_list.append(img.image.url)
                return Response(image_list)

            return Response()

        else:
            return Response({'details':'Invalid token'})
    else:
        return Response({'details':'Authentication details were not provided'})
