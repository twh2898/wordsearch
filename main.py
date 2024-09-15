#!/usr/bin/env python3

def load_word_list(filepath: str) -> list[str]:
    with open(filepath, 'r') as f:
        return list(filter(len, map(str.upper, map(str.strip, f))))


def load_card(filepath: str) -> list[list[str]]:
    rows = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip().upper()
            if not line:
                continue
            letters = list(line)
            rows.append(letters)
            assert len(letters) == len(rows[0])
    return rows


XY = tuple[int, int]


class Search:
    words: list[str]
    letter_map: dict[str, dict[str, list[str]]]

    def __init__(self, words: list[str], first_match_stop: bool = True):
        self.words = words
        self.letter_map = {}
        self._gen_letter_map()
        self.first_match_stop = first_match_stop

    def _gen_letter_map(self):
        l_map = {}

        for word in words:
            first = word[0]
            second = word[1]
            if first not in l_map:
                l_map[first] = {}
            if second not in l_map[first]:
                l_map[first][second] = []
            l_map[first][second].append(word)

        self.letter_map = dict(l_map)

    def _search_delta(self, row: int, col: int, delta: XY, words: list[str]):
        r, c = row + delta[0] * 2, col + delta[1] * 2
        partial = words[0][:2]

        for i in range(2, max(map(len, words))):
            if c < 0 or c >= self._shape[0] \
                or r < 0 or r >= self._shape[1] \
                    or r == row and c == col:
                return

            letter = self._card[r][c]
            partial += letter

            to_remove = list(filter(lambda w: len(w) < i and w[i] == letter, words))
            for word in to_remove:
                words.remove(word)

            if len(words) == 0:
                return
            elif partial in words:
                self._solution[partial] = (row, col), (r, c)
                if self.first_match_stop:
                    return

            r += delta[0]
            c += delta[1]

    def _find_second(self, row: int, col: int, first: dict[str, list[str]]):
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if c < 0 or c >= self._shape[0] \
                    or r < 0 or r >= self._shape[1] \
                        or r == row and c == col:
                    continue

                l_second = self._card[r][c]

                words = first.get(l_second, None)
                if words:
                    delta = (r - row, c - col)
                    assert delta[0] != 0 or delta[1] != 0
                    self._search_delta(row, col, delta, words)

    def solve(self, card: list[list[str]]) -> dict[str, tuple[XY, XY]]:
        self._card = card
        self._shape = (len(card[0]), len(card))
        self._solution: dict[str, tuple[XY, XY]] = {}

        for r, row in enumerate(card):
            for c, letter in enumerate(row):
                first = self.letter_map.get(letter, None)
                if first:
                    self._find_second(r, c, first)

            if len(self._solution) == len(self.words):
                break

        return self._solution


def to_human(solution: dict[str, tuple[XY, XY]]) -> dict[str, tuple[XY, XY]]:
    return {word: ((start[1] + 1, start[0] + 1), (end[1] + 1, end[0] + 1)) for word, (start, end) in solution.items()}


if __name__ == '__main__':
    words = load_word_list('words.txt')
    card = load_card('card.txt')

    print('Searching card for', len(words), 'words')

    search = Search(words)
    print('Letter map is', search.letter_map)

    solution = search.solve(card)
    solution = to_human(solution)
    print('Solution is')
    for word, (start, end) in solution.items():
        space = max(map(len, solution.keys()))
        print(f'{word:{space}} {str(start):8} {end}')

    from timeit import timeit
    time = timeit(lambda: search.solve(card), number=1000)
    print('Average solve time:', time, 's')
