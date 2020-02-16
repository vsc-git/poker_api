import random
from enum import IntEnum
from typing import List

from django.core.validators import MinValueValidator
from django.db import models


class PokerUserActionType:
    CHECK = 'CHECK'
    CALL = 'CALL'
    RAISE = 'RAISE'
    FOLD = 'FOLD'
    ALL_IN = 'ALL_IN'

    @staticmethod
    def values() -> []:
        return [PokerUserActionType.CALL, PokerUserActionType.RAISE, PokerUserActionType.FOLD]


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

    def pick_card(self) -> Card:
        card_list = self.cardinpack_set.filter(is_draw=False)
        if not len(card_list):
            raise Exception("No more card")
        card_in_pack = random.choice(card_list)
        card_in_pack.is_draw = True
        card_in_pack.save()
        return card_in_pack.card

    def reset_pack(self):
        for card in self.cardinpack_set.only():
            card.is_draw = False
            card.save()
        self.save()

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
    bot = models.BooleanField(default=False)

    @classmethod
    def create(cls, id):
        obj = cls(id=id, money=500)
        obj.save()
        obj.name = obj.pk
        obj.save()
        return obj


class PokerGame(models.Model):
    STOPPED = 0
    PRE_FLOP = 2
    FLOP = 3
    TURN = 4
    RIVER = 5
    FINISH = 6
    POKER_GAME_STATE = [
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
    processing = models.BooleanField(default=False)
    game_round = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    def add_user(self, user: User) -> 'UserInGame':
        user_in_game = UserInGame.create(user=user, game=self)
        self.useringame_set.add(user_in_game)
        self.save()
        return user_in_game

    @classmethod
    def create(cls, id):
        obj = cls(id=id, pack=Pack.create(), board=Board.create(), blind=10)
        obj.save()
        return obj


class UserInGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    game = models.ForeignKey(PokerGame, on_delete=models.CASCADE)
    hand = models.ForeignKey(Hand, on_delete=models.PROTECT)
    bet = models.FloatField(default=0)
    in_game = models.BooleanField(default=False)
    is_dealer = models.BooleanField(default=False)
    is_turn = models.BooleanField(default=False)
    has_speak = models.BooleanField(default=False)
    score = models.OneToOneField('Score', on_delete=models.PROTECT, null=True, blank=True)

    @classmethod
    def create(cls, user: User, game: PokerGame):
        obj = cls(user=user, game=game, hand=Hand.create())
        obj.save()
        return obj


class Score(models.Model):
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
    POKER_SCORE = [
        (FOLD, 'FOLD'),
        (HIGH_CARD, 'HIGH_CARD'),
        (PAIR, 'PAIR'),
        (TWO_PAIRS, 'TWO_PAIRS'),
        (THREE_OF_A_KIND, 'THREE_OF_A_KIND'),
        (STRAIGHT, 'STRAIGHT'),
        (FLUSH, 'FLUSH'),
        (FULL_HOUSE, 'FULL_HOUSE'),
        (FOUR_OF_A_KIND, 'FOUR_OF_A_KIND'),
        (STRAIGHT_FLUSH, 'STRAIGHT_FLUSH'),
        (ROYAL_FLUSH, 'ROYAL_FLUSH')
    ]
    value = models.IntegerField(choices=POKER_SCORE)
    # pack of card liked to the hand list of list of card
    trick = models.ManyToManyField(Hand, blank=True)
    # other cards no evaluate
    other = models.ManyToManyField(Card, blank=True)

    @classmethod
    def create(cls, value: int, trick: List[List[Card]], other: List[Card]):
        obj = cls(value=value)
        obj.save()
        for card_list in trick:
            if len(card_list) > 0:
                hand = Hand.create()
                for card in card_list:
                    hand.card_list.add(card)
                obj.trick.add(hand)
        card_list = sorted(other, key=lambda ca: ca.value, reverse=True)
        for card in card_list:
            obj.other.add(card)
        obj.save()
        return obj

    def compare_to(self, other_score) -> int:
        if self.value is other_score.hand:
            return self.compare_trick(other_score)
        return self.value - other_score.hand

    def compare_trick(self, other_score) -> int:
        if self.value is Score.FOLD:
            return 0
        elif self.value is Score.ROYAL_FLUSH:
            return 0
        elif self.value is Score.STRAIGHT_FLUSH:
            return self.compare_straight_flush(other_score)
        elif self.value is Score.FOUR_OF_A_KIND:
            return self.compare_four_of_a_kind(other_score)
        elif self.value is Score.FULL_HOUSE:
            return self.compare_full_house(other_score)
        elif self.value is Score.FLUSH:
            return self.compare_flush(other_score)
        elif self.value is Score.STRAIGHT:
            return self.compare_straight(other_score)
        elif self.value is Score.THREE_OF_A_KIND:
            return self.compare_three_of_a_kind(other_score)
        elif self.value is Score.TWO_PAIRS:
            return self.compare_two_pair(other_score)
        elif self.value is Score.PAIR:
            return self.compare_pair(other_score)
        else:
            return self.compare_other(other_score)

    def compare_other(self, other_score) -> int:
        for i in range(0, len(self.other)):
            c1 = self.other[i]
            c2 = other_score.other[i]
            if c1.value == c2.value:
                continue
            elif c1.value > c2.value:
                return 1
            else:
                return -1
        return 0

    @staticmethod
    def compare_card(c1: Card, c2: Card) -> int:
        if c1.value == c2.value:
            return 0
        elif c1.value > c2.value:
            return 1
        else:
            return -1

    def compare_straight_flush(self, other_score) -> int:
        card1 = self.get_high_card_for_straight()
        card2 = other_score.get_high_card_for_straight()
        return Score.compare_card(card1, card2)

    def compare_four_of_a_kind(self, other_score) -> int:
        return Score.compare_card(self.trick.only()[0].card_list.only()[0], other_score.trick[0][0])

    def compare_full_house(self, other_score) -> int:
        r1 = Score.compare_card(self.trick.only()[0].card_list.only()[0], other_score.trick[0][0])
        if r1 == 0:
            return Score.compare_card(self.trick.only()[0].card_list.only()[0], other_score.trick[0][0])
        else:
            return r1

    def compare_flush(self, other_score) -> int:
        cards1 = sorted(self.trick.only()[0].card_list.only(), key=lambda card: card.value, reverse=True)
        cards2 = sorted(other_score.trick[0], key=lambda card: card.value, reverse=True)
        for i in range(0, len(cards1)):
            c1 = cards1[i]
            c2 = cards2[i]
            if c1.value == c2.value:
                continue
            elif c1.value > c2.value:
                return 1
            else:
                return -1
        return 0

    def compare_straight(self, other_score) -> int:
        card1 = self.get_high_card_for_straight()
        card2 = other_score.get_high_card_for_straight()
        return Score.compare_card(card1, card2)

    def compare_three_of_a_kind(self, other_score) -> int:
        r1 = Score.compare_card(self.trick.only()[0].card_list.only()[0], other_score.trick[0][0])
        if r1 == 0:
            return self.compare_other(other_score)
        else:
            return r1

    def compare_two_pair(self, other_score) -> int:
        if self.trick.only()[0].card_list.only()[0].value > self.trick.only()[1].card_list.only()[0].value:
            pair1a = self.trick.only()[0].card_list.only()
            pair2a = self.trick.only()[1].card_list.only()
        else:
            pair1a = self.trick.only()[1].card_list.only()
            pair2a = self.trick.only()[0].card_list.only()
        if other_score.trick[0][0].value > other_score.trick[1][0].value:
            pair1b = other_score.trick[0]
            pair2b = other_score.trick[1]
        else:
            pair1b = other_score.trick[1]
            pair2b = other_score.trick[0]
        r1 = Score.compare_card(pair1a[0], pair1b[0])
        if r1 == 0:
            r2 = Score.compare_card(pair2a[0], pair2b[0])
            if r2 == 0:
                return self.compare_other(other_score)
            else:
                return r2
        else:
            return r1

    def compare_pair(self, other_score) -> int:
        r1 = Score.compare_card(self.trick.only()[0].card_list.only()[0], other_score.trick[0][0])
        if r1 == 0:
            return self.compare_other(other_score)
        else:
            return r1

    def get_high_card_for_straight(self) -> Card:
        sorted_cards = sorted(self.trick.only()[0].card_list.only(), key=lambda card: card.value, reverse=True)
        if sorted_cards[0].value is Card.ACE:
            if sorted_cards[1].value is Card.KING:
                return sorted_cards[0]
            else:
                return sorted_cards[1]
        return sorted_cards[0]

    def __str__(self):
        if self.value is Score.ROYAL_FLUSH:
            return "Royal flush of " + list(filter(lambda dict: dict[0] == self.trick.only()[0].card_list.only()[0].color, Card.POKER_CARD_COLOR))[0][1]
        elif self.value is Score.STRAIGHT_FLUSH:
            high_card = self.get_high_card_for_straight()
            return "Straight flush at " + str(high_card)
        elif self.value is Score.FOUR_OF_A_KIND:
            return "Four of a kind of " + list(filter(lambda dict: dict[0] == self.trick.only()[0].card_list.only()[0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.value is Score.FULL_HOUSE:
            return "Full house of " + list(filter(lambda dict: dict[0] == self.trick.only()[0].card_list.only()[0].value, Card.POKER_CARD_VALUE))[0][1] + " by " + \
                   list(filter(lambda dict: dict[0] == self.trick.only()[1].card_list.only()[0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.value is Score.FLUSH:
            cards = sorted(self.trick.only()[0].card_list.only(), key=lambda card: card.value, reverse=True)
            return "Flush at " + str(cards[0])
        elif self.value is Score.STRAIGHT:
            high_card = self.get_high_card_for_straight()
            return "Straight at " + list(filter(lambda dict: dict[0] == high_card.value, Card.POKER_CARD_VALUE))[0][1]
        elif self.value is Score.THREE_OF_A_KIND:
            return "Three of a kind of " + list(filter(lambda dict: dict[0] == self.trick.only()[0].card_list.only()[0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.value is Score.TWO_PAIRS:
            return "Two pairs of " + list(filter(lambda dict: dict[0] == self.trick.only()[0].card_list.only()[0].value, Card.POKER_CARD_VALUE))[0][1] + " and " + \
                   list(filter(lambda dict: dict[0] == self.trick.only()[1].card_list.only()[0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.value is Score.PAIR:
            return "Pair of " + list(filter(lambda dict: dict[0] == self.trick.only()[0].card_list.only()[0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.value is Score.FOLD:
            return "Fold"
        else:
            cards = sorted(self.other.only(), key=lambda card: card.value, reverse=True)
            return "Highcard of " + list(filter(lambda dict: dict[0] == cards[0].value, Card.POKER_CARD_VALUE))[0][1]

    def __lt__(self, other_score):
        res = self.compare_to(other_score)
        if res < 0:
            return True
        return False

    def __le__(self, other_score):
        res = self.compare_to(other_score)
        if res <= 0:
            return True
        return False

    def __gt__(self, other_score):
        res = self.compare_to(other_score)
        if res > 0:
            return True
        return False

    def __ge__(self, other_score):
        res = self.compare_to(other_score)
        if res >= 0:
            return True
        return False

    def __eq__(self, other_score):
        res = self.compare_to(other_score)
        if res == 0:
            return True
        return False
