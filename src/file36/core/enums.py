from enum import Enum


class Speed(Enum):
    def __str__(self):
        return self.name

    SLOW = 500
    MEDIUM = 300
    FAST = 200
    SUPERFAST = 100
    ULTRAFAST = 50
    HYPERFAST = 10
    ULTRAKILL = 5


class Mode(Enum):
    TEXT = 1
    FILE = 2
    RAW = 3
