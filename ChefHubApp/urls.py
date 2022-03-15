from django.conf.urls import url 
from ChefHubApp import views
 
urlpatterns = [ 
    url(r'^signup', views.signup),
    url(r'^login',views.login),
    url(r'^generateOtp',views.generateOtp)
    url(r'^getChefs',views.getChefs)
]