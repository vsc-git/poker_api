from typing import List

from .models import Score, Card

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
            cards = sorted(cards, key=lambda card: card.value, reverse=True)
            if cards[0].value is Card.ACE and cards[1].value is Card.KING:
                return Score.create(Score.ROYAL_FLUSH, [cards], [])
        return self.is_straight_flush()

    def is_straight_flush(self) -> Score:
        cards = self.has_flush()
        cards = self.has_straight(cards)
        if len(cards) > 0:
            cards = sorted(cards, key=lambda card: card.value, reverse=True)
            return Score.create(Score.STRAIGHT_FLUSH, [cards], [])
        return self.is_four_of_a_kind()

    def is_four_of_a_kind(self) -> Score:
        res = {k: v for k, v in self.res_val.items() if v >= 4}
        if len(res) > 0:
            cards = list({c for c in self.cards if c.value is list(res.items())[0][0]})
            other = self.reduce(self.subtrat_card(self.cards, cards), 1)
            return Score.create(Score.FOUR_OF_A_KIND, [cards], other)
        return self.is_full_house()

    def is_full_house(self) -> Score:
        res3 = {k: v for k, v in self.res_val.items() if v >= 3}
        res2 = {k: v for k, v in self.res_val.items() if v == 2}
        if len(res3) > 0 and len(res2) > 0:
            cards = list({c for c in self.cards if c.value is list(res3.items())[0][0]})
            pair = list({c for c in self.cards if c.value is list(res2.items())[0][0]})
            return Score.create(Score.FULL_HOUSE, [cards, pair], [])
        return self.is_flush()

    def is_flush(self) -> Score:
        cards = self.has_flush()
        if len(cards) > 0:
            return Score.create(Score.FLUSH, [self.reduce(cards, 5)], [])
        return self.is_straight()

    def is_straight(self) -> Score:
        cards = self.has_straight()
        if len(cards) > 0:
            return Score.create(Score.STRAIGHT, [self.reduce(cards, 5)], [])
        return self.is_three_of_a_kind()

    def is_three_of_a_kind(self) -> Score:
        res = {k: v for k, v in self.res_val.items() if v >= 3}
        if len(res) > 0:
            cards = list({c for c in self.cards if c.value is list(res.items())[0][0]})
            other = self.reduce(self.subtrat_card(self.cards, cards), 2)
            return Score.create(Score.THREE_OF_A_KIND, [cards], other)
        return self.is_two_pair()

    def is_two_pair(self) -> Score:
        res = {k: v for k, v in self.res_val.items() if v >= 2}
        if len(res) > 1:
            res = sorted(res.keys(), reverse=True)
            pair1 = list({c for c in self.cards if c.value is res[0]})
            pair2 = list({c for c in self.cards if c.value is res[1]})
            other = self.reduce(self.subtrat_card(self.subtrat_card(self.cards, pair1), pair2), 1)
            return Score.create(Score.TWO_PAIRS, [pair1, pair2], other)
        return self.is_pair()

    def is_pair(self) -> Score:
        res = {k: v for k, v in self.res_val.items() if v >= 2}
        if len(res) > 0:
            cards = list({c for c in self.cards if c.value is list(res.items())[0][0]})
            other = self.reduce(self.subtrat_card(self.cards, cards), 3)
            return Score.create(Score.PAIR, [cards], other)
        return self.is_highcard()

    def is_highcard(self) -> Score:
        other = self.reduce(self.cards, 5)
        return Score.create(Score.HIGH_CARD, [], other)

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
        if len(cards) == 0:
            return []
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
        result = sorted(cards, key=lambda card: card.value)
        while len(result) > number_to_keep:
            result.pop(0)
        return result
