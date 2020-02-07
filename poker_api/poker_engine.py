from django.shortcuts import get_object_or_404

from .bot_engine import BotEngine
from .models import *
from .utils import *


class PokerEngine:

    @staticmethod
    def process_user_action(game_id: int, user_id: int, action, bet) -> Response:
        poker_game: PokerGame = get_object_or_404(PokerGame.objects.filter(id=game_id))
        if poker_game.processing:
            return send_detail_response(message=f'Game is occupied, retry later', status=403)

        if poker_game.state in [PokerGame.FINISH, PokerGame.STOPPED]:
            return send_detail_response(message=f'Game is not in a correcte state : {poker_game.state}', status=403)

        user_in_game: UserInGame = get_object_or_404(poker_game.useringame_set.filter(id=user_id))
        if not user_in_game.in_game:
            return send_detail_response(message=f'You are not in current game', status=403)
        if not user_in_game.is_turn:
            return send_detail_response(message=f'Is not your turn.', status=403)
        try:
            poker_game.processing = True
            poker_game.save()
            if action == PokerUserActionType.FOLD:
                user_in_game.in_game = False
                user_in_game.save()
            elif action == PokerUserActionType.RAISE:
                if user_in_game.user.money < bet:
                    return send_detail_response(message=f'You cannot raise more than you have (max : {user_in_game.user.money}).', status=403)
                user_in_game.bet += bet
                user_in_game.user.money -= bet
                user_in_game.save()
            elif action != PokerUserActionType.CALL:
                return send_detail_response(message=f'Untraited action.', status=403)
            PokerEngine.__pass_next_action(poker_game)
            return send_detail_response(message=f'Ok', status=200)
        finally:
            poker_game.processing = False
            poker_game.save()

    @staticmethod
    def start_game(game_id: int) -> Response:
        poker_game: PokerGame = get_object_or_404(PokerGame.objects.filter(id=game_id))
        if poker_game.processing:
            return send_detail_response(message=f'Game is occupied, retry later', status=403)

        if poker_game.state not in [PokerGame.FINISH, PokerGame.STOPPED]:
            return send_detail_response(message=f'Game is not in a correcte state : {poker_game.state}', status=403)

        try:
            poker_game.processing = True
            poker_game.save()
            PokerEngine.__pass_next_step(poker_game)
            return send_detail_response(message=f'Ok', status=200)
        finally:
            poker_game.processing = False
            poker_game.save()

    @staticmethod
    def __pass_next_action(game: PokerGame):
        next_player = PokerEngine.__user_can_action(game)
        if next_player:
            PokerEngine.__set_next_player(game, next_player.id)
            if next_player.user.bot:
                PokerEngine.__call_bot_action(game, next_player)
        else:
            PokerEngine.__pass_next_step(game)

    @staticmethod
    def __user_can_action(game: PokerGame) -> UserInGame:
        active_user_list = game.useringame_set.filter(in_game=True).order_by('id')
        if len(list(active_user_list)) <= 1:
            pass
        max_bet = active_user_list.order_by('-bet').first().bet
        user_that_can_make_action = active_user_list.filter(bet__lt=max_bet, user__money__lte=0)
        if len(list(user_that_can_make_action)) > 0:
            # No more player can raise
            return PokerEngine.__find_next_player(game)
        elif game.state == PokerGame.PRE_FLOP:
            # in preflop big deal player can raise even if he already has the same bet of the pot
            return PokerEngine.__find_next_player(game)

    @staticmethod
    def __find_next_player(game: PokerGame) -> UserInGame:
        active_user_list = list(game.useringame_set.filter(in_game=True).order_by('id'))
        for i in range(0, len(active_user_list) - 1):
            if active_user_list[i].is_turn:
                index = i
                break
        if not index:
            # if no player play, it's time to select first player
            return PokerEngine.__find_first_player(game)
        for i in range(1, len(active_user_list)):
            user_in_game = active_user_list[(index + i) % len(active_user_list)]
            if user_in_game.user.money > 0:
                return user_in_game
        return active_user_list[index % len(active_user_list)]

    @staticmethod
    def __find_first_player(game: PokerGame) -> UserInGame:
        user_list = list(game.useringame_set.all())
        for i in range(0, len(user_list) - 1):
            if user_list[i].is_dealer:
                index = i
                break
        if not index:
            raise Exception("No dealer define")
        if game.state == PokerGame.PRE_FLOP:
            index += 2
        for i in range(1, len(user_list)):
            user_in_game = user_list[(index + i) % len(user_list)]
            if user_in_game.in_game and user_in_game.user.money > 0:
                return user_in_game
        raise Exception("No first user found")

    @staticmethod
    def __pass_next_step(game: PokerGame):
        if game.state == PokerGame.STOPPED or game.state == PokerGame.FINISH:
            PokerEngine.__start(game)
        elif game.state == PokerGame.PRE_FLOP:
            PokerEngine.__flop(game)
        elif game.state == PokerGame.FLOP:
            PokerEngine.__turn(game)
        elif game.state == PokerGame.TURN:
            PokerEngine.__river(game)
        elif game.state == PokerGame.RIVER:
            PokerEngine.__finish(game)

    @staticmethod
    def __start(game: PokerGame):
        PokerEngine.__set_next_player(game, None)
        game.state = PokerGame.PRE_FLOP
        game.board = Board.create()
        for card in game.pack.cardinpack_set:
            card.is_draw = False
            card.save()
        game.game_round += 1
        if game.game_round % 5 == 0:
            game.blind *= 2
        PokerEngine.__draw_pre_flop(game)
        PokerEngine.__init_player(game)
        game.save()

    @staticmethod
    def __flop(game: PokerGame):
        PokerEngine.__set_next_player(game, None)
        game.state = PokerGame.FLOP
        PokerEngine.__draw_flop(game)
        PokerEngine.__set_next_player(game, PokerEngine.__find_first_player(game).id)
        game.save()

    @staticmethod
    def __turn(game: PokerGame):
        PokerEngine.__set_next_player(game, None)
        game.state = PokerGame.TURN
        PokerEngine.__draw_turn(game)
        PokerEngine.__set_next_player(game, PokerEngine.__find_first_player(game).id)
        game.save()

    @staticmethod
    def __river(game: PokerGame):
        PokerEngine.__set_next_player(game, None)
        game.state = PokerGame.RIVER
        PokerEngine.__draw_river(game)
        PokerEngine.__set_next_player(game, PokerEngine.__find_first_player(game).id)
        game.save()

    @staticmethod
    def __finish(game: PokerGame):
        PokerEngine.__set_next_player(game, None)
        game.state = PokerGame.FINISH
        # TODO define winner
        # TODO divise money
        game.save()

    @staticmethod
    def __draw_pre_flop(game: PokerGame):
        # TODO start with dealer+1
        for user_in_game in game.useringame_set.filter(in_game=True):
            user_in_game.hand.card_list.add(game.pack.pick_card())
            user_in_game.hand.save()
        for user_in_game in game.useringame_set.filter(in_game=True):
            user_in_game.hand.card_list.add(game.pack.pick_card())
            user_in_game.hand.save()

    @staticmethod
    def __draw_flop(game: PokerGame):
        for i in range(0, 2):
            game.board.card_list.add(game.pack.pick_card())
            game.board.save()

    @staticmethod
    def __draw_turn(game: PokerGame):
        game.board.card_list.add(game.pack.pick_card())
        game.board.save()

    @staticmethod
    def __draw_river(game: PokerGame):
        game.board.card_list.add(game.pack.pick_card())
        game.board.save()

    @staticmethod
    def __set_next_player(game: PokerGame, next_user_in_game_id: int):
        for user_in_game in game.useringame_set.values():
            if next_user_in_game_id and user_in_game.id == next_user_in_game_id:
                user_in_game['is_turn'] = True
            else:
                user_in_game['is_turn'] = False
            user_in_game.save()

    @staticmethod
    def __init_player(game: PokerGame):
        user_list = game.useringame_set.values()
        for i in range(0, len(user_list) - 1):
            if user_list[i].is_dealer:
                dealer = i + 1
            user_list[i].is_turn = False
            user_list[i].bet = 0
            user_list[i].hand = Hand.create()
            user_list[i].is_dealer = False
            if user_list[i].user.money > 0:
                user_list[i].in_game = True
            else:
                user_list[i].in_game = False
            user_list[i].save()
        if len(game.useringame_set.filter(in_game=True)) <= 1:
            raise Exception("No enough player")
        if not dealer:
            dealer = 0
        # set new dealer
        for i in range(0, len(user_list) - 1):
            user_in_game = user_list[(i + dealer) % len(user_list)]
            if user_in_game.in_game:
                user_in_game.is_dealer = True
                user_in_game.save()
                dealer = (i + dealer)
                break
        # set small blind
        for i in range(1, len(user_list)):
            user_in_game = user_list[(i + dealer) % len(user_list)]
            if user_in_game.in_game > 0:
                user_in_game.bet = min(game.blind, user_in_game.user.money)
                user_in_game.user.money -= user_in_game.bet
                user_in_game.user.save()
                user_in_game.save()
                break
        # set big blind
        for i in range(2, len(user_list) + 1):
            user_in_game = user_list[(i + dealer) % len(user_list)]
            if user_in_game.in_game:
                user_in_game.bet = min(game.blind * 2, user_in_game.user.money)
                user_in_game.user.money -= user_in_game.bet
                user_in_game.user.save()
                user_in_game.save()
                break

    @staticmethod
    def __call_bot_action(game: PokerGame, bot: UserInGame):
        BotEngine.call_bot_action(game, bot)
