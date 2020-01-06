from rest_framework import serializers
from .models import *


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'value', 'color')


class HandSerializer(serializers.ModelSerializer):
    cardList = CardSerializer(many=True)

    class Meta:
        model = Hand
        fields = ('id', 'cardList')


class PackSerializer(serializers.ModelSerializer):
    cardList = CardSerializer(many=True)

    class Meta:
        model = Pack
        fields = ('id', 'cardList')


class CardInPackSerializer(serializers.ModelSerializer):
    card = CardSerializer()

    class Meta:
        model = CardInPack
        fields = ('id', 'card', 'pack', 'is_draw')


class BoardSerializer(serializers.ModelSerializer):
    cardList = CardInPackSerializer(many=True)

    class Meta:
        model = Board
        fields = ('id', 'cardList')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'money', 'online')


class PokerGameSerializer(serializers.ModelSerializer):
    board = BoardSerializer()
    pack = PackSerializer()
    userList = UserSerializer(many=True)

    class Meta:
        model = PokerGame
        fields = ('id', 'userList', 'pack', 'board', 'pot', 'blind', 'state', 'game_round')


class UserInGameSerializer(serializers.ModelSerializer):
    hand = HandSerializer()
    user = UserSerializer()

    class Meta:
        model = UserInGame
        fields = ('id', 'user', 'game', 'hand', 'bet', 'in_game', 'is_dealer', 'is_turn')
