#IMPORTS
from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
import os
import io
from cryptography.fernet import Fernet
import jwt
import datetime
import requests
import random
import firebase_admin
from firebase_admin import credentials, firestore, storage


#APP INITIALIZE
if not firebase_admin._apps:
    cred_dict = {
        "type": "service_account",
        "project_id": "chefhub-8bb79",
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY"),
        "client_email": "firebase-adminsdk-zyic1@chefhub-8bb79.iam.gserviceaccount.com",
        "client_id": "104554908566712336845",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-zyic1%40chefhub-8bb79.iam.gserviceaccount.com"
    }
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred,{'storageBucket': 'chefhub-8bb79.appspot.com'})


#DATA-BASE
db = firestore.client()

#DATA-BUCKET
bucket = storage.bucket()

#PASSWORD-ENCRYPTION-DECRYPTION-KEY
PASS_ENC_DEC_KEY = bytes(os.environ.get("PASS_ENC_DEC_KEY"),'UTF-8')

#CIPHER SUITE TO ENCRYPT AND DECRYPT PASSWORD
cipher_suite = Fernet(PASS_ENC_DEC_KEY)

#SECRET KEY TO GENERATE JWT
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
        data['mobilenumber'] = str(data['mobilenumber'])
        name = data['name']
        mobileNumber = data['mobilenumber']
        encrypted_password = cipher_suite.encrypt(bytes(data['password'],'UTF-8'))
        user_type = data['type']
        try :
            checkdata = db.collection('Login').document(mobileNumber).get()
            data_dict = checkdata.to_dict()
            if data_dict:
                return JsonResponse({'success':False,'message':'user exists'})
            db.collection('Login').document(mobileNumber).set({"name":name,"password" : encrypted_password, "type":user_type})
            del data['password']
            if user_type == "User":
                db.collection('Users').document(mobileNumber).set(data)
            else:
                db.collection('Chefs').document(mobileNumber).set(data)
            return JsonResponse({'success':True,'message':'successfully added'})
        except:
            return JsonResponse({'success':False, 'message':'Adding Failure'})



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
        data['mobilenumber'] = str(data['mobilenumber'])
        mobileNumber = data['mobilenumber']
        password = data['password']
        try :
            result = db.collection("Login").document(mobileNumber).get()
            dictionary = result.to_dict()
            if dictionary == None:
                return JsonResponse({'success':False,'message':"Invalid User"})
            encoded_password = dictionary['password']
            decoded_password = cipher_suite.decrypt(encoded_password).decode("UTF-8")
            if decoded_password != password :
                return JsonResponse({'success':False,'message':'Invalid Password'})
            user_type = dictionary['type']
            encoded_jwt = jwt.encode({"mobilenumber":mobileNumber,'datetime':str(datetime.datetime.now()),'type':user_type}, SECRET_KEY_JWT, algorithm="HS256")
            return JsonResponse({'success':True,'message':'Success','token':encoded_jwt,'type':user_type})
        except:
            return JsonResponse({'success':False,'message':"database error"})



'''
Function : generateOtp
Methods : GET
Description: sends a 6-digit message to the mobilenumber and responds with otp 
'''
@api_view(['GET'])
def generateOtp(request):

    if request.method == 'GET':
        data = request.data
        if(type(data)!=dict):
            data=data.dict()
        data['mobilenumber'] = str(data['mobilenumber'])
        mobileNumber = data['mobilenumber']
        try :
            url = "https://www.fast2sms.com/dev/bulk"
            payload = "sender_id=ChefHub&message={}&language=english&route=p&numbers={}"
            OTP = str(random.randint(100001, 999999))
            message = "Welcome to ChefHub, Your OTP is : "+OTP
            payload=payload.format(message,mobileNumber)
            headers = {
            'authorization': os.environ.get("FAST2SMS_AUTHORIZATION_KEY"),
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
            }
            response = requests.request("POST", url, data=payload, headers=headers)
            return JsonResponse({'success':True,'message':'otp sent','OTP':OTP})
        except:
            return JsonResponse({'success':False, 'message':'Message Sending Failure'})
        



'''
Function : getChefs
Methods : GET
Description: returns details of 6 chefs
'''
@api_view(['GET'])
def getChefs(request):

    if request.method == 'GET':
        data = request.data
        if(type(data)!=dict):
            data=data.dict()
        token = data['token']
        #Need to validate token
        startafter = str(data['start'])
        try:
            res = db.collection("Chefs").order_by("mobilenumber").start_after({'mobilenumber':startafter}).limit(6).get()
            chefs= []
            for chef in res:
                chefs.append(chef.to_dict())
            data = {
                'chefs':chefs,
                'isEnd':True if len(chefs)<6 else False
            }
            return JsonResponse({'success':True,'message':'Fetched chefs data','data':data})
        except:
            return JsonResponse({'success':False,'message':"database error"})


            
