from typing import List

from piccolo.game import DaresCollection


class Globals:

    admins_list: List[int] = []
    DARES: DaresCollection = DaresCollection("dares")
