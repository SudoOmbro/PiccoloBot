from copy import copy
from random import shuffle, sample
from typing import List


class PiccoloDare:

    def __init__(self, start_text: str, duration: int, end_text: str, level: int, name: str, involved_players: int):
        # metadata
        self.name: str = name
        self.level: int = level
        # game data
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


class PiccoloGame:

    def __init__(self, dares_pool: List[PiccoloDare], players: List[str], rounds: int):
        self.players: List[str] = players
        self.rounds: int = rounds
        self.turns: int = rounds * len(players)
        self.lingering_dares: List[List[PiccoloDare, int, List[str]]] = []
        # generate the dares list by shuffling the dares_pool and slicing to the number of turns
        pool: List[PiccoloDare] = copy(dares_pool)
        shuffle(pool)
        self.dares = pool[:self.turns]

    def _remove_expired_dares(self, dares_to_remove: List[List[PiccoloDare, int, List[str]]]):
        if len(dares_to_remove) != 0:
            for dare in dares_to_remove:
                self.lingering_dares.remove(dare)

    def _check_lingering_dares(self) -> List[(List[PiccoloDare], List[str])]:
        expired_dares: (List[PiccoloDare], List[str]) = []
        dares_to_remove: List[(List[PiccoloDare], int, List[str])] = []
        for dare in self.lingering_dares:
            if dare[1] == 0:
                dares_to_remove.append(dare)
                expired_dares.append((dare[0], dare[2]))
        return expired_dares

    def do_turn(self) -> List[(List[PiccoloDare], List[str])] or None:
        """ :returns the list of dares to show or None if the game is finished """
        dares_to_return: List[(List[PiccoloDare], List[str])] = []
        if len(self.dares):
            return None
        next_dare = self.dares[0]
        dares_to_return.append((next_dare, sample(self.players, next_dare.involved_players)))
        self.dares.pop(0)
        expired_dares = self._check_lingering_dares()
        if len(expired_dares) != 0:
            dares_to_return.extend(expired_dares)
        return dares_to_return
