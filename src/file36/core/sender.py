import logging
import threading
import wave
from pathlib import Path
from typing import Annotated

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from reedsolo import RSCodec

from file36.core.enums import Mode, Speed

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
        speed: Speed,
        volume: Annotated[int, "1 to 100"],
        ecc_bytes: int = 2,
        block_ecc_bytes: int = 32,
    ):
        if mode == Mode.TEXT and isinstance(data, str):
            self.data = data.encode()
        elif mode == Mode.FILE and isinstance(data, str):
            self.file_path = Path(data)
            self.data = self._read_bytes()
        elif mode == Mode.RAW and isinstance(data, bytes):
            self.data = data
        else:
            raise ValueError(f"Invalid combination of {mode} and type {type(data)}")

        self.speed = speed
        self.volume = volume / 100
        self.mode = mode
        self.rsc = RSCodec(ecc_bytes)
        self.rsc_block = RSCodec(block_ecc_bytes)

    @staticmethod
    def _to_bits(data: bytes) -> list[int]:
        """Converts bytes to a list of bits (MSB)"""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits

    def _read_bytes(self) -> bytes:
        """Reads a file as bytes from object's `file_path` property"""
        with self.file_path.open("rb") as file:
            return file.read()

    def _generate_tone(self, freq: int, duration: int):
        """Generates a tone given a frequency and a duration in milliseconds."""
        d = duration / 1000
        t = np.linspace(0, d, int(self.SAMPLE_RATE * d), False)
        sine = np.sin(2 * np.pi * freq * t)
        return sine.astype(np.float32) * self.volume

    def _construct_sequence(self, sequence: list[tuple[int, int]]):
        """
        Generates a sequence of tones given a list of
        tones containing the frequency and duration
        (in ms) of each tone.
        """
        parts = []
        for freq, duration in sequence:
            parts.append(self._generate_tone(freq, duration))

        return np.concatenate(parts)

    def encode(self, data: bytes):
        """Encodes bytes to a tone sequence."""
        if self.mode == Mode.TEXT:
            encoded = b""
            for byte in data:
                block = bytes(self.rsc.encode(bytes([byte])))
                encoded += block
        else:
            encoded = bytes(self.rsc_block.encode(data))

        sequence = []
        for bit in self._to_bits(encoded):
            freq = self.FREQ_ONE if bit == 1 else self.FREQ_ZERO
            sequence.append((freq, self.speed.value))
            sequence.append((self.FREQ_SYNC, self.speed.value))
        return self._construct_sequence(sequence)

    def padding(self):
        """
        Returns a sequence of tones that acts as padding.
        Used before and after transmission.
        """
        tones = [
            (600, 150),
            (700, 150),
        ]
        return self._construct_sequence(tones)

    def header(self):
        """Returns a sequence that acts as the transmission start identifier"""
        tones = [
            (1900, 300),
            (1200, 10),
            (1900, 300),
        ]
        return self._construct_sequence(tones)

    def mode_header(self):
        """Returns a sequence that signifies the mode of encoded audio being transmitted"""
        match self.mode:
            case Mode.TEXT:
                freq = (1500, 150)
            case Mode.FILE:
                freq = (2000, 150)
            case Mode.RAW:
                freq = (2500, 150)
            case _:
                freq = (250, 150)

        tones = [
            (500, 150),
            freq,
        ]
        return self._construct_sequence(tones)

    def build(self):
        """Builds and returns the full transmission waveform."""
        return np.concatenate(
            [
                self.padding(),
                self.header(),
                self.mode_header(),
                self.encode(self.data + self.EOT),
                self.padding(),
            ]
        ).astype(np.float32)

    def play(self):
        """Plays audio using sd.OutputStream()"""
        audio = self.build()
        bps = 1000 / self.speed.value
        logging.info(
            f"Playing header + data ({len(audio) / self.SAMPLE_RATE:.2f}s total @ "
            f"{bps:.0f}bits/s or {bps / 8:.0f}bytes/s)"
        )
        position = 0
        done = threading.Event()

        def callback(outdata, frames, time, status):
            nonlocal position
            if status:
                logging.warning(f"Stream status: {status}")
            chunk = audio[position : position + frames]
            outdata[: len(chunk), 0] = chunk
            outdata[len(chunk) :] = 0
            position += frames
            if len(chunk) < frames:
                done.set()
                raise sd.CallbackStop()

        with sd.OutputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=callback,
        ):
            done.wait()

        logging.info("Done!")

    def visualize(self):
        """Builds the transmission waveform and shows a spectrogram of it."""
        waveform = self.build()
        plt.figure(figsize=(12, 4))
        plt.specgram(
            waveform,
            Fs=self.SAMPLE_RATE,
            cmap="inferno",
            NFFT=4096,
            noverlap=3072,
            vmin=-80,
        )
        plt.ylim(0, 3500)
        plt.title("Transmission Spectrogram")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.colorbar(label="Intensity (dB)")
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
