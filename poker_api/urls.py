"""poker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from poker_api.views import *

urlpatterns = [
    url(r'test', TestView.as_view(), name='test_list_view'),
    url(r'user/(?P<user_id>\d+)', UserView.as_view(), name='game_view'),
    url(r'(?P<game_id>\d+)/(?P<user_id>\d*)', UserInGameView.as_view(), name='user_in_game_view'),
    url(r'(?P<game_id>\d+)', GameView.as_view(), name='game_view'),
    url(r'user', UserListView.as_view(), name='user_list_view'),
    url(r'', GameListView.as_view(), name='game_list_view'),
]
