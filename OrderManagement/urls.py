"""OrderManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from . import view

urlpatterns = [
    url(r'^$',view.index),
    url(r'^logIn/$',view.logIn),
    url(r'^goRegister/$',view.goRegister),
    url(r'^register/$',view.register),
    url(r'^cashier/$',view.cashier),
    url(r'^check/(?P<idx>[0-9]*)$',view.check),
    url(r'^chef/$',view.chef),
    url(r'^cook/(?P<idx>[0-9]*)$',view.cook),
    url(r'^deliverer/$',view.deliverer),
    url(r'^deliver/(?P<idx>[0-9]*)$',view.deliver),
    url(r'^getOrder/(?P<orderdetail>(.*?))$',view.getOrder),
]
