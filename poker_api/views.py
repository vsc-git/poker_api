from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import views

from .poker_engine import PokerEngine
from .score import ScoreCalculator
from .serializers import *
from .utils import *


class GameListView(views.APIView):
    def get(self, request) -> Response:
        serializer = PokerGameLightSerializer(PokerGame.objects.all(), many=True)
        return Response(serializer.data)


class GameView(views.APIView):
    def get(self, request, game_id) -> Response:
        poker_game = get_object_or_404(PokerGame.objects.filter(id=int(game_id)))
        serializer = PokerGamePublicSerializer(poker_game)
        return Response(serializer.data)

    def put(self, request, game_id) -> Response:
        query = PokerGame.objects.filter(id=int(game_id))
        if not query:
            print(f'Poker game {game_id} not found. create a new one')
            poker_game = PokerGame.create(game_id)
        else:
            poker_game = query.first()
        serializer = PokerGamePublicSerializer(poker_game)
        return Response(serializer.data)

    def delete(self, request, game_id) -> Response:
        if not game_id:
            raise Http404()
        poker_game = get_object_or_404(PokerGame.objects.filter(id=int(game_id)))
        poker_game.delete()
        return Response()


class UserListView(views.APIView):
    def get(self, request) -> Response:
        serializer = UserSerializer(User.objects.all(), many=True)
        return Response(serializer.data)


class UserOffView(views.APIView):
    def post(self, request, user_id) -> Response:
        user: User = get_object_or_404(User.objects.filter(id=int(user_id)))
        user.online = not user.online
        user.save()
        serializer = UserInGamePublicSerializer(user.useringame_set, many=True)
        return Response(serializer.data)


class UserBotView(views.APIView):
    def post(self, request, user_id) -> Response:
        user: User = get_object_or_404(User.objects.filter(id=int(user_id)))
        user.bot = not user.bot
        user.save()
        serializer = UserInGamePublicSerializer(user.useringame_set, many=True)
        return Response(serializer.data)


class UserView(views.APIView):
    def get(self, request, user_id) -> Response:
        user = get_object_or_404(User.objects.filter(id=int(user_id)))
        serializer = UserInGamePublicSerializer(user.useringame_set, many=True)
        return Response(serializer.data)

    def put(self, request, user_id) -> Response:
        query = User.objects.filter(id=int(user_id))
        if not query:
            print(f'User {user_id} not found. create a new one')
            user = User.create(user_id)
        else:
            user = query.first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def delete(self, request, user_id) -> Response:
        if not user_id:
            raise Http404()
        user = get_object_or_404(User.objects.filter(id=int(user_id)))
        user.delete()
        return Response()


class UserInGameView(views.APIView):

    def get(self, request, game_id, user_id) -> Response:
        if not game_id:
            raise Http404()
        poker_game: PokerGame = get_object_or_404(PokerGame.objects.filter(id=int(game_id)))
        user_in_game = get_object_or_404(poker_game.useringame_set.filter(user__id=user_id))
        user_in_game.score = ScoreCalculator(user_in_game.hand.card_list.only(), user_in_game.hand.card_list.only()).get_score()
        user_in_game.save()
        return Response(UserInGamePrivateSerializer(user_in_game).data)

    def put(self, request, game_id, user_id) -> Response:
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

    def delete(self, request, game_id, user_id) -> Response:
        if not game_id or not user_id:
            raise Http404()
        poker_game: PokerGame = get_object_or_404(PokerGame.objects.filter(id=int(game_id)))
        user_in_game = get_object_or_404(poker_game.useringame_set.filter(user__id=user_id))
        user_in_game.delete()
        return Response()


class UserActionView(views.APIView):

    def post(self, request, game_id, user_id) -> Response:
        if not game_id or not user_id:
            raise Http404()

        try:
            action = request.data['action']
        except KeyError:
            return send_detail_response(message=f"Missing parameter 'action'. Values : {PokerUserActionType.values()}", status=400)

        try:
            bet = request.data['bet']
        except KeyError:
            bet = 0

        if not bet:
            bet = 0

        if action not in PokerUserActionType.values():
            return send_detail_response(message=f"Invalid parameter 'action'. Values : {PokerUserActionType.values()}", status=400)
        if action == PokerUserActionType.RAISE and bet <= 0:
            return send_detail_response(message=f"Invalid parameter 'bet' with RAISE, must be positive", status=400)

        poker_game: PokerGame = get_object_or_404(PokerGame.objects.filter(id=game_id))
        user_in_game: UserInGame = get_object_or_404(poker_game.useringame_set.filter(id=user_id))
        if user_in_game.user.bot:
            return send_detail_response(message=f"You can't play for a bot", status=403)
        return PokerEngine.process_user_action(poker_game, user_in_game, action, bet)


class GameStartView(views.APIView):
    def put(self, request, game_id) -> Response:
        if not game_id:
            raise Http404()
        return PokerEngine.start_game(game_id)


class GameRestartView(views.APIView):
    def put(self, request, game_id)->Response:
        if not game_id:
            raise Http404()
        return PokerEngine.restart_game(game_id)


class TestView(views.APIView):

    def post(self, request) -> Response:
        print(request.data)
        print(request.data['action'])
        if request.data['action'] == PokerUserActionType.CHECK:
            print("CHECK")
        print(request.data['bet'])
        return Response(request.data)
