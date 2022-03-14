from rest_framework.decorators import api_view

import requests
import random
import os

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
            payload.format(message,mobileNumber)
            print(payload)
            headers = {
            #'authorization': "gNHOw26kaWRV4QEyrGB9xcYnquhfTj18Lt3DbFU0d5oizCKISlJCU9qaShMyAB3cPIvmfQO8XoRdZEFs",
            'authorization': os.environ.get("FAST2SMS_AUTHORIZATION_KEY"),
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
            }
            response = requests.request("POST", url, data=payload, headers=headers)
        except:
            return JsonResponse({'success':False, 'message':'Message Sending Failure'})
        return JsonResponse({'success':True,'message':"otp sent",'otp':OTP})
