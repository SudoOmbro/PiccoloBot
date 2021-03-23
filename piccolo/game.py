from copy import copy
from random import shuffle, sample, randint, choice
from typing import List

from utils.filesystem import load_json, save_json


class PiccoloDare:

    LETTERS = "QWERTYUIOPASDFGHJKLZXCVBNM"

    def __init__(
            self,
            start_text: str = "skip turn",
            duration: int = 0,
            end_text: str or None = None,
            involved_players: int = 0,
            wiggle: int = 0,
            strings: List[str] or None = None
    ):
        self.duration: int = duration  # the duration of the dare
        self.start_text: str = start_text  # the text that comes out at the start of the dare
        self.end_text: str = end_text  # the text that comes out at the end of the dare
        self.involved_players: int = involved_players  # the number of involved players
        self.wiggle: int = wiggle  # the wiggle room to the duration (duration + wiggle = max duration)
        self.strings: List[str] or None = strings  # the strings from which the game can randomly select from for {r}

    def load_from_json(self, json_data: dict):
        self.__dict__.update(json_data)

    def dump_to_json(self):
        return self.__dict__

    def _format(self, text: str, players: List[str]) -> str:
        """ format the given text with the names of the players involved and with the duration if present """
        string: str = text
        # add player names
        pos: int = 1
        for name in players:
            string = string.replace(f"{{{pos}}}", name)
            pos += 1
        # add the duration
        if self.duration != 0:
            string = string.replace("{d}", str(self.duration))
        # add random letters
        string = string.replace("{l}", self.LETTERS[randint(0, len(self.LETTERS) - 1)])
        # add random selection from string list
        if self.strings is not None:
            string = string.replace("{r}", choice(self.strings))
        # return
        return string

    def get_start_text(self, players: List[str]):
        """ format start_text with the names of the players involved and with the duration if present """
        return self._format(self.start_text, players)

    def get_end_text(self, players: List[str]):
        """ format end_text with the names of the players involved and with the duration if present """
        return self._format(self.end_text, players)

    def __str__(self):
        return f"duration: {self.duration} + {self.wiggle}\nstart text: {self.start_text}\n" \
               f"end text: {self.end_text}\ninvolved players: {self.involved_players}\n" \
               f"strings: {self.strings}"


class DaresCollection:

    def __init__(self, filename: str):
        self.filename: str = filename
        self.pool: List[PiccoloDare] = []
        json_data: dict or None = load_json(filename)
        if json_data is not None:
            for dare_dict in json_data["dares"]:
                self.add_dare_from_dict(dare_dict)
        else:
            self.save()

    def add_dare(self, dare: PiccoloDare):
        self.pool.append(dare)

    def add_dare_from_dict(self, dare_dict: dict):
        dare: PiccoloDare = PiccoloDare()
        dare.load_from_json(dare_dict)
        self.pool.append(dare)

    def delete_dare(self, index: int):
        self.pool.pop(index)

    def save(self):
        """ save the collection to filename.json """
        pool: List[dict] = []
        for dare in self.pool:
            pool.append(dare.dump_to_json())
        json_data: dict = {
            "dares": pool
        }
        save_json(json_data, self.filename)

    def get_pages(self, dares_per_page: int = 20) -> List[str]:
        """ get a list of pages with dares_per_page dares printed on them """
        pages: List[str] = []
        pos: int = 0
        counter: int = 0
        string: str = ""
        for dare in self.pool:
            if counter < dares_per_page:
                string += f"dare {pos}:\n{dare}\n\n"
            else:
                counter = 0
                pages.append(string)
                string = f"dare {pos}:\n{dare}\n\n"
            pos += 1
        if len(string) != 0:
            pages.append(string)
        return pages

    def __str__(self):
        string: str = ""
        pos: int = 0
        for dare in self.pool:
            string += f"dare {pos}:\n{dare}\n\n"
            pos += 1
        return string


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
        self._remove_expired_dares(dares_to_remove)
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
        player_number = next_dare.involved_players
        # skip dares that can't be done for a lack of players
        while player_number > len(self.players):
            self.dares.pop(0)
            if len(self.dares) != 0:
                next_dare: PiccoloDare = self.dares[0]
                player_number = next_dare.involved_players
            else:
                return None
        involved_players: List[str] = sample(self.players, player_number)
        # add the next dare to the dares to return
        dares_to_return.append(next_dare.get_start_text(involved_players))
        # if the next dare has a duration, add it to the lingering dares
        if next_dare.duration != 0:
            self.lingering_dares.append([
                next_dare,
                next_dare.duration if next_dare.wiggle == 0 else next_dare.duration + randint(0, next_dare.wiggle),
                involved_players])
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
        PiccoloDare("{1} aaaa {2} {l}", 0, None, 2),
        PiccoloDare("1:{1} 2:{2} 3:{3} 2:{2}", 0, None, 3),
        PiccoloDare("{1}, {2} lingering start ({d})", 2, "{1}, {2} lingering end ({d})", 2),
        PiccoloDare("{1} {r}", 0, None, 1, strings=["string1", "string2", "string3"]),
    ]
    players = ["jhon", "elia", "matt"]
    rounds = 2
    game = PiccoloGame(test_dares, players, rounds)
    for i in range(len(players) * rounds):
        print(game.do_turn())
    print(game.do_turn())
