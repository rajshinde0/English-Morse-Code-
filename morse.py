"""
Morse code encoding and decoding.

Pure functions only - no GUI, no audio, no file access. This means the
translation logic can be imported and tested on its own:

    >>> from morse import encode, decode
    >>> encode("HELLO WORLD")
    '.... . .-.. .-.. --- / .-- --- .-. .-.. -..'
    >>> decode('.... . .-.. .-.. --- / .-- --- .-. .-.. -..')
    'HELLO WORLD'
"""

# International Morse Code (ITU-R M.1677-1)
CHAR_TO_MORSE = {
    'A': '.-',     'B': '-...',   'C': '-.-.',   'D': '-..',
    'E': '.',      'F': '..-.',   'G': '--.',    'H': '....',
    'I': '..',     'J': '.---',   'K': '-.-',    'L': '.-..',
    'M': '--',     'N': '-.',     'O': '---',    'P': '.--.',
    'Q': '--.-',   'R': '.-.',    'S': '...',    'T': '-',
    'U': '..-',    'V': '...-',   'W': '.--',    'X': '-..-',
    'Y': '-.--',   'Z': '--..',
    '0': '-----',  '1': '.----',  '2': '..---',  '3': '...--',
    '4': '....-',  '5': '.....',  '6': '-....',  '7': '--...',
    '8': '---..',  '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.',  '(': '-.--.',  ')': '-.--.-',
    '&': '.-...',  ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.',  '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.',
}

MORSE_TO_CHAR = {morse: char for char, morse in CHAR_TO_MORSE.items()}

# Separators used in the text representation of Morse code.
LETTER_GAP = ' '
WORD_GAP = ' / '


class MorseError(ValueError):
    """Raised when input cannot be translated."""


def encode(text):
    """
    Convert English text to Morse code.

    Letters are separated by a space and words by ' / '. Raises MorseError
    if the text is empty or contains no translatable characters.
    """
    if not text or not text.strip():
        raise MorseError("Nothing to translate - the input is empty.")

    unsupported = set()
    words = []

    for word in text.upper().split():
        letters = []
        for char in word:
            if char in CHAR_TO_MORSE:
                letters.append(CHAR_TO_MORSE[char])
            else:
                # Collect rather than fail, so one stray character does not
                # throw away an otherwise valid translation.
                unsupported.add(char)
        if letters:
            words.append(LETTER_GAP.join(letters))

    if not words:
        raise MorseError(
            "None of those characters can be written in Morse code: "
            + ' '.join(sorted(unsupported))
        )

    return WORD_GAP.join(words)


def decode(code):
    """
    Convert Morse code back to English text.

    Accepts words separated by '/' or '|' with any surrounding whitespace.
    Unrecognised sequences become '#' so the position of the problem stays
    visible in the output.
    """
    if not code or not code.strip():
        raise MorseError("Nothing to translate - the input is empty.")

    stray = set(code) - set('.-/| \t\n')
    if stray:
        raise MorseError(
            "Morse code may only contain dots, dashes and '/': "
            "found " + ' '.join(sorted(stray))
        )

    normalised = code.replace('|', '/')
    words = []

    for chunk in normalised.split('/'):
        letters = [MORSE_TO_CHAR.get(seq, '#') for seq in chunk.split()]
        if letters:
            words.append(''.join(letters))

    if not words:
        raise MorseError("No Morse code found in the input.")

    return ' '.join(words)


def looks_like_morse(text):
    """
    Guess whether text is Morse code rather than English.

    Used to pick a direction automatically so the user can press one button
    instead of choosing between two.
    """
    stripped = text.strip()
    if not stripped:
        return False
    return set(stripped) <= set('.-/| \t\n')


def translate(text):
    """
    Translate in whichever direction fits the input.

    Returns a (result, direction) pair where direction is either
    'English to Morse' or 'Morse to English'.
    """
    if looks_like_morse(text):
        return decode(text), 'Morse to English'
    return encode(text), 'English to Morse'
