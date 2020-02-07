from .models import *


class BotEngine:

    @staticmethod
    def call_bot_action(game: PokerGame, bot: UserInGame):
        if not bot.user.bot:
            raise Exception('Not a bot player')
        if not bot.is_turn:
            raise Exception('Not bot turn')
        if game.state not in [PokerGame.PRE_FLOP, PokerGame.FLOP, PokerGame.TURN, PokerGame.RIVER]:
            raise Exception(f'Game is not in correct start {game.state}')

