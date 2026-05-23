import sys
import argparse
import logging
from file36.core.sender import Sender
from file36.core.enums import Mode, Speed

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

parser = argparse.ArgumentParser(
    prog="file36",
    description="A file-transfer-over-sound utility.",
    epilog="By NIHILNE",
)

mode = parser.add_mutually_exclusive_group(required=True)

mode.add_argument(
    "-t",
    "--text-mode",
    action="store_true",
    help="Encodes and plays the specified text.",
)

mode.add_argument(
    "-p",
    "--path-mode",
    action="store_true",
    help="Encodes and plays a file from the specified path.",
)

mode.add_argument(
    "-b",
    "--byte-mode",
    action="store_true",
    help="Encodes input to audio and plays it.",
)

mode.add_argument(
    "-r",
    "--receive",
    action="store_true",
    help="Listens for encoded audio and shows results.",
)

mode.add_argument(
    "--test",
    action="store_true",
    help="Plays test audio.",
)

parser.add_argument(
    "--save",
    action="store_true",
    help="Saves either the played audio or the received audio.",
)

options = parser.parse_args()

if not any(vars(options).values()):
    parser.error("No options given.")

if not options.test:
    raise RuntimeError("Feature not implemented yet. Please use -t or --test.")

if options.test:
    sender = Sender(Mode.TEXT, "TEST_DATA 123!@", Speed.HYPERFAST)
    sender.play()

    if options.save:
        sender.export_wav("./output.wav")
