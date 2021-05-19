"""proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

import app.views as views

urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls),
    path('cohort/<int:cohort_id>/', views.cohort),
    # url(r'^cohort/infos/$', views.cohort_infos),
    url(r'^cohort/create/$', views.create_cohort),
    url(r'^cohort/create/sub/$', views.create_sub_cohort),
    path('cohort/update/<int:cohort_id>/', views.update_cohort),
    path('cohort/delete/<int:cohort_id>/', views.delete_cohort),
    path('cohort/add/sharing/<int:cohort_id>/<int:user_id>/',
         views.add_sharing_cohort),
    path('cohort/remove/sharing/<int:cohort_id>/<int:user_id>/',
         views.remove_sharing_cohort),
    path('login/', views.login),
    path('logout/', views.logout),
    path('me/', views.me),
    path('friends/', views.get_friends),
    path('terms/<int:cohort_id>/', views.terms),
    path('variants/<int:cohort_id>/<int:start>/<int:size>/', views.variants),
    # url(r'^vcf/', views.vcf),
    # url(r'^vcfs/', views.vcfs),
]
