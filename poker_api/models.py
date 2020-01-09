from enum import IntEnum

from django.core.validators import MinValueValidator
from django.db import models


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


class Card(models.Model):
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
    POKER_CARD_VALUE = [
        (TWO, '2'),
        (THREE, '3'),
        (FOUR, '4'),
        (FIVE, '5'),
        (SIX, '6'),
        (SEVEN, '7'),
        (HEIGHT, '8'),
        (NINE, '9'),
        (TEN, '10'),
        (JACK, 'Jack'),
        (QUEEN, 'Queen'),
        (KING, 'King'),
        (ACE, 'Ace')
    ]
    CLUBS = 0
    HEARTS = 1
    SPADES = 2
    DIAMONDS = 3
    POKER_CARD_COLOR = [
        (CLUBS, 'Clubs'),
        (HEARTS, 'Hearts'),
        (SPADES, 'Spades'),
        (DIAMONDS, 'Diamonds')
    ]

    color = models.IntegerField(choices=POKER_CARD_COLOR)
    value = models.IntegerField(choices=POKER_CARD_VALUE)

    def __str__(self) -> str:
        result = ''
        if self.value is self.TEN:
            result += 'J'
        elif self.value is self.JACK:
            result += 'J'
        elif self.value is self.QUEEN:
            result += 'Q'
        elif self.value is self.KING:
            result += 'K'
        elif self.value is self.ACE:
            result += '1'
        else:
            result += str(self.value)
        if self.color is self.CLUBS:
            result += '♣'
        elif self.color is self.DIAMONDS:
            result += '♢'
        elif self.color is self.HEARTS:
            result += '♡'
        else:
            result += '♠'
        return result


class Hand(models.Model):
    card_list = models.ManyToManyField(Card, blank=True)

    @classmethod
    def create(cls):
        obj = cls()
        obj.save()
        return obj


class Pack(models.Model):
    card_list = models.ManyToManyField(Card, through='CardInPack')

    # def pick_card(self)->Card:
    #     card = random.choice(self.cardinpack_set.filter(is_draw=False))
    #     card.

    @classmethod
    def create(cls):
        pack = cls()
        pack.save()
        [pack.cardinpack_set.create(card=card) for card in Card.objects.all()]
        pack.save()
        return pack


class CardInPack(models.Model):
    card = models.ForeignKey(Card, on_delete=models.PROTECT)
    pack = models.ForeignKey(Pack, on_delete=models.CASCADE)
    is_draw = models.BooleanField(default=False)


class Board(models.Model):
    card_list = models.ManyToManyField(Card, blank=True)

    @classmethod
    def create(cls):
        obj = cls()
        obj.save()
        return obj


class User(models.Model):
    name = models.TextField(max_length=100, unique=True)
    money = models.FloatField()
    online = models.BooleanField(default=True)

    @classmethod
    def create(cls, id):
        obj = cls(id=id, money=500)
        obj.save()
        obj.name = obj.pk
        obj.save()
        return obj


class PokerGame(models.Model):
    PROCESSING = -1
    STOPPED = 0
    PRE_FLOP = 2
    FLOP = 3
    TURN = 4
    RIVER = 5
    FINISH = 6
    POKER_GAME_STATE = [
        (PROCESSING, 'PROCESSING'),
        (STOPPED, 'STOPPED'),
        (PRE_FLOP, 'PRE_FLOP'),
        (FLOP, 'FLOP'),
        (TURN, 'TURN'),
        (RIVER, 'RIVER'),
        (FINISH, 'FINISH')
    ]
    user_list = models.ManyToManyField(User, through='UserInGame')
    pack = models.OneToOneField(Pack, on_delete=models.PROTECT, unique=True)
    board = models.OneToOneField(Board, on_delete=models.PROTECT, unique=True)
    pot = models.FloatField(default=0)
    blind = models.FloatField(default=0)
    state = models.IntegerField(choices=POKER_GAME_STATE, default=STOPPED)
    game_round = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    def add_user(self, user: User) -> 'UserInGame':
        user_in_game = UserInGame.create(user=user, game=self)
        self.useringame_set.add(user_in_game)
        self.save()
        return user_in_game

    @classmethod
    def create(cls, id):
        obj = cls(id=id, pack=Pack.create(), board=Board.create())
        obj.save()
        print(obj.user_list.count())
        return obj


class UserInGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    game = models.ForeignKey(PokerGame, on_delete=models.CASCADE)
    hand = models.ForeignKey(Hand, on_delete=models.PROTECT)
    bet = models.FloatField(default=0)
    in_game = models.BooleanField(default=False)
    is_dealer = models.BooleanField(default=False)
    is_turn = models.BooleanField(default=False)

    @classmethod
    def create(cls, user: User, game: PokerGame):
        obj = cls(user=user, game=game, hand=Hand.create())
        obj.save()
        return obj

# TODO keep score and history
