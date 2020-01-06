from enum import IntEnum

from django.db import models
from django.core.validators import MinValueValidator


class PokerActionType(IntEnum):
    CHECK = 0
    CALL = 1
    RAISE = 2
    FOLD = 3
    ALL_IN = 4


class PokerGameState(IntEnum):
    COMPULSORY_BETS = 0
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    SHOWDOWN = 5
    FINISH = 6


class PokerHandType(IntEnum):
    FOLD = 0
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIRS = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class PokerCardColorType(IntEnum):
    CLUBS = 0
    HEARTS = 1
    SPADES = 2
    DIAMONDS = 3


class PokerCardValueType(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    HEIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Card(models.Model):
    color: PokerCardColorType = models.IntegerField(choices=[(tag, tag.value) for tag in PokerCardColorType])
    value: PokerCardValueType = models.IntegerField(choices=[(tag, tag.value) for tag in PokerCardValueType])


class Hand(models.Model):
    cardList = models.ManyToManyField(Card, blank=True)


class Pack(models.Model):
    cardList = models.ManyToManyField(Card, through='CardInPack')


class CardInPack(models.Model):
    card = models.ForeignKey(Card,on_delete=models.PROTECT)
    pack = models.ForeignKey(Pack,on_delete=models.CASCADE)
    is_draw = models.BooleanField(default=False)


class Board(models.Model):
    cardList = models.ManyToManyField(Card, blank=True)


class User(models.Model):
    name = models.TextField(max_length=100, unique=True)
    money = models.FloatField()
    online = models.BooleanField(default=True)


class PokerGame(models.Model):
    userList = models.ManyToManyField(User, through='UserInGame')
    pack = models.OneToOneField(Pack, on_delete=models.PROTECT, unique=True)
    board = models.OneToOneField(Board, on_delete=models.PROTECT, unique=True)
    pot = models.FloatField(default=0)
    blind = models.FloatField(default=0)
    state: PokerGameState = models.IntegerField(choices=[(tag, tag.value) for tag in PokerGameState])
    game_round = models.IntegerField(validators=[MinValueValidator(0)], default=0)


class UserInGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    game = models.ForeignKey(PokerGame, on_delete=models.CASCADE)
    hand = models.ForeignKey(Hand, on_delete=models.PROTECT)
    bet = models.FloatField()
    in_game = models.BooleanField(default=False)
    is_dealer = models.BooleanField(default=False)
    is_turn = models.BooleanField(default=False)

#TODO keep score and history