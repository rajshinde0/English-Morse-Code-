# Morse Code Translator

A desktop application that translates between English and International Morse
code, plays the result as sound, and keeps a searchable history of everything
you have translated.

Built with Python and Tkinter for a Semester 2 Python course project.

## What it does

- **Translates both ways.** Type English to get Morse code, or type Morse code
  to get English back. You do not choose a direction - the app detects which
  one you meant from what you type.
- **Plays real Morse audio.** The output is turned into sound using proper
  Morse timing (a dash lasts three times as long as a dot, with the standard
  gaps between symbols, letters and words). A speed slider sets the pace in
  words per minute, and you can save the sound as a `.wav` file.
- **Remembers your history.** Every translation is saved with a timestamp and
  shown in a table you can search. Double-click any row to load it back in.
  History can be exported to CSV.

## Running it

```
python app.py
```

That is all - the project uses only the Python standard library, so there is
nothing to install first. (On Linux, Tkinter may need `sudo apt-get install
python3-tk`.)

## How the code is organised

The project is split so that the translation logic is separate from the
interface, which makes it easy to read and to test.

| File             | Responsibility                                        |
|------------------|-------------------------------------------------------|
| `app.py`         | The window and everything the user clicks. Run this.  |
| `morse.py`       | Encoding and decoding. Pure functions, no GUI.        |
| `audio.py`       | Turns Morse code into sound and plays it.             |
| `history.py`     | Saves, loads, searches and exports past translations. |
| `test_morse.py`  | Automated tests for the logic above.                  |
| `history.json`   | Saved history (created automatically on first use).   |

Because `morse.py` and `audio.py` do not depend on the interface, they can be
used on their own:

```python
>>> import morse
>>> morse.encode("HELLO WORLD")
'.... . .-.. .-.. --- / .-- --- .-. .-.. -..'
>>> morse.decode('... --- ...')
'SOS'
```

## Running the tests

```
python test_morse.py
```

This checks encoding, decoding, round-tripping text through both, direction
detection, and the audio timing ratios.

## Using the app

1. Type into the **Input** box.
   - English, e.g. `HELLO WORLD`
   - or Morse code, e.g. `.... . .-.. .-.. --- / .-- --- .-. .-.. -..`
     (spaces between letters, ` / ` between words).
2. Press **Translate** (or just press Enter).
3. The result appears in **Output** and plays as sound. Use **Play** to hear it
   again, **Save .wav** to keep it, or **Copy** to copy the text.
4. Tick **Mute** to translate silently, or drag **Speed** to change how fast
   the audio plays.

Every translation is added to the **History** table at the bottom. Type in the
**Search** box to filter it, double-click a row to reload that text, or use
**Export CSV** / **Clear history**.

## Notes

- Supported characters: A-Z, 0-9, and common punctuation
  (`. , ? ' ! / ( ) & : ; = + - _ " $ @`). Unsupported characters are skipped
  when encoding; unrecognised Morse sequences show up as `#` when decoding, so
  you can see exactly where a problem is.
- Audio uses `winsound` on Windows (built in). On other systems it falls back
  to `pygame` if installed; without it, translation still works silently.
