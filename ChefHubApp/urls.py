from django.conf.urls import url 
from ChefHubApp import views 
from ChefHubApp import transactions
 
urlpatterns = [ 
    url(r'^signup', views.signup),
    url(r'^login',views.login),
    url(r'^generateotp',transactions.requestotp)
]