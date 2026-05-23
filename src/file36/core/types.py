from argparse import ArgumentTypeError

from file36.core.enums import Speed


def volume_type(x):
    ivalue = int(x)
    if 1 <= ivalue <= 100:
        return ivalue
    raise ArgumentTypeError("Must be 1-100")


def speed_type(value):
    try:
        return Speed[value.upper()]
    except KeyError:
        raise ArgumentTypeError(
            f"Invalid speed: {value}. Must be one of {[s.name for s in Speed]}"
        )
