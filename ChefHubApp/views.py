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

import requests
import random


import firebase_admin
from firebase_admin import credentials, firestore, storage


if not firebase_admin._apps:
    cred = credentials.Certificate(os.path.abspath("chefhub-firebase.json"))
    firebase_admin.initialize_app(cred,{'storageBucket': 'chefhub-8bb79.appspot.com'})



db = firestore.client()
bucket = storage.bucket()


PASS_ENC_DEC_KEY = bytes(os.environ.get("PASS_ENC_DEC_KEY"),'UTF-8')

cipher_suite = Fernet(PASS_ENC_DEC_KEY)

SECRET_KEY_JWT = os.environ.get("SECRET_KEY_JWT")


'''
Function : signup
Methods : Post
Description: adds data to Users and Login table of firebase with encrypted passwords
'''
@api_view(['POST'])
def signup(request):

    if request.method == 'POST':
        data = request.data
        if(type(data)!=dict):
            data=data.dict()
        name = data['name']
        mobileNumber = data['mobilenumber']
        password = cipher_suite.encrypt(bytes(data['password'],'UTF-8'))
        user_type = data['type']
        try :
            checkdata = db.collection('Login').document(mobileNumber).get()
            data_dict = checkdata.to_dict()
            if data_dict:
                return JsonResponse({'success':False,'message':'user exists'})
            data['password'] = password
            db.collection('Users').document(mobileNumber).set(data)
            db.collection('Login').document(mobileNumber).set({"name":name,"password" : password, "type":user_type})
        except:
            return JsonResponse({'success':False, 'message':'Adding Failure'})
        return JsonResponse({'success':True,'message':'successfully added'})



'''
Function : login
Methods : GET
Description: checks the data in the firebase and return a response with jwt-token if valid user 
'''
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
        encoded_jwt = jwt.encode({"mobilenumber":mobileNumber,"password": encoded_password.decode(),'datetime':str(datetime.datetime.now())}, SECRET_KEY_JWT, algorithm="HS256")
        return JsonResponse({'success':True,'message':'Success','token':encoded_jwt})




'''
Function : requestotp
Methods : GET
Description: sends a 6-digit message to the mobilenumber and responds with otp 
'''
@api_view(['GET'])
def requestotp(request):

    if request.method == 'GET':
        data = request.data
        if(type(data)!=dict):
            data=data.dict()
        mobileNumber = data['mobilenumber']
        try :
            url = "https://www.fast2sms.com/dev/bulk"
            payload = "sender_id=ChefHub&message={}&language=english&route=p&numbers={}"
            OTP = str(random.randint(100001, 999999))
            message = "Welcome to ChefHub, Your OTP is : "+OTP
            payload=payload.format(message,mobileNumber)
            print(payload)
            headers = {
            'authorization': os.environ.get("FAST2SMS_AUTHORIZATION_KEY"),
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
            }
            response = requests.request("POST", url, data=payload, headers=headers)
        except:
            return JsonResponse({'success':False, 'message':'Message Sending Failure'})
        return JsonResponse({'success':True,'message':'otp sent','OTP':OTP})