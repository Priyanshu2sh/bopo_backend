"""
URL configuration for bopo_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('', include('bopo_admin.urls')),
    path('api/point/', include('bopo.urls')),
    path('api/redeemAwardPoints/', include('bopo_award.urls')),
    path('api/transactionHistory/', include('transaction_history.urls')),
    path('api/qr/', include('qr_store.urls')),
    path('api/transfer/', include('transfer.urls')),
    
    # state , city
    path('bopo_admin/', include('bopo_admin.urls')), 


]
