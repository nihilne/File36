import sys
import argparse
import logging
from utils.sender import Sender
from core.enums import Mode, Speed

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

parser.add_argument(
    "-s",
    "--send",
    action="store_true",
    help="Encodes input to audio and plays it.",
)

parser.add_argument(
    "-r",
    "--receive",
    action="store_true",
    help="Listens for encoded audio and shows results.",
)

parser.add_argument(
    "-t",
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

if options.send and options.receive:
    raise ValueError("Sending and receiving are mutually exclusive options.")

if options.send or options.receive:
    raise RuntimeError("Feature not implemented yet. Please use -t or --test.")

if options.test:
    sender = Sender(Mode.TEXT, "TEST_DATA 123!@", Speed.HYPERFAST)
    sender.play()

    if options.save:
        sender.export_wav("./")
