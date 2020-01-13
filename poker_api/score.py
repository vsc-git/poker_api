from typing import List

from .models import Card, ScoreType


class Score:
    hand: int
    trick: List[List[Card]]  # pack of card liked to the hand list of list of card
    other: List[Card]  # other cards no evaluate

    def __init__(self, hand: int, trick: List[List[Card]], other: List[Card]):
        self.hand = hand
        self.trick = trick
        if other is not None:
            self.other = sorted(other, key=Card.value, reverse=True)

    def compare_to(self, other_score) -> int:
        if self.hand is other_score.hand:
            return self.compare_trick(other_score)
        return self.hand - other_score.hand

    def compare_trick(self, other_score) -> int:
        if self.hand is ScoreType.FOLD:
            return 0
        elif self.hand is ScoreType.ROYAL_FLUSH:
            return 0
        elif self.hand is ScoreType.STRAIGHT_FLUSH:
            return self.compare_straight_flush(other_score)
        elif self.hand is ScoreType.FOUR_OF_A_KIND:
            return self.compare_four_of_a_kind(other_score)
        elif self.hand is ScoreType.FULL_HOUSE:
            return self.compare_full_house(other_score)
        elif self.hand is ScoreType.FLUSH:
            return self.compare_flush(other_score)
        elif self.hand is ScoreType.STRAIGHT:
            return self.compare_straight(other_score)
        elif self.hand is ScoreType.THREE_OF_A_KIND:
            return self.compare_three_of_a_kind(other_score)
        elif self.hand is ScoreType.TWO_PAIRS:
            return self.compare_two_pair(other_score)
        elif self.hand is ScoreType.PAIR:
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
        return Score.compare_card(self.trick[0][0], other_score.trick[0][0])

    def compare_full_house(self, other_score) -> int:
        r1 = Score.compare_card(self.trick[0][0], other_score.trick[0][0])
        if r1 == 0:
            return Score.compare_card(self.trick[0][0], other_score.trick[0][0])
        else:
            return r1

    def compare_flush(self, other_score) -> int:
        cards1 = sorted(self.trick[0], key=Card.value, reverse=True)
        cards2 = sorted(other_score.trick[0], key=Card.value, reverse=True)
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
        r1 = Score.compare_card(self.trick[0][0], other_score.trick[0][0])
        if r1 == 0:
            return self.compare_other(other_score)
        else:
            return r1

    def compare_two_pair(self, other_score) -> int:
        if self.trick[0][0].value > self.trick[1][0].value:
            pair1a = self.trick[0]
            pair2a = self.trick[1]
        else:
            pair1a = self.trick[1]
            pair2a = self.trick[0]
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
        r1 = Score.compare_card(self.trick[0][0], other_score.trick[0][0])
        if r1 == 0:
            return self.compare_other(other_score)
        else:
            return r1

    def get_high_card_for_straight(self) -> Card:
        sorted_cards = sorted(self.trick[0], key=Card.value, reverse=True)
        if sorted_cards[0].value is Card.ACE:
            if sorted_cards[1].value is Card.KING:
                return sorted_cards[0]
            else:
                return sorted_cards[1]
        return sorted_cards[0]

    def __str__(self):
        if self.hand is ScoreType.ROYAL_FLUSH:
            return "Royal flush of " + list(filter(lambda dict: dict[0] == self.trick[0][0].color, Card.POKER_CARD_COLOR))[0][1]
        elif self.hand is ScoreType.STRAIGHT_FLUSH:
            high_card = self.get_high_card_for_straight()
            return "Straight flush at " + str(high_card)
        elif self.hand is ScoreType.FOUR_OF_A_KIND:
            return "Four of a kind of " + list(filter(lambda dict: dict[0] == self.trick[0][0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.hand is ScoreType.FULL_HOUSE:
            return "Full house of " + list(filter(lambda dict: dict[0] == self.trick[0][0].value, Card.POKER_CARD_VALUE))[0][1] + " by " + list(filter(lambda dict: dict[0] == self.trick[1][0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.hand is ScoreType.FLUSH:
            cards = sorted(self.trick[0], key=Card.value, reverse=True)
            return "Flush at " + str(cards[0])
        elif self.hand is ScoreType.STRAIGHT:
            high_card = self.get_high_card_for_straight()
            return "Straight at " + list(filter(lambda dict: dict[0] == high_card.value, Card.POKER_CARD_VALUE))[0][1]
        elif self.hand is ScoreType.THREE_OF_A_KIND:
            return "Three of a kind of " + list(filter(lambda dict: dict[0] == self.trick[0][0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.hand is ScoreType.TWO_PAIRS:
            return "Two pairs of " + list(filter(lambda dict: dict[0] == self.trick[0][0].value, Card.POKER_CARD_VALUE))[0][1] + " and " + list(filter(lambda dict: dict[0] == self.trick[1][0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.hand is ScoreType.PAIR:
            return "Pair of " + list(filter(lambda dict: dict[0] == self.trick[0][0].value, Card.POKER_CARD_VALUE))[0][1]
        elif self.hand is ScoreType.FOLD:
            return "Fold"
        else:
            cards = sorted(self.other, key=Card.value, reverse=True)
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


class ScoreCalculator:
    cards: List[Card]
    res_val = dict
    res_col = dict

    # return top 5 card that make point to compare
    def __init__(self, user_hand: List[Card], current_board: List[Card] = None):
        if current_board is None:
            self.cards = user_hand
        else:
            self.cards = []
            self.cards.extend(user_hand)
            self.cards.extend(current_board)

    def get_score(self) -> Score:
        res = self.group_card()
        self.res_val = res[0]
        self.res_col = res[1]
        return self.is_royal_flush()

    def is_royal_flush(self) -> Score:
        cards = self.has_flush()
        cards = self.has_straight(cards)
        if len(cards) > 0:
            cards = sorted(cards, key=Card.value, reverse=True)
            if cards[0].value is Card.ACE and cards[1].value is Card.KING:
                return Score(ScoreType.ROYAL_FLUSH, [cards], [])
        return self.is_straight_flush()

    def is_straight_flush(self) -> Score:
        cards = self.has_flush()
        cards = self.has_straight(cards)
        if len(cards) > 0:
            cards = sorted(cards, key=Card.value, reverse=True)
            return Score(ScoreType.STRAIGHT_FLUSH, [cards], [])
        return self.is_four_of_a_kind()

    def is_four_of_a_kind(self) -> Score:
        res = {k: v for k, v in self.res_val.items() if v >= 4}
        if len(res) > 0:
            cards = list({c for c in self.cards if c.value is list(res.items())[0][0]})
            other = self.reduce(self.subtrat_card(self.cards, cards), 1)
            return Score(ScoreType.FOUR_OF_A_KIND, [cards], other)
        return self.is_full_house()

    def is_full_house(self) -> Score:
        res3 = {k: v for k, v in self.res_val.items() if v >= 3}
        res2 = {k: v for k, v in self.res_val.items() if v == 2}
        if len(res3) > 0 and len(res2) > 0:
            cards = list({c for c in self.cards if c.value is list(res3.items())[0][0]})
            pair = list({c for c in self.cards if c.value is list(res2.items())[0][0]})
            return Score(ScoreType.FULL_HOUSE, [cards, pair], [])
        return self.is_flush()

    def is_flush(self) -> Score:
        cards = self.has_flush()
        if len(cards) > 0:
            return Score(ScoreType.FLUSH, [self.reduce(cards, 5)], [])
        return self.is_straight()

    def is_straight(self) -> Score:
        cards = self.has_straight()
        if len(cards) > 0:
            return Score(ScoreType.STRAIGHT, [self.reduce(cards, 5)], [])
        return self.is_three_of_a_kind()

    def is_three_of_a_kind(self) -> Score:
        res = {k: v for k, v in self.res_val.items() if v >= 3}
        if len(res) > 0:
            cards = list({c for c in self.cards if c.value is list(res.items())[0][0]})
            other = self.reduce(self.subtrat_card(self.cards, cards), 2)
            return Score(ScoreType.THREE_OF_A_KIND, [cards], other)
        return self.is_two_pair()

    def is_two_pair(self) -> Score:
        res = {k: v for k, v in self.res_val.items() if v >= 2}
        if len(res) > 1:
            res = sorted(res.keys(), key=lambda e: e.value, reverse=True)
            pair1 = list({c for c in self.cards if c.value is res[0]})
            pair2 = list({c for c in self.cards if c.value is res[1]})
            other = self.reduce(self.subtrat_card(self.subtrat_card(self.cards, pair1), pair2), 1)
            return Score(ScoreType.TWO_PAIRS, [pair1, pair2], other)
        return self.is_pair()

    def is_pair(self) -> Score:
        res = {k: v for k, v in self.res_val.items() if v >= 2}
        if len(res) > 0:
            cards = list({c for c in self.cards if c.value is list(res.items())[0][0]})
            other = self.reduce(self.subtrat_card(self.cards, cards), 3)
            return Score(ScoreType.PAIR, [cards], other)
        return self.is_highcard()

    def is_highcard(self) -> Score:
        other = self.reduce(self.cards, 5)
        return Score(ScoreType.HIGH_CARD, [], other)

    def group_card(self, cards: List[Card] = None) -> tuple:
        if cards is None:
            cards = self.cards
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

    def has_flush(self, cards: List[Card] = None) -> List[Card]:
        if cards is None:
            res = self.res_col
            cards = self.cards
        else:
            res = self.group_card(cards)[1]
        res = {k for k, v in res.items() if v >= 5}
        for r in res:
            return list({o for o in cards if o.color is r})
        return []

    def has_straight(self, cards: List[Card] = None) -> List[Card]:
        if cards is None:
            cards = self.cards
        cards = sorted(cards, key=Card.value)
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
                count = 1
                last_value = c.value.value
            if c.value.value == last_value:
                current_group.append(c)
                last_value = c.value.value
            elif c.value.value == last_value + 1:
                current_group.append(c)
                count += 1
                last_value = c.value.value
            else:
                groups.append((current_group, count))
                current_group = [c]
                count = 1
                last_value = c.value.value
        # add last card
        groups.append((current_group, count))
        for r in groups:
            if r[1] >= 5:
                return r[0]
        return []

    def subtrat_card(self, cards: List[Card], to_delete: List[Card]) -> List[Card]:
        result = []
        result.extend(cards)
        for c in to_delete:
            result.remove(c)
        return result

    def reduce(self, cards: List[Card], number_to_keep: int) -> List[Card]:
        result = sorted(cards, key=Card.value)
        while len(result) > number_to_keep:
            result.pop(0)
        return result
