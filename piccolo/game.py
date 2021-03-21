from copy import copy
from random import shuffle, sample
from typing import List


class PiccoloDare:

    def __init__(self, start_text: str, duration: int, end_text: str or None, involved_players: int):
        self.duration: int = duration
        self.start_text: str = start_text
        self.end_text: str = end_text
        self.involved_players: int = involved_players

    def _format(self, text: str, players: List[str]) -> str:
        """ format the given text with the names of the players involved and with the duration if present """
        string: str = text
        pos: int = 1
        for name in players:
            string = string.replace(f"{{{pos}}}", name)
            pos += 1
        if self.duration != 0:
            string = string.replace("{d}", str(self.duration))
        return string

    def get_start_text(self, players: List[str]):
        """ format start_text with the names of the players involved and with the duration if present """
        return self._format(self.start_text, players)

    def get_end_text(self, players: List[str]):
        """ format end_text with the names of the players involved and with the duration if present """
        return self._format(self.end_text, players)

    def __str__(self):
        return f"duration: {self.duration}\nstart text: {self.start_text}\n" \
               f"end text: {self.end_text}\ninvolved players: {self.involved_players}"


class PiccoloGame:

    def __init__(self, dares_pool: List[PiccoloDare], players: List[str], rounds: int):
        self.players: List[str] = players
        self.rounds: int = rounds
        self.turns: int = rounds * len(players)
        self.lingering_dares: List[(PiccoloDare, int, List[str])] = []
        # generate the dares list by shuffling the dares_pool and slicing to the number of turns
        if len(dares_pool) >= self.turns:
            # if the number of dares is enough, just randomize and slice
            pool = self.randomize_dares_pool(dares_pool)
            self.dares: List[PiccoloDare] = pool[:self.turns]
        else:
            # if the number of dares in the pool isn't enough, dares have to be reused
            self.dares: List[PiccoloDare] = self.randomize_dares_pool(dares_pool)
            while len(self.dares) < self.turns:
                pool = self.randomize_dares_pool(dares_pool)
                if len(self.dares) + len(pool) < self.turns:
                    self.dares.extend(pool)
                else:
                    final_pos: int = self.turns - len(self.dares)
                    self.dares.extend(pool[:final_pos])

    @staticmethod
    def randomize_dares_pool( dares_pool: List[PiccoloDare]):
        pool: List[PiccoloDare] = copy(dares_pool)
        shuffle(pool)
        return pool

    def _remove_expired_dares(self, dares_to_remove: List):
        """ removes expired dares from self.lingering_dares """
        if len(dares_to_remove) != 0:
            for dare in dares_to_remove:
                self.lingering_dares.remove(dare)

    def _check_lingering_dares(self) -> List[str]:
        """ checks if there are any lingering dares that expired """
        expired_dares: List[str] = []
        dares_to_remove: List = []
        for dare in self.lingering_dares:
            if dare[1] == 0:
                dares_to_remove.append(dare)
                expired_dares.append(dare[0].get_end_text(dare[2]))
            else:
                dare[1] -= 1
        return expired_dares

    def do_turn(self) -> List[str] or None:
        """ :returns the list of dares messages to show or None if the game is finished """
        dares_to_return: List[str] = []
        # return None if the game is finished
        if len(self.dares) == 0:
            return None
        # get next dare
        next_dare: PiccoloDare = self.dares[0]
        # get involved players
        involved_players: List[str] = sample(self.players, next_dare.involved_players)
        # add the next dare to the dares to return
        dares_to_return.append(next_dare.get_start_text(involved_players))
        # if the next dare has a duration, add it to the lingering dares
        if next_dare.duration != 0:
            self.lingering_dares.append([next_dare, next_dare.duration, involved_players])
        # check if any lingering dare expired
        expired_dares = self._check_lingering_dares()
        # add expired lingering dares to dares to return
        if len(expired_dares) != 0:
            dares_to_return.extend(expired_dares)
        # remove next dare from dare queue
        self.dares.pop(0)
        return dares_to_return

    def __str__(self):
        string: str = f"players: {self.players}\ndares:"
        for dare in self.dares:
            string += f"\n\n{dare}"
        return string


if __name__ == "__main__":
    test_dares = [
        PiccoloDare("{1} aaaa {2}", 0, None, 2),
        PiccoloDare("1:{1} 2:{2} 3:{3} 2:{2}", 0, None, 3),
        PiccoloDare("{1}, {2} lingering start ({d})", 2, "{1}, {2} lingering end ({d})", 2)
    ]
    players = ["jhon", "elia", "matt"]
    game = PiccoloGame(test_dares, players, 1)
    print(game.do_turn())
    print(game.do_turn())
    print(game.do_turn())
    print(game.do_turn())