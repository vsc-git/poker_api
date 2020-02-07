from .models import *


class BasicBotEngine:

    @staticmethod
    def call_bot_action(game: PokerGame, bot: UserInGame):
        if not bot.user.bot:
            raise Exception('Not a bot player')
        if not bot.is_turn:
            raise Exception('Not bot turn')
        if game.state not in [PokerGame.PRE_FLOP, PokerGame.FLOP, PokerGame.TURN, PokerGame.RIVER]:
            raise Exception(f'Game is not in correct start {game.state}')
        BasicBotEngine.__bot_make_choice()


    @staticmethod
    def __bot_make_choice(game: PokerGame, bot: UserInGame, current: int):
        bot_choice = self.bot_choice(game)
        if self.__action == PokerGame.RAISE:
            self.raise_time += 1
        else:
            self.raise_time = 0
        if bot_choice > 0 and self.raise_time < 5:
            self.bot_raise(current, game.get_blind())
        elif bot_choice < 0:
            if current - self.__bet <= 0:
                self.__action = poker_enum.PokerActionType.CALL
                print(f'Bot action : CALL')
            else:
                self.__action = poker_enum.PokerActionType.FOLD
                print(f'Bot action : FOLD')
        else:
            diff = current - self.__bet
            self.__bet += min(diff, self.__money)
            self.__money -= min(diff, self.__money)
            if self.__money == 0:
                self.__action = poker_enum.PokerActionType.ALL_IN
                print(f'Bot action : ALL_IN')
            else:
                self.__action = poker_enum.PokerActionType.CALL
                print(f'Bot action : CALL')

    @staticmethod
    def __bot_raise(self, current: int, blind: int):
        diff = current - self.__bet
        # RAISE
        if diff + blind >= self.__money:
            self.__bet += self.__money
            self.__money = 0
            self.__action = poker_enum.PokerActionType.ALL_IN
            print(f'Bot action : ALL_IN')
        else:
            self.__bet += diff + blind
            self.__money -= diff + blind
            self.__action = poker_enum.PokerActionType.RAISE
            print(f'Bot action : RAISE')

    @staticmethod
    def __bot_choice(game: poker_game) -> int:
        """
        check if bot need to raise or not
        :param current: current bet
        :param game: game
        :return: positif if need to raise, 0 to call or check, negatif for fold
        """
        if game.get_state() == poker_enum.PokerGameState.PRE_FLOP:
            return self.bot_choice_pre_flop()
        elif game.get_state() == poker_enum.PokerGameState.FLOP:
            return self.bot_choice_flop(game)
        elif game.get_state() == poker_enum.PokerGameState.TURN:
            return self.bot_choice_turn(game)
        elif game.get_state() == poker_enum.PokerGameState.RIVER:
            return self.bot_choice_river(game)
        raise Exception('Not a good state')

    @staticmethod
    def __bot_choice_pre_flop(self) -> int:
        """
        check if bot need to raise or not
        :param current: current bet
        :param game: game
        :return: positif if need to raise, 0 to call or check, negatif for fold
        """
        c1 = self.__user_hand.get_cards()[0]
        c2 = self.__user_hand.get_cards()[1]
        color = c1.get_color() == c2.get_color()
        pair = c1.get_value() == c2.get_value()
        diff = abs(c1.get_value() - c2.get_value())
        suite = diff == 1
        if (pair and c1.get_value() >= 10) or (suite and c1.get_value() >= 10 and c2.get_value() >= 10) or (
                color and c1.get_value() >= 10 and c2.get_value() >= 10) or (suite and color and c1.get_value() >= 5):
            return 2
        elif (pair and c1.get_value() > 5) or (suite and color) or (color and (c1.get_value() >= 10 or c2.get_value() >= 10)) or (color and diff <= 5) or (
                diff <= 5 and (c1.get_value() >= 10 or c2.get_value() >= 10)):
            return 1
        elif diff <= 5 or suite or color or pair:
            return 0
        return -1

    @staticmethod
    def __bot_choice_flop(self, game: poker_game) -> int:
        """
        check if bot need to raise or not
        :param current: current bet
        :param game: game
        :return: positif if need to raise, 0 to call or check, negatif for fold
        """
        current_score = score_calculator.ScoreCalculator(self.get_hand(), game.get_board()).get_score()
        cards = []
        cards.extend(self.get_hand().get_cards())
        cards.extend(game.get_board().get_cards())
        straight_lenght = self.straight_lenght(cards)
        flush_lenght = self.flush_lenght(cards)
        if current_score.get_hand() >= poker_enum.PokerHandType.TWO_PAIRS or straight_lenght > 4 or flush_lenght > 4:
            return 1
        elif current_score.get_hand() >= poker_enum.PokerHandType.PAIR or straight_lenght > 3 or flush_lenght > 3:
            return 0
        return -1

    @staticmethod
    def __bot_choice_turn(self, game: poker_game) -> int:
        """
        check if bot need to raise or not
        :param current: current bet
        :param game: game
        :return: positif if need to raise, 0 to call or check, negatif for fold
        """
        current_score = score_calculator.ScoreCalculator(self.get_hand(), game.get_board()).get_score()
        cards = []
        cards.extend(self.get_hand().get_cards())
        cards.extend(game.get_board().get_cards())
        straight_lenght = self.straight_lenght(cards)
        flush_lenght = self.flush_lenght(cards)
        if current_score.get_hand() >= poker_enum.PokerHandType.TWO_PAIRS or straight_lenght > 4 or flush_lenght > 4:
            return 1
        elif current_score.get_hand() >= poker_enum.PokerHandType.PAIR or straight_lenght > 3 or flush_lenght > 3:
            return 0
        return -1

    @staticmethod
    def __bot_choice_river(self, game: poker_game) -> int:
        """
        check if bot need to raise or not
        :param current: current bet
        :param game: game
        :return: positif if need to raise, 0 to call or check, negatif for fold
        """
        current_score = score_calculator.ScoreCalculator(self.get_hand(), game.get_board()).get_score()
        if current_score.get_hand() >= poker_enum.PokerHandType.THREE_OF_A_KIND:
            return 1
        elif current_score.get_hand() >= poker_enum.PokerHandType.PAIR:
            return 0
        return -1

    @staticmethod
    def __flush_lenght(self, cards):
        res = self.__group_card(cards)[1]
        maxi = 0
        for k, v in res.items():
            maxi = max(v, maxi)
        return maxi

    @staticmethod
    def __group_card(self, cards=None):
        res_val = dict()
        res_col = dict()
        for c in cards:
            if c.get_value() not in res_val:
                res_val.setdefault(c.get_value(), 1)
            else:
                res_val[c.get_value()] += 1
            if c.get_color() not in res_col:
                res_col.setdefault(c.get_color(), 1)
            else:
                res_col[c.get_color()] += 1
        return (res_val, res_col)

    @staticmethod
    def __straight_lenght(self, cards):
        cards = sorted(cards, key=card.Card.get_value)
        last_value = None
        groups = []
        current_group = []
        count = 0
        # manage case where straight start with ace
        aces = {a for a in cards if a.get_value() is poker_enum.PokerCardValueType.ACE}
        for a in aces:
            if len(current_group) == 0:
                last_value = 1
                count = 1
            current_group.append(a)
        for c in cards:
            if last_value == None:
                current_group.append(c)
                last_value = c.get_value().value
                count = 1
                last_value = c.get_value().value
            if c.get_value().value == last_value:
                current_group.append(c)
                last_value = c.get_value().value
            elif c.get_value().value == last_value + 1:
                current_group.append(c)
                count += 1
                last_value = c.get_value().value
            else:
                groups.append((current_group, count))
                current_group = []
                current_group.append(c)
                count = 1
                last_value = c.get_value().value
        # add last card
        groups.append((current_group, count))
        maxi = 0
        for k, v in groups:
            maxi = max(v, maxi)
        return maxi