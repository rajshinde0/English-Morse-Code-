"""
Tests for the translation logic.

Run them with:

    python test_morse.py

These only touch morse.py, which is possible because the translation code
does not depend on the interface, the audio or the history file.
"""

import unittest

import morse
import audio


class TestEncode(unittest.TestCase):

    def test_single_word(self):
        self.assertEqual(morse.encode('SOS'), '... --- ...')

    def test_sentence_uses_slash_between_words(self):
        self.assertEqual(
            morse.encode('HELLO WORLD'),
            '.... . .-.. .-.. --- / .-- --- .-. .-.. -..',
        )

    def test_is_case_insensitive(self):
        self.assertEqual(morse.encode('sos'), morse.encode('SOS'))

    def test_digits_and_punctuation(self):
        self.assertEqual(morse.encode('7?'), '--... ..--..')

    def test_extra_whitespace_is_ignored(self):
        self.assertEqual(morse.encode('  HI   YOU  '), morse.encode('HI YOU'))

    def test_unsupported_characters_are_skipped(self):
        self.assertEqual(morse.encode('A~B'), '.- -...')

    def test_empty_input_is_rejected(self):
        with self.assertRaises(morse.MorseError):
            morse.encode('   ')

    def test_wholly_unsupported_input_is_rejected(self):
        with self.assertRaises(morse.MorseError):
            morse.encode('~~~')


class TestDecode(unittest.TestCase):

    def test_single_word(self):
        self.assertEqual(morse.decode('... --- ...'), 'SOS')

    def test_sentence(self):
        self.assertEqual(
            morse.decode('.... . .-.. .-.. --- / .-- --- .-. .-.. -..'),
            'HELLO WORLD',
        )

    def test_slash_without_surrounding_spaces(self):
        self.assertEqual(morse.decode('.../---'), 'S O')

    def test_unknown_sequence_becomes_hash(self):
        self.assertEqual(morse.decode('.- ........'), 'A#')

    def test_letters_are_rejected(self):
        with self.assertRaises(morse.MorseError):
            morse.decode('hello')

    def test_empty_input_is_rejected(self):
        with self.assertRaises(morse.MorseError):
            morse.decode('')


class TestRoundTrip(unittest.TestCase):

    def test_text_survives_a_round_trip(self):
        for text in ('SOS', 'HELLO WORLD', 'MEET ME AT 5', 'VIT PYTHON PROJECT'):
            self.assertEqual(morse.decode(morse.encode(text)), text)


class TestDirectionDetection(unittest.TestCase):

    def test_morse_is_recognised(self):
        self.assertTrue(morse.looks_like_morse('... --- ...'))

    def test_english_is_recognised(self):
        self.assertFalse(morse.looks_like_morse('SOS'))

    def test_translate_picks_encoding(self):
        result, direction = morse.translate('SOS')
        self.assertEqual(result, '... --- ...')
        self.assertEqual(direction, 'English to Morse')

    def test_translate_picks_decoding(self):
        result, direction = morse.translate('... --- ...')
        self.assertEqual(result, 'SOS')
        self.assertEqual(direction, 'Morse to English')


class TestAudioTiming(unittest.TestCase):

    def test_dot_length_follows_the_paris_convention(self):
        self.assertAlmostEqual(audio.dot_duration(20), 0.06)

    def test_higher_speed_gives_shorter_dots(self):
        self.assertLess(audio.dot_duration(40), audio.dot_duration(10))

    def test_rendered_audio_is_a_valid_wav_file(self):
        data = audio.render_wav('... --- ...', wpm=20)
        self.assertTrue(data.startswith(b'RIFF'))
        self.assertIn(b'WAVE', data[:16])

    def test_a_dash_lasts_three_times_a_dot(self):
        dot = len(audio.render_wav('.', wpm=20))
        dash = len(audio.render_wav('-', wpm=20))
        header = 44
        self.assertAlmostEqual((dash - header) / (dot - header), 3, places=1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
