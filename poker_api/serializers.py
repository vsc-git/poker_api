from rest_framework import serializers

from .models import *


class CardSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ['value']

    def get_value(self, obj):
        return str(obj)


class HandSerializer(serializers.ModelSerializer):
    card_list = CardSerializer(many=True)

    class Meta:
        model = Hand
        fields = ('id', 'card_list')


class PackSerializer(serializers.ModelSerializer):
    card_list = CardSerializer(many=True)

    class Meta:
        model = Pack
        fields = ('id', 'card_list')


class CardInPackSerializer(serializers.ModelSerializer):
    card = CardSerializer()

    class Meta:
        model = CardInPack
        fields = ('id', 'card', 'is_draw')


class BoardSerializer(serializers.ModelSerializer):
    card_list = CardSerializer(many=True)

    class Meta:
        model = Board
        fields = ('id', 'card_list')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'money', 'online')


class UserInGamePublicSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserInGame
        fields = ('id', 'user', 'game', 'bet', 'in_game', 'is_dealer', 'is_turn', 'has_speak')


class PokerGamePublicSerializer(serializers.ModelSerializer):
    board = BoardSerializer()
    useringame_set = UserInGamePublicSerializer(many=True)
    state = serializers.SerializerMethodField()

    class Meta:
        model = PokerGame
        fields = ('id','useringame_set', 'board', 'pot', 'blind', 'state', 'processing', 'game_round')

    def get_state(self, obj):
        return list(filter(lambda dict : dict[0]==obj.state, PokerGame.POKER_GAME_STATE))[0][1]


class UserInGamePrivateSerializer(serializers.ModelSerializer):
    hand = HandSerializer()
    user = UserSerializer()
    game = PokerGamePublicSerializer()

    class Meta:
        model = UserInGame
        fields = ('id', 'user', 'hand', 'bet', 'in_game', 'is_dealer', 'is_turn', 'has_speak', 'game')


class PokerGameLightSerializer(serializers.ModelSerializer):
    user_number = serializers.SerializerMethodField()

    class Meta:
        model = PokerGame
        fields = ('id', 'user_number', 'game_round')

    def get_user_number(self, obj):
        return obj.user_list.count()


