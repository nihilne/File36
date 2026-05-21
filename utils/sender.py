import logging
import numpy as np
import sounddevice as sd
from pathlib import Path
from typing import Annotated

from config import DEFAULT_SPEED, DEFAULT_VOLUME
from core.enums import Speed


class Sender:
    SAMPLE_RATE = 44100
    FREQ_ZERO = 1200
    FREQ_ONE = 2200
    FREQ_SYNC = 1700

    def __init__(
        self,
        file_path: str,
        speed: Speed = DEFAULT_SPEED,
        volume: Annotated[float, "0.0 to 1.0"] = DEFAULT_VOLUME,
    ):
        self.file_path = Path(file_path)
        self.speed = speed
        self.volume = volume

    def read_bytes(self):
        """Reads raw bytes of the file speficied."""
        with self.file_path.open("rb") as file:
            return file.read()

    def to_bits(self, data: bytes):
        bits = []
        for byte in data:
            for i in range(7, -1, -1):  # MSB for some reason
                bits.append((byte >> i) & 1)
        return bits

    def tone(self, freq: int, duration: int):
        """Generates a tone given a frequency and a duration in milliseconds."""
        d = duration / 1000.0
        t = np.linspace(0, d, int(self.SAMPLE_RATE * d), False)
        sine = np.sin(2 * np.pi * freq * t)
        return sine.astype(np.float32) * self.volume

    def sequence(self, sequence: list[tuple[int, int]]):
        """
        Generates a sequence of tones given a list of
        tones containing the frequency and duration
        (in ms) of each tone.
        """
        parts = []
        for freq, duration in sequence:
            parts.append(self.tone(freq, duration))

        return np.concatenate(parts)

    def padding(self):
        tones = [
            (600, 50),
            (0, 50),
            (600, 50),
            (700, 200),
        ]
        return self.sequence(tones)

    def header(self):
        tones = [
            (1900, 300),
            (1200, 50),
            (1900, 300),
        ]
        return self.sequence(tones)

    def encode(self):
        data = self.read_bytes()
        bits = self.to_bits(data)
        sequence = []
        for bit in bits:
            freq = self.FREQ_ONE if bit == 1 else self.FREQ_ZERO
            sequence.append((freq, self.speed.value))
            sequence.append((self.FREQ_SYNC, self.speed.value))

        return self.sequence(sequence)

    def play(self):
        all = np.concatenate(
            [
                self.padding(),
                self.header(),
                self.tone(self.FREQ_SYNC, self.speed.value * 2),
                self.encode(),
                self.padding(),
            ]
        )
        sd.play(all, self.SAMPLE_RATE)
        bps = 1000 / self.speed.value
        logging.info(
            f"Playing header + data ({len(all) / self.SAMPLE_RATE:.2f}s total @ {bps:.0f}bits/s or {bps / 8:.0f}bytes/s)"
        )
        sd.wait()
        logging.info("Done!")
