from enum import Enum

class Time(str, Enum):
    DAY = "day"
    SUNSET = "sunset"
    NIGHT = "night"

    @classmethod
    def get_time_description(cls, time: str) -> str:
        if time == cls.DAY:
            return "day"
        elif time == cls.SUNSET:
            return "sunset"
        elif time == cls.NIGHT:
            return "night"
