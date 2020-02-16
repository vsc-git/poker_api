from django.shortcuts import get_object_or_404

from .models import *
from .score import ScoreCalculator
from .utils import *


class PokerEngine:

    @staticmethod
    def process_user_action(poker_game: PokerGame, user_in_game: UserInGame, action: PokerUserActionType, bet: float = 0) -> Response:
        if poker_game.state in [PokerGame.FINISH, PokerGame.STOPPED]:
            return send_detail_response(message=f'Game is not in a correcte state : {poker_game.state}', status=403)

        if not user_in_game.in_game:
            return send_detail_response(message=f'You are not in current game', status=403)
        if not user_in_game.is_turn:
            return send_detail_response(message=f'Is not your turn.', status=403)

        if poker_game.processing and not user_in_game.user.bot:
            return send_detail_response(message=f'Game is occupied, retry later', status=403)
        try:
            print(f'User {user_in_game.user.id} action : {action}')
            poker_game.processing = True
            poker_game.save()
            max_bet_user = poker_game.useringame_set.filter(in_game=True).order_by('-bet').first()
            max_bet = 0
            if max_bet_user:
                max_bet = max_bet_user.bet
            if action == PokerUserActionType.FOLD:
                user_in_game.in_game = False
                user_in_game.has_speak = True
                user_in_game.save()
            elif action == PokerUserActionType.RAISE:
                if user_in_game.user.money < bet:
                    return send_detail_response(
                        message=f'You cannot raise more than you have (max : {user_in_game.user.money}).', status=403)
                if user_in_game.bet + bet < max_bet and bet < user_in_game.user.money:
                    return send_detail_response(message=f'You have to bet at least : {min(max_bet - user_in_game.bet, user_in_game.user.money)}.', status=403)
                user_in_game.bet += bet
                user_in_game.user.money -= bet
                user_in_game.has_speak = True
                user_in_game.save()
            elif action == PokerUserActionType.CALL:
                if user_in_game.user.money > 0 and user_in_game.bet+bet < max_bet:
                    return send_detail_response(
                        message=f'Attended bet : {max_bet - user_in_game.bet}.', status=403)
                if user_in_game.bet+bet > max_bet:
                    return send_detail_response(
                        message=f'You bet to much,make a raise (attended : {max_bet-user_in_game.bet}).', status=403)
                if user_in_game.user.money < bet:
                    return send_detail_response(
                        message=f'You cannot bet more than you have (max : {user_in_game.user.money}).', status=403)
                if bet > 0 :
                    user_in_game.bet += bet
                    user_in_game.user.money -= bet
                user_in_game.has_speak = True
                user_in_game.save()
            else:
                return send_detail_response(message=f'Untraited action.', status=403)
            PokerEngine.__pass_next_action(poker_game)
            return send_detail_response(message=f'Ok', status=200)
        finally:
            # keep processing state when bot play
            poker_game.processing = False or user_in_game.user.bot
            poker_game.save()

    @staticmethod
    def restart_game(game_id: int) -> Response:
        poker_game: PokerGame = get_object_or_404(PokerGame.objects.filter(id=game_id))
        try:
            poker_game.state = PokerGame.STOPPED
            poker_game.processing = True
            poker_game.save()
            PokerEngine.__pass_next_step(poker_game)
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
            next_player = PokerEngine.__set_next_player(game, next_player.id)
            if next_player.user.bot:
                PokerEngine.__call_bot_action(game, next_player)
        else:
            PokerEngine.__pass_next_step(game)

    @staticmethod
    def __user_can_action(game: PokerGame) -> UserInGame:
        active_user_list = game.useringame_set.filter(in_game=True).order_by('id')
        if len(list(active_user_list)) <= 1:
            pass
        if len(list(active_user_list.filter(has_speak=False))) > 0:
            return PokerEngine.__find_next_player(game)
        max_bet = game.useringame_set.filter(in_game=True).order_by('-bet').first().bet
        user_that_can_make_action = active_user_list.filter(bet__lt=max_bet, user__money__lte=0)
        if len(list(user_that_can_make_action)) > 0:
            # one player has to pay the bet
            return PokerEngine.__find_next_player(game)
        # elif game.state == PokerGame.PRE_FLOP and max_bet <= game.blind:
        #     # in preflop big deal player can raise even if he already has the same bet of the pot
        #     return PokerEngine.__find_next_player_pre_flop(game)

    @staticmethod
    def __find_next_player(game: PokerGame) -> UserInGame:
        active_user_list = list(game.useringame_set.filter(in_game=True).order_by('id'))
        index = -1
        for i in range(0, len(active_user_list)):
            if active_user_list[i].is_turn:
                index = i
                break
        if index == -1:
            # if no player play, it's time to select first player
            return PokerEngine.__find_first_player(game)
        for i in range(1, len(active_user_list) + 1):
            user_in_game = active_user_list[(index + i) % len(active_user_list)]
            if user_in_game.user.money > 0:
                return user_in_game
        return active_user_list[index % len(active_user_list)]

    @staticmethod
    def __find_first_player(game: PokerGame) -> UserInGame:
        user_list = list(game.useringame_set.all())
        index = -1
        for i in range(0, len(user_list)):
            if user_list[i].is_dealer:
                index = i
                break
        if index == -1:
            raise Exception("No dealer define")
        if game.state == PokerGame.PRE_FLOP:
            index += 2
        for i in range(1, len(user_list) + 1):
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
        game.state = PokerGame.PRE_FLOP
        game.board.card_list.clear()
        game.board.save()
        game.pack.reset_pack()
        game.game_round += 1
        if game.game_round % 5 == 0:
            game.blind *= 2
        first_player = PokerEngine.__init_player(game)
        PokerEngine.__draw_pre_flop(game)
        game.save()
        if first_player.user.bot:
            PokerEngine.__call_bot_action(game, first_player)

    @staticmethod
    def __flop(game: PokerGame):
        game.state = PokerGame.FLOP
        PokerEngine.__draw_flop(game)
        PokerEngine.__reset_user_speak(game)
        next_player = PokerEngine.__set_next_player(game, PokerEngine.__find_first_player(game).id)
        game.save()
        if next_player.user.bot:
            PokerEngine.__call_bot_action(game, next_player)

    @staticmethod
    def __turn(game: PokerGame):
        game.state = PokerGame.TURN
        PokerEngine.__draw_turn(game)
        PokerEngine.__reset_user_speak(game)
        next_player = PokerEngine.__set_next_player(game, PokerEngine.__find_first_player(game).id)
        game.save()
        if next_player.user.bot:
            PokerEngine.__call_bot_action(game, next_player)

    @staticmethod
    def __river(game: PokerGame):
        game.state = PokerGame.RIVER
        PokerEngine.__draw_river(game)
        PokerEngine.__reset_user_speak(game)
        next_player = PokerEngine.__set_next_player(game, PokerEngine.__find_first_player(game).id)
        game.save()
        if next_player.user.bot:
            PokerEngine.__call_bot_action(game, next_player)

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
        for i in range(0, 3):
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
    def __set_next_player(game: PokerGame, next_user_in_game_id: int) -> UserInGame:
        player: UserInGame = None
        for user_in_game in game.useringame_set.only():
            if next_user_in_game_id and user_in_game.id == next_user_in_game_id:
                user_in_game.is_turn = True
                player = user_in_game
            else:
                user_in_game.is_turn = False
            user_in_game.save()
        return player

    @staticmethod
    def __reset_user_speak(game: PokerGame):
        for user_in_game in game.useringame_set.only():
            # TODO depends of money
            user_in_game.has_speak = False
            user_in_game.save()

    @staticmethod
    def __init_player(game: PokerGame) -> UserInGame:
        user_list = game.useringame_set.only()
        dealer = -1
        for i in range(0, len(user_list)):
            if user_list[i].is_dealer:
                dealer = i + 1
            user_list[i].is_turn = False
            user_list[i].has_speak = False
            user_list[i].bet = 0
            user_list[i].hand.card_list.clear()
            user_list[i].hand.save()
            user_list[i].is_dealer = False
            if user_list[i].user.money > 0:
                user_list[i].in_game = True
            else:
                user_list[i].in_game = False
            user_list[i].save()
        if len(game.useringame_set.filter(in_game=True)) <= 1:
            raise Exception("No enough player")
        if dealer == -1:
            dealer = 0
        # set new dealer
        for i in range(0, len(user_list)):
            user_in_game = user_list[(i + dealer) % len(user_list)]
            if user_in_game.in_game:
                user_in_game.is_dealer = True
                user_in_game.save()
                dealer = (i + dealer)
                break
        # set small blind
        for i in range(1, len(user_list) + 1):
            user_in_game = user_list[(i + dealer) % len(user_list)]
            if user_in_game.in_game > 0:
                user_in_game.bet = min(game.blind, user_in_game.user.money)
                user_in_game.user.money -= user_in_game.bet
                user_in_game.user.save()
                user_in_game.save()
                break
        # set big blind
        for i in range(2, len(user_list) + 2):
            user_in_game = user_list[(i + dealer) % len(user_list)]
            if user_in_game.in_game:
                user_in_game.bet = min(game.blind * 2, user_in_game.user.money)
                user_in_game.user.money -= user_in_game.bet
                user_in_game.user.save()
                user_in_game.save()
                break

        # set player turn
        player: UserInGame = None
        for i in range(3, len(user_list) + 3):
            user_in_game = user_list[(i + dealer) % len(user_list)]
            if user_in_game.in_game:
                user_in_game.is_turn = True
                user_in_game.save()
                player = user_in_game
                break
        return player

    @staticmethod
    def __call_bot_action(game: PokerGame, bot: UserInGame):
        BasicBotEngine.call_bot_action(game, bot)


class BasicBotEngine:

    @staticmethod
    def call_bot_action(game: PokerGame, bot: UserInGame):
        if not bot.user.bot:
            raise Exception('Not a bot player')
        if not bot.is_turn:
            raise Exception('Not bot turn')
        if game.state not in [PokerGame.PRE_FLOP, PokerGame.FLOP, PokerGame.TURN, PokerGame.RIVER]:
            raise Exception(f'Game is not in correct start {game.state}')
        BasicBotEngine.__bot_make_choice(game, bot)

    @staticmethod
    def __bot_make_choice(game: PokerGame, bot: UserInGame):
        bot_choice = BasicBotEngine.__bot_choice(game, bot)
        # TODO Add random for raise init in preflop and keep in other state
        # TODO add raise limit to avoid to loop with other bot
        bot_choice = 0
        max_bet = game.useringame_set.filter(in_game=True).order_by('id').order_by('-bet').first().bet
        if bot_choice > 0:  # and self.raise_time < 5:
            PokerEngine.process_user_action(game, bot, PokerUserActionType.RAISE, game.blind)
        elif bot_choice < 0:
            if max_bet == bot.bet:
                PokerEngine.process_user_action(game, bot, PokerUserActionType.CALL)
            else:
                PokerEngine.process_user_action(game, bot, PokerUserActionType.FOLD)
        else:
            diff = max_bet - bot.bet
            PokerEngine.process_user_action(game, bot, PokerUserActionType.RAISE, min(diff, bot.user.money))

    @staticmethod
    def __bot_choice(game: PokerGame, bot: UserInGame) -> int:
        """
        check if bot need to raise or not
        :param game: game
        :param bot: current user
        :return: positif if need to raise, 0 to call or check, negatif for fold
        """
        if game.state == PokerGame.PRE_FLOP:
            return BasicBotEngine.__bot_choice_pre_flop(game, bot)
        elif game.state == PokerGame.FLOP:
            return BasicBotEngine.__bot_choice_flop(game, bot)
        elif game.state == PokerGame.TURN:
            return BasicBotEngine.__bot_choice_turn(game, bot)
        elif game.state == PokerGame.RIVER:
            return BasicBotEngine.__bot_choice_river(game, bot)
        raise Exception('Not a good state')

    @staticmethod
    def __bot_choice_pre_flop(game: PokerGame, bot: UserInGame) -> int:
        """
        check if bot need to raise or not
        :param game: game
        :param bot: current user
        :return: positif if need to raise, 0 to call or check, negatif for fold
        """
        c1: Card = bot.hand.card_list.only()[0]
        c2: Card = bot.hand.card_list.only()[1]
        color = c1.color == c2.color
        pair = c1.value == c2.value
        diff = abs(c1.value - c2.value)
        suite = diff == 1
        if (pair and c1.value >= 10) or (suite and c1.value >= 10 and c2.value >= 10) or (
                color and c1.value >= 10 and c2.value >= 10) or (suite and color and c1.value >= 5):
            return 2
        elif (pair and c1.value > 5) or (suite and color) or (color and (c1.value >= 10 or c2.value >= 10)) or (color and diff <= 5) or (
                diff <= 5 and (c1.value >= 10 or c2.value >= 10)):
            return 1
        elif diff <= 5 or suite or color or pair:
            return 0
        return -1

    @staticmethod
    def __bot_choice_flop(game: PokerGame, bot: UserInGame) -> int:
        return BasicBotEngine.__bot_choice_turn(game, bot)

    @staticmethod
    def __bot_choice_turn(game: PokerGame, bot: UserInGame) -> int:
        """
        check if bot need to raise or not
        :param game: game
        :param bot: current user
        :return: positif if need to raise, 0 to call or check, negatif for fold
        """
        current_score = ScoreCalculator(bot.hand.card_list.only(), game.board.card_list.only()).get_score()
        cards = []
        cards.extend(bot.hand.card_list.only())
        cards.extend(game.board.card_list.only())
        straight_lenght = BasicBotEngine.__straight_lenght(cards)
        flush_lenght = BasicBotEngine.__flush_lenght(cards)
        if current_score.hand >= Score.TWO_PAIRS or straight_lenght > 4 or flush_lenght > 4:
            return 1
        elif current_score.hand >= Score.PAIR or straight_lenght > 3 or flush_lenght > 3:
            return 0
        return -1

    @staticmethod
    def __bot_choice_river(game: PokerGame, bot: UserInGame) -> int:
        """
        check if bot need to raise or not
        :param game: game
        :param bot: current user
        :return: positif if need to raise, 0 to call or check, negatif for fold
        """
        current_score = ScoreCalculator(bot.hand.card_list.only(), game.board.card_list.only()).get_score()
        if current_score.hand >= Score.THREE_OF_A_KIND:
            return 1
        elif current_score.hand >= Score.PAIR:
            return 0
        return -1

    @staticmethod
    def __flush_lenght(cards):
        res = BasicBotEngine.__group_card(cards)[1]
        maxi = 0
        for k, v in res.items():
            maxi = max(v, maxi)
        return maxi

    @staticmethod
    def __group_card(cards=None):
        res_val = dict()
        res_col = dict()
        for c in cards:
            if c.value not in res_val:
                res_val.setdefault(c.value, 1)
            else:
                res_val[c.value] += 1
            if c.color not in res_col:
                res_col.setdefault(c.color, 1)
            else:
                res_col[c.color] += 1
        return res_val, res_col

    @staticmethod
    def __straight_lenght(cards):
        cards = sorted(cards, key=lambda card: card.value)
        last_value = None
        groups = []
        current_group = []
        count = 0
        # manage case where straight start with ace
        aces = {a for a in cards if a.value is Card.ACE}
        for a in aces:
            if len(current_group) == 0:
                last_value = 1
                count = 1
            current_group.append(a)
        for c in cards:
            if last_value is None:
                current_group.append(c)
                last_value = c.value
                count = 1
                last_value = c.value
            if c.value == last_value:
                current_group.append(c)
                last_value = c.value
            elif c.value == last_value + 1:
                current_group.append(c)
                count += 1
                last_value = c.value
            else:
                groups.append((current_group, count))
                current_group = [c]
                count = 1
                last_value = c.value
        # add last card
        groups.append((current_group, count))
        maxi = 0
        for k, v in groups:
            maxi = max(v, maxi)
        return maxi
