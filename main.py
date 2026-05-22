import sys
import argparse
import logging
from utils.sender import Sender
from core.enums import Mode

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

parser = argparse.ArgumentParser(description="File36")
parser.add_argument("mode", help="Whether to send or receive")
args = parser.parse_args()

match args.mode:
    case "send":
        print("You tried sending... but nothing happened yet.")
    case "receive":
        print("You tried receiving... but nothing happened yet.")
    case "test-run":
        sender = Sender(Mode.TEXT, "TEST_DATA 123!@")
        sender.play()
        sender.export_wav("./output.wav")
    case _:
        print("Invalid mode. Try `send`, `receive`, or `test-run`.")
        exit()
