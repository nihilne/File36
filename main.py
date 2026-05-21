import sys
import argparse
import logging
from utils.sender import Sender

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
        sender = Sender("./sample")
        sender.play()
    case "receive":
        print("You tried receiving... but nothing happened yet.")
    case _:
        print("Invalid mode. Try `send` or `receive`.")
        exit()
