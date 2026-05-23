import logging
import wave
import numpy as np
import sounddevice as sd
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Annotated

from file36.config import DEFAULT_SPEED, DEFAULT_VOLUME
from file36.core.enums import Speed, Mode

matplotlib.use("Qt5Agg")


class Sender:
    SAMPLE_RATE = 192000
    FREQ_ZERO = 1200
    FREQ_ONE = 2300
    FREQ_SYNC = 1800
    EOT = b"\x04"

    def __init__(
        self,
        mode: Mode,
        data: str | Path | bytes,
        speed: Speed = DEFAULT_SPEED,
        volume: Annotated[float, "0.0 to 1.0"] = DEFAULT_VOLUME,
    ):
        if mode == Mode.TEXT and isinstance(data, str):
            self.data = data.encode()
        elif mode == Mode.FILE and isinstance(data, Path):
            self.file_path = Path(data)
            self.data = self._read_bytes()
        elif mode == Mode.RAW and isinstance(data, bytes):
            self.data = data
        else:
            raise ValueError(f"Invalid combination of {mode} and type {type(data)}")

        self.speed = speed
        self.volume = volume

    def _read_bytes(self):
        """Reads raw bytes of the object's file_path property"""
        with self.file_path.open("rb") as file:
            return file.read()

    def _to_bits(self, data: bytes):
        """Converts bytes to a list of bits (MSB)"""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
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
        """
        Returns a sequence of tones that acts as padding.
        Used before and after transmission
        """
        tones = [
            (600, 50),
            (0, 10),
            (600, 50),
            (700, 200),
        ]
        return self.sequence(tones)

    def header(self):
        """Returns a sequence that acts as the transmission start identifier"""
        tones = [
            (1900, 300),
            (1200, 10),
            (1900, 300),
        ]
        return self.sequence(tones)

    def eot(self):
        """Returns an End Of Transmission (EOT) byte"""
        return self.encode(self.EOT)

    def encode(self, data: bytes):
        """Encodes bytes to a tone sequence"""
        bits = self._to_bits(data)
        sequence = []
        for bit in bits:
            freq = self.FREQ_ONE if bit == 1 else self.FREQ_ZERO
            sequence.append((freq, self.speed.value))
            sequence.append((self.FREQ_SYNC, self.speed.value))

        return self.sequence(sequence)

    def build(self):
        """Builds and returns the full transmission waveform."""
        return np.concatenate(
            [
                self.padding(),
                self.header(),
                self.tone(self.FREQ_SYNC, self.speed.value * 2),
                self.encode(self.data),
                self.eot(),
                self.padding(),
            ]
        )

    def play(self):
        audio = self.build()
        sd.play(audio, self.SAMPLE_RATE)
        bps = 1000 / self.speed.value
        logging.info(
            f"Playing header + data ({len(audio) / self.SAMPLE_RATE:.2f}s total @ {bps:.0f}bits/s or {bps / 8:.0f}bytes/s)"
        )
        sd.wait()
        logging.info("Done!")

    def visualize(self):
        waveform = self.build()
        time = np.linspace(0, len(waveform) / self.SAMPLE_RATE, len(waveform))

        samples = int(self.SAMPLE_RATE * 0.2)
        plt.figure(figsize=(12, 4))
        plt.plot(time[:samples], waveform[:samples], linewidth=0.5)
        plt.title("Transmission Waveform")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.tight_layout()
        plt.show()

    def export_wav(self, output_path: str):
        """Builds the transmission waveform and exports it as a WAV file."""
        audio = self.build()
        pcm_audio = np.int16(audio * 32767)

        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(self.SAMPLE_RATE)
            wav_file.writeframes(pcm_audio.tobytes())

        logging.info(f"WAV exported to {output_path}")
