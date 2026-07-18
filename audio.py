"""
Morse code audio using synthesised tones.

The whole message is rendered into a single in-memory WAV file and handed to
the sound system in one go. That is what keeps the interface responsive:
there is no per-symbol sleeping on the main thread.

Timing follows the standard Morse ratios, where one 'unit' is the length of
a dot:

    dot                 1 unit      gap between symbols   1 unit
    dash                3 units     gap between letters   3 units
                                    gap between words     7 units

A dot lasts 1.2 / wpm seconds, which is the usual PARIS convention, so 20
words per minute gives a 60 ms dot.

Only the standard library is used. Playback prefers winsound on Windows and
falls back to pygame elsewhere if it happens to be installed.
"""

import io
import math
import wave
import array
import sys

SAMPLE_RATE = 44100
DEFAULT_FREQUENCY = 600     # Hz - the traditional pitch for Morse listening
DEFAULT_WPM = 20
RAMP_SECONDS = 0.005        # short fade in/out to stop tones clicking

# Timing ratios, in dot units.
DOT_UNITS = 1
DASH_UNITS = 3
SYMBOL_GAP_UNITS = 1
LETTER_GAP_UNITS = 3
WORD_GAP_UNITS = 7


def dot_duration(wpm):
    """Length of a single dot, in seconds, for the given words per minute."""
    if wpm <= 0:
        raise ValueError("Speed must be greater than zero.")
    return 1.2 / wpm


def _tone(samples_out, seconds, frequency):
    """Append a fading-in-and-out sine tone to samples_out."""
    total = int(SAMPLE_RATE * seconds)
    ramp = min(int(SAMPLE_RATE * RAMP_SECONDS), total // 2)
    step = 2 * math.pi * frequency / SAMPLE_RATE

    for i in range(total):
        amplitude = 0.6
        # Taper the very start and end of the tone. Without this the abrupt
        # jump from silence to full volume is audible as a click.
        if ramp:
            if i < ramp:
                amplitude *= i / ramp
            elif i > total - ramp:
                amplitude *= (total - i) / ramp
        samples_out.append(int(32767 * amplitude * math.sin(step * i)))


def _silence(samples_out, seconds):
    """Append a run of silent samples to samples_out."""
    samples_out.extend([0] * int(SAMPLE_RATE * seconds))


def render_wav(code, wpm=DEFAULT_WPM, frequency=DEFAULT_FREQUENCY):
    """
    Render Morse code text into WAV file bytes.

    'code' is a string of dots, dashes and '/' separators as produced by
    morse.encode. Returns the complete contents of a WAV file, ready to be
    played or written to disk.
    """
    unit = dot_duration(wpm)
    samples = array.array('h')

    words = [w for w in code.replace('|', '/').split('/') if w.strip()]

    for word_index, word in enumerate(words):
        if word_index:
            _silence(samples, unit * WORD_GAP_UNITS)

        letters = word.split()
        for letter_index, letter in enumerate(letters):
            if letter_index:
                _silence(samples, unit * LETTER_GAP_UNITS)

            for symbol_index, symbol in enumerate(letter):
                if symbol_index:
                    _silence(samples, unit * SYMBOL_GAP_UNITS)
                if symbol == '.':
                    _tone(samples, unit * DOT_UNITS, frequency)
                elif symbol == '-':
                    _tone(samples, unit * DASH_UNITS, frequency)

    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(samples.tobytes())
    return buffer.getvalue()


class Player:
    """
    Plays rendered Morse audio without blocking the caller.

    Falls back to doing nothing (reporting available == False) when no usable
    sound backend is present, so the rest of the application still runs.
    """

    def __init__(self):
        self.backend = None
        self._winsound = None
        self._pygame = None

        if sys.platform == 'win32':
            try:
                import winsound
                self._winsound = winsound
                self.backend = 'winsound'
            except ImportError:
                pass

        if self.backend is None:
            try:
                import pygame
                pygame.mixer.init(frequency=SAMPLE_RATE, channels=1)
                self._pygame = pygame
                self.backend = 'pygame'
            except Exception:
                pass

    @property
    def available(self):
        return self.backend is not None

    def play(self, wav_bytes):
        """Start playing WAV data and return immediately."""
        if self.backend == 'winsound':
            self._winsound.PlaySound(
                wav_bytes,
                self._winsound.SND_MEMORY | self._winsound.SND_ASYNC,
            )
        elif self.backend == 'pygame':
            sound = self._pygame.mixer.Sound(io.BytesIO(wav_bytes))
            sound.play()

    def stop(self):
        """Cut playback short."""
        if self.backend == 'winsound':
            self._winsound.PlaySound(None, self._winsound.SND_PURGE)
        elif self.backend == 'pygame':
            self._pygame.mixer.stop()


def save_wav(code, path, wpm=DEFAULT_WPM, frequency=DEFAULT_FREQUENCY):
    """Render Morse code and write it to a .wav file."""
    with open(path, 'wb') as handle:
        handle.write(render_wav(code, wpm, frequency))
