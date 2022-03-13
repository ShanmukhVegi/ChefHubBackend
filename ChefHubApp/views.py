from django.shortcuts import render

from django.http.response import JsonResponse

from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


import os
import io
from io import BytesIO

from cryptography.fernet import Fernet
import jwt
import datetime


import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate(os.path.abspath("chefhub-firebase.json"))
firebase_admin.initialize_app(cred,{'storageBucket': 'chefhub-8bb79.appspot.com'})



db = firestore.client()
bucket = storage.bucket()

key = b'UysF9LLktZez86mfmvClB8nVr6PxuW0TeDyVjpBHJbw='
cipher_suite = Fernet(key)

secret_key_jwt = "ChefHub@123$"


@api_view(['POST'])
def signup(request):

    if request.method == 'POST':
        data = request.data
        if(type(data)!=dict):
            data=data.dict()
        name = data['name']
        mobileNumber = data['mobilenumber']
        password = cipher_suite.encrypt(bytes(data['password'],'utf-8'))
        user_type = data['type']
        try :
            checkdata = db.collection('Login').document(mobileNumber)
            if checkdata:
                return JsonResponse({'success':False,'message':'user exists'})
            db.collection('Users').document(mobileNumber).set(data)
            db.collection('Login').document(mobileNumber).set({"name":name,"password" : password, "type":user_type})
        except:
            return JsonResponse({'success':False, 'message':'Adding Failure'})
        return JsonResponse({'success':True,'message':'successfully added'})




@api_view(['GET'])
def login(request):
    
    if request.method == 'GET':
        data = request.data
        if(type(data)!=dict):
            data=data.dict()
        mobileNumber = data['mobilenumber']
        password = data['password']
        result = db.collection("Login").document(mobileNumber).get()
        dictionary = result.to_dict()
        if dictionary == None:
            return JsonResponse({'success':False,'message':"Invalid User"})
        encoded_password = dictionary['password']
        decoded_password = cipher_suite.decrypt(encoded_password).decode("UTF-8")
        if decoded_password != password :
            return JsonResponse({'success':False,'message':'Invalid Password'})
        encoded_jwt = jwt.encode({"mobilenumber":mobileNumber,"password": encoded_password.decode(),'datetime':str(datetime.datetime.now())}, secret_key_jwt, algorithm="HS256")
        return JsonResponse({'success':True,'message':'Success','token':encoded_jwt})