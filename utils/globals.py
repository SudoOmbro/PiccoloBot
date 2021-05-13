from typing import List

from piccolo.game import DaresCollection


class Globals:

    admins_list: List[int] = []
    DARES: DaresCollection = DaresCollection("dares")

    GAMES_PLAYED = 0
    DARES_COMPLETED = 0
    TOTAL_PLAYERS = 0
