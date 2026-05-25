import argparse
import logging
import sys
import threading
from argparse import Namespace

from file36.config import DEFAULT_SPEED, DEFAULT_VOLUME
from file36.core.enums import Mode, Speed
from file36.core.sender import Sender
from file36.core.receiver import Receiver
from file36.core.types import speed_type, volume_type

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


def main():
    parser = argparse.ArgumentParser(
        prog="file36",
        description="A file-transfer-over-sound utility.",
        epilog="By NIHILNE",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # PLAY PARSER & OPTIONS
    send_parser = subparsers.add_parser("send", help="Encode and play audio.")

    send_parser.add_argument(
        "--save", action="store_true", help="Export the audio as a WAV file."
    )
    send_parser.add_argument(
        "--visualize", action="store_true", help="Show a spectrogram."
    )
    send_parser.add_argument(
        "-v",
        "--volume",
        type=volume_type,
        default=DEFAULT_VOLUME,
    )
    send_parser.add_argument(
        "--speed",
        type=speed_type,
        default=DEFAULT_SPEED,
        choices=list(Speed),
    )

    # SEND MODES
    send_mode = send_parser.add_mutually_exclusive_group(required=True)

    send_mode.add_argument(
        "-d",
        "--demo",
        action="store_true",
        help="Encode and play demo data.",
    )

    send_mode.add_argument(
        "-t", "--text", metavar="TEXT", help="Encode and play a text string."
    )
    send_mode.add_argument(
        "-f", "--file", metavar="PATH", help="Encode and play a file."
    )

    # RECEIVE PARSER & OPTIONS
    receive_parser = subparsers.add_parser(
        "receive", help="Listen for and decode audio."
    )

    receive_parser.add_argument(
        "--save", action="store_true", help="Export the audio as a WAV file."
    )

    args = parser.parse_args()

    if args.command == "send":
        mode_send(args)
    elif args.command == "receive":
        mode_receive(args)


def mode_send(options: Namespace):
    if options.demo:
        send = Sender(Mode.TEXT, "TEST_DATA 123!@", options.speed, options.volume)

    if options.text:
        send = Sender(Mode.TEXT, options.text, options.speed, options.volume)

    if options.file:
        send = Sender(Mode.FILE, options.file, options.speed, options.volume)

    if options.visualize:
        send_thread = threading.Thread(target=send.play)
        send_thread.start()
        send.visualize()
        send_thread.join()
    else:
        send.play()

    if options.save:
        send.export_wav("./output.wav")


def mode_receive(options: Namespace):
    Receiver(DEFAULT_SPEED).receive()
