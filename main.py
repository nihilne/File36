import sys
import argparse
import logging
from sender import Sender, Speed

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
    "%d-%m-%Y %H:%M:%S",
)
handler.setFormatter(formatter)
root.addHandler(handler)

parser = argparse.ArgumentParser(description="File36")
parser.add_argument("mode", help="Whether to send or receive")
args = parser.parse_args()

match args.mode:
    case "send":
        sender = Sender("./sample", volume=0.8, speed=Speed.HYPERFAST)
        sender.play()
    case "receive":
        print("Receive")
    case _:
        print("Nothing")
