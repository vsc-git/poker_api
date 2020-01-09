from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework.response import Response

from .serializers import *


class GameListView(views.APIView):
    def get(self, request):
        serializer = PokerGameLightSerializer(PokerGame.objects.all(), many=True)
        return Response(serializer.data)


class GameView(views.APIView):
    def get(self, request, game_id):
        poker_game = get_object_or_404(PokerGame.objects.filter(id=int(game_id)))
        serializer = PokerGamePublicSerializer(poker_game)
        return Response(serializer.data)

    def put(self, request, game_id):
        query = PokerGame.objects.filter(id=int(game_id))
        if not query:
            print(f'Poker game {game_id} not found. create a new one')
            poker_game = PokerGame.create(game_id)
        else:
            poker_game = query.first()
        serializer = PokerGamePublicSerializer(poker_game)
        return Response(serializer.data)

    def delete(self, request, game_id):
        if not game_id:
            raise Http404()
        poker_game = get_object_or_404(PokerGame.objects.filter(id=int(game_id)))
        poker_game.delete()
        return Response()


class UserListView(views.APIView):
    def get(self, request):
        serializer = UserSerializer(User.objects.all(), many=True)
        return Response(serializer.data)


class UserView(views.APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User.objects.filter(id=int(user_id)))
        serializer = UserInGamePublicSerializer(user.useringame_set, many=True)
        return Response(serializer.data)

    def put(self, request, user_id):
        query = User.objects.filter(id=int(user_id))
        if not query:
            print(f'User {user_id} not found. create a new one')
            user = User.create(user_id)
        else:
            user = query.first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def delete(self, request, user_id):
        if not user_id:
            raise Http404()
        user = get_object_or_404(User.objects.filter(id=int(user_id)))
        user.delete()
        return Response()


class UserInGameView(views.APIView):

    def get(self, request, game_id, user_id):
        if not game_id:
            raise Http404()
        poker_game: PokerGame = get_object_or_404(PokerGame.objects.filter(id=int(game_id)))
        user_in_game = get_object_or_404(poker_game.useringame_set.filter(user__id=user_id))
        return Response(UserInGamePrivateSerializer(user_in_game).data)

    def put(self, request, game_id, user_id):
        if not game_id:
            raise Http404()
        poker_game: PokerGame = get_object_or_404(PokerGame.objects.filter(id=int(game_id)))
        user_query = poker_game.user_list.filter(id=user_id)
        if not user_query:
            # user not create in this game, need to add it
            user = get_object_or_404(User.objects.filter(id=user_id))
            user_in_game = UserInGame.create(user, poker_game)
        else:
            user_in_game = user_query.first()
        return Response(UserInGamePrivateSerializer(user_in_game).data)

    def delete(self, request, game_id, user_id):
        if not game_id or not user_id:
            raise Http404()
        poker_game: PokerGame = get_object_or_404(PokerGame.objects.filter(id=int(game_id)))
        user_in_game = get_object_or_404(poker_game.useringame_set.filter(user__id=user_id))
        user_in_game.delete()
        return Response()


class TestView(views.APIView):

    def get(self, request):
        # game = PokerGame.create()
        return Response()
