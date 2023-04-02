from django.contrib import admin
from django.urls import path
from index import views

urlpatterns = [
    path("",views.index,name="index"),
    path("dryrun/",views.dryrun,name='dryrun'),
   
] 

