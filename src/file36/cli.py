import sys
import argparse
import logging
import threading
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


def main():
    parser = argparse.ArgumentParser(
        prog="file36",
        description="A file-transfer-over-sound utility.",
        epilog="By NIHILNE",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # PLAY PARSER & OPTIONS
    play_parser = subparsers.add_parser("play", help="Encode and play audio.")

    play_parser.add_argument(
        "--save", action="store_true", help="Export the audio as a WAV file."
    )
    play_parser.add_argument(
        "--visualize", action="store_true", help="Show a spectrogram."
    )
    play_parser.add_argument(
        "-v",
        "--volume",
        type=volume_type,
        default=DEFAULT_VOLUME,
    )
    play_parser.add_argument(
        "--speed",
        type=speed_type,
        default=DEFAULT_SPEED,
        choices=[s.name for s in Speed],
    )

    # PLAY MODES
    play_mode = play_parser.add_mutually_exclusive_group(required=True)

    play_mode.add_argument(
        "-d",
        "--demo",
        action="store_true",
        help="Encode and play demo data.",
    )

    play_mode.add_argument(
        "-t", "--text", metavar="TEXT", help="Encode and play a text string."
    )
    play_mode.add_argument(
        "-f", "--file", metavar="PATH", help="Encode and play a file."
    )
    play_mode.add_argument(
        "-b", "--bytes", metavar="HEX", help="Encode and play raw bytes (hex)."
    )

    # RECEIVE PARSER & OPTIONS
    receive_parser = subparsers.add_parser(
        "receive", help="Listen for and decode audio."
    )

    receive_parser.add_argument(
        "--save", action="store_true", help="Export the audio as a WAV file."
    )

    args = parser.parse_args()

    if args.command == "play":
        mode_play(args)
    elif args.command == "receive":
        mode_receive(args)


def mode_play(options: Namespace):
    if options.demo:
        sender = Sender(Mode.TEXT, "TEST_DATA 123!@", options.speed, options.volume)

    if options.text:
        sender = Sender(Mode.TEXT, options.text, options.speed, options.volume)

    if options.file:
        sender = Sender(Mode.FILE, options.file, options.speed, options.volume)

    if options.bytes:
        sender = Sender(
            Mode.RAW, bytes.fromhex(options.bytes), options.speed, options.volume
        )

    if options.visualize:
        play_thread = threading.Thread(target=sender.play)
        play_thread.start()
        sender.visualize()
        play_thread.join()
    else:
        sender.play()

    if options.save:
        sender.export_wav("./output.wav")


def mode_receive(options: Namespace):
    raise RuntimeError("Not implemented yet.")
