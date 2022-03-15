from django.conf.urls import url 
from ChefHubApp import views
 
urlpatterns = [ 
    url(r'^signup', views.signup),
    url(r'^login',views.login),
    url(r'^generateotp',views.requestOtp)
]