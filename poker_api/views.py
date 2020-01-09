from rest_framework import viewsets
from .serializers import *


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer


class HandViewSet(viewsets.ModelViewSet):
    queryset = Hand.objects.all()
    serializer_class = HandSerializer


class PackViewSet(viewsets.ModelViewSet):
    queryset = Pack.objects.all()
    serializer_class = PackSerializer


class CardInPackViewSet(viewsets.ModelViewSet):
    queryset = CardInPack.objects.all()
    serializer_class = CardInPackSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PokerGameViewSet(viewsets.ModelViewSet):
    queryset = PokerGame.objects.all()
    serializer_class = PokerGameSerializer


class UserInGameViewSet(viewsets.ModelViewSet):
    queryset = UserInGame.objects.all()
    serializer_class = UserInGameSerializer
