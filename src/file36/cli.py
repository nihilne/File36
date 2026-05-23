import sys
import argparse
import logging
from argparse import Namespace

from file36.config import DEFAULT_VOLUME, DEFAULT_SPEED
from file36.core.sender import Sender
from file36.core.enums import Mode, Speed
from file36.core.types import volume_type, speed_type

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    "%d-%m-%Y %H:%M:%S",
)
handler.setFormatter(formatter)
root.addHandler(handler)


def mode_test(options: Namespace):
    sender = Sender(Mode.TEXT, "TEST_DATA 123!@", options.speed, options.volume)
    sender.play()

    if options.save:
        sender.export_wav("./output.wav")


def mode_unimplemented(options: Namespace):
    raise RuntimeError("Feature not implemented yet. Please use -t or --test.")


def main():
    parser = argparse.ArgumentParser(
        prog="file36",
        description="A file-transfer-over-sound utility.",
        epilog="By NIHILNE",
    )

    mode = parser.add_mutually_exclusive_group(required=True)

    mode.add_argument(
        "-t",
        "--text-mode",
        action="store_const",
        const=mode_unimplemented,
        dest="func",
        help="Encodes and plays the specified text.",
    )

    mode.add_argument(
        "-p",
        "--path-mode",
        action="store_const",
        const=mode_unimplemented,
        dest="func",
        help="Encodes and plays a file from the specified path.",
    )

    mode.add_argument(
        "-b",
        "--byte-mode",
        action="store_const",
        const=mode_unimplemented,
        dest="func",
        help="Encodes input to audio and plays it.",
    )

    mode.add_argument(
        "-r",
        "--receive",
        action="store_const",
        const=mode_unimplemented,
        dest="func",
        help="Listens for encoded audio and shows results.",
    )

    mode.add_argument(
        "--test",
        action="store_const",
        const=mode_test,
        dest="func",
        help="Plays test audio.",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Saves either the played audio or the received audio.",
    )

    parser.add_argument(
        "-v",
        "--volume",
        type=volume_type,
        default=DEFAULT_VOLUME,
        help="Sets the volume. Accepts values from 1 to 100.",
    )

    parser.add_argument(
        "--speed",
        type=speed_type,
        default=DEFAULT_SPEED,
        choices=list(Speed),
        help="Sets the speed (or BPS) of the encoded audio.",
    )

    args = parser.parse_args()

    args.func(args)
