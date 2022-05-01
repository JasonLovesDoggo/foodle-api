import enum


def swap_mode(mode: str):
    mode = mode.lower()
    if mode == "infinite":
        return Modes.INFINITE
    elif mode == "daily":
        return Modes.DAILY
    elif mode == "hourly":
        return Modes.HOURLY
    #elif mode == "minutely":
    #    return Modes.MINUTELY
    else:
        raise ValueError("Invalid mode: " + mode + " is not a valid mode.")


class Modes(enum.Enum):
    """
    Enum for the different modes of the program.
    """
    INFINITE = 0
    DAILY = 1
    HOURLY = 2
    MINUTELY = 3
