"""
URL configuration for FastTrade project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from TradeApp.views import index_page, auto, rec_short, LINK_TO_COIN,COIN_LINK,rec_long,rec

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name = 'main'),
    path('FastTrade/templates/TradeApp/auto.html', auto, name = 'auto'),
    path('FastTrade/templates/TradeApp/short.html', rec_short, name = 'rec_short'),
    path('FastTrade/templates/TradeApp/rec.html', rec_long, name = 'rec_long'),
    path('FastTrade/templates/TradeApp/rec.html', rec, name = 'rec'),

    # path('FastTrade\templates\TradeApp\main.html', buy, name = 'buy'),
    path(COIN_LINK, LINK_TO_COIN,name = 'LINK'),
    # path('https://www.binance.com/api/v3/avgPrice', LINK_TO_COIN,name = 'LINK'),
    ]
