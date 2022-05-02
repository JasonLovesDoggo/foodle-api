import enum
from typing import Literal


def swap_mode(mode: str):
    mode = mode.lower()
    if mode == "infinite":
        return Modes.INFINITE
    elif mode == "daily":
        return Modes.DAILY
    elif mode == "hourly":
        return Modes.HOURLY
    # elif mode == "minutely":
    #    return Modes.MINUTELY
    else:
        raise ValueError("Invalid mode: " + mode + " is not a valid mode.")


Guesses = Literal[1, 2, 3, 4, 5, 6, 0]


class Modes(enum.Enum):
    """
    Enum for the different modes of the program.
    """
    INFINITE = 'infinite'
    DAILY = 'daily'
    HOURLY = 'hourly'
    MINUTELY = 'minutely'
