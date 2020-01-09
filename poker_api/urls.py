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
from django.urls import include
from rest_framework import routers

from poker_api.views import *

router = routers.DefaultRouter()
router.register(r'cards', CardViewSet)
router.register(r'hands', HandViewSet)
router.register(r'packs', PackViewSet)
router.register(r'cardinpack', CardInPackViewSet)
router.register(r'boards', BoardViewSet)
router.register(r'users', UserViewSet)
router.register(r'pokergame', PokerGameViewSet)
router.register(r'useringame', UserInGameViewSet)

urlpatterns = [
    url('',  include(router.urls)),
    # path('article/<id_article>', views.view_article),
    # path('article/<int:id_article>$', views.view_article, name='afficher_article'),
]
# def view_article(request, id_article):
#     """
#     Vue qui affiche un article selon son identifiant (ou ID, ici un numéro)
#     Son ID est le second paramètre de la fonction (pour rappel, le premier
#     paramètre est TOUJOURS la requête de l'utilisateur)
#     """
#     return HttpResponse(
#         "Vous avez demandé l'article n° {0} !".format(id_article)
#     )
# return redirect('afficher_article', id_article=42)
