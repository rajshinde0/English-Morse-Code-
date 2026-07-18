"""
Morse Code Translator - user interface.

Run this file to start the application:

    python app.py

The translation, audio and history logic all live in their own modules
(morse.py, audio.py, history.py). This file is only concerned with putting
them on screen.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import morse
import audio
from history import History

BACKGROUND = '#f4f6f8'
ACCENT = '#2d6cdf'
TEXT = '#1c2733'
MUTED_TEXT = '#6b7a8c'
OK = '#1f9254'
BAD = '#c0392b'


class TranslatorApp:
    """The main window."""

    def __init__(self, root):
        self.root = root
        self.history = History()
        self.player = audio.Player()
        self.muted = tk.BooleanVar(value=False)
        self.wpm = tk.IntVar(value=audio.DEFAULT_WPM)
        self.last_morse = ''

        root.title('Morse Code Translator')
        root.geometry('760x680')
        root.minsize(640, 600)
        root.configure(bg=BACKGROUND)

        self._build_header()
        self._build_input()
        self._build_controls()
        self._build_output()
        self._build_history()
        self._build_status()

        self.refresh_history()
        self.input_box.focus_set()

        if not self.player.available:
            self.set_status('No sound device found - translation still works.', BAD)

    # ---------------------------------------------------------------- layout

    def _build_header(self):
        header = tk.Frame(self.root, bg=BACKGROUND)
        header.pack(fill=tk.X, padx=20, pady=(18, 6))

        tk.Label(
            header, text='Morse Code Translator', font=('Segoe UI', 20, 'bold'),
            fg=TEXT, bg=BACKGROUND,
        ).pack(anchor='w')

        tk.Label(
            header,
            text='Type English or Morse code - the direction is detected for you.',
            font=('Segoe UI', 10), fg=MUTED_TEXT, bg=BACKGROUND,
        ).pack(anchor='w')

    def _build_input(self):
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(fill=tk.X, padx=20, pady=(10, 0))

        tk.Label(
            frame, text='Input', font=('Segoe UI', 10, 'bold'),
            fg=TEXT, bg=BACKGROUND,
        ).pack(anchor='w')

        self.input_box = tk.Text(
            frame, height=4, font=('Segoe UI', 11), wrap=tk.WORD,
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground='#cbd5e0', highlightcolor=ACCENT,
        )
        self.input_box.pack(fill=tk.X, pady=(4, 0))

        # Enter translates; Shift+Enter inserts a newline.
        self.input_box.bind('<Return>', self._on_return)
        self.input_box.bind('<Shift-Return>', lambda event: None)

    def _build_controls(self):
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(fill=tk.X, padx=20, pady=10)

        self._button(frame, 'Translate', self.translate, ACCENT).pack(side=tk.LEFT)
        self._button(frame, 'Play', self.play_audio, '#5a6b7d').pack(side=tk.LEFT, padx=(8, 0))
        self._button(frame, 'Save .wav', self.save_audio, '#5a6b7d').pack(side=tk.LEFT, padx=(8, 0))
        self._button(frame, 'Clear', self.clear, '#8899aa').pack(side=tk.LEFT, padx=(8, 0))

        tk.Checkbutton(
            frame, text='Mute', variable=self.muted, bg=BACKGROUND, fg=TEXT,
            font=('Segoe UI', 10), activebackground=BACKGROUND,
            selectcolor=BACKGROUND, cursor='hand2',
        ).pack(side=tk.LEFT, padx=(16, 0))

        speed = tk.Frame(frame, bg=BACKGROUND)
        speed.pack(side=tk.RIGHT)
        tk.Label(
            speed, text='Speed', font=('Segoe UI', 10), fg=MUTED_TEXT, bg=BACKGROUND,
        ).pack(side=tk.LEFT)
        tk.Scale(
            speed, from_=5, to=40, orient=tk.HORIZONTAL, variable=self.wpm,
            length=140, bg=BACKGROUND, fg=TEXT, highlightthickness=0,
            troughcolor='#dde3ea', font=('Segoe UI', 8),
        ).pack(side=tk.LEFT)
        tk.Label(
            speed, text='wpm', font=('Segoe UI', 10), fg=MUTED_TEXT, bg=BACKGROUND,
        ).pack(side=tk.LEFT)

    def _build_output(self):
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(fill=tk.X, padx=20)

        row = tk.Frame(frame, bg=BACKGROUND)
        row.pack(fill=tk.X)
        tk.Label(
            row, text='Output', font=('Segoe UI', 10, 'bold'), fg=TEXT, bg=BACKGROUND,
        ).pack(side=tk.LEFT)
        tk.Button(
            row, text='Copy', command=self.copy_output, relief=tk.FLAT,
            font=('Segoe UI', 9), fg=ACCENT, bg=BACKGROUND, cursor='hand2',
            activebackground=BACKGROUND, borderwidth=0,
        ).pack(side=tk.RIGHT)

        self.output_box = tk.Text(
            frame, height=5, font=('Consolas', 12), wrap=tk.WORD,
            relief=tk.FLAT, highlightthickness=1, highlightbackground='#cbd5e0',
            bg='#ffffff', state=tk.DISABLED,
        )
        self.output_box.pack(fill=tk.X, pady=(4, 0))

    def _build_history(self):
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(14, 0))

        row = tk.Frame(frame, bg=BACKGROUND)
        row.pack(fill=tk.X)
        tk.Label(
            row, text='History', font=('Segoe UI', 10, 'bold'), fg=TEXT, bg=BACKGROUND,
        ).pack(side=tk.LEFT)

        tk.Button(
            row, text='Clear history', command=self.clear_history, relief=tk.FLAT,
            font=('Segoe UI', 9), fg=BAD, bg=BACKGROUND, cursor='hand2',
            activebackground=BACKGROUND, borderwidth=0,
        ).pack(side=tk.RIGHT)
        tk.Button(
            row, text='Export CSV', command=self.export_history, relief=tk.FLAT,
            font=('Segoe UI', 9), fg=ACCENT, bg=BACKGROUND, cursor='hand2',
            activebackground=BACKGROUND, borderwidth=0,
        ).pack(side=tk.RIGHT, padx=(0, 12))

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.refresh_history())
        search = tk.Entry(
            row, textvariable=self.search_var, font=('Segoe UI', 9), width=22,
            relief=tk.FLAT, highlightthickness=1, highlightbackground='#cbd5e0',
        )
        search.pack(side=tk.RIGHT, padx=(0, 12))
        tk.Label(
            row, text='Search', font=('Segoe UI', 9), fg=MUTED_TEXT, bg=BACKGROUND,
        ).pack(side=tk.RIGHT, padx=(0, 4))

        columns = ('time', 'direction', 'input', 'output')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)
        for column, heading, width in (
            ('time', 'Time', 130),
            ('direction', 'Direction', 120),
            ('input', 'Input', 180),
            ('output', 'Output', 260),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor='w')

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(6, 0))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(6, 0))

        # Double-clicking a past translation loads it back into the input box.
        self.tree.bind('<Double-1>', self.reuse_entry)

    def _build_status(self):
        self.status = tk.Label(
            self.root, text='', font=('Segoe UI', 10), fg=MUTED_TEXT,
            bg=BACKGROUND, anchor='w',
        )
        self.status.pack(fill=tk.X, padx=20, pady=(8, 14))

    def _button(self, parent, text, command, colour):
        return tk.Button(
            parent, text=text, command=command, bg=colour, fg='white',
            font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor='hand2',
            padx=18, pady=8, activebackground=colour, activeforeground='white',
        )

    # --------------------------------------------------------------- actions

    def _on_return(self, event):
        self.translate()
        return 'break'   # stop Tk inserting the newline as well

    def set_status(self, message, colour=MUTED_TEXT):
        self.status.config(text=message, fg=colour)

    def show_output(self, text):
        self.output_box.config(state=tk.NORMAL)
        self.output_box.delete('1.0', tk.END)
        self.output_box.insert('1.0', text)
        self.output_box.config(state=tk.DISABLED)

    def translate(self):
        source = self.input_box.get('1.0', tk.END).strip()
        if not source:
            self.set_status('Type something to translate first.', BAD)
            return

        try:
            result, direction = morse.translate(source)
        except morse.MorseError as error:
            self.set_status(str(error), BAD)
            return

        self.show_output(result)
        # Remember whichever side of the translation is Morse, so the play
        # and save buttons work in both directions.
        self.last_morse = result if direction == 'English to Morse' else source

        error = self.history.add(direction, source, result)
        if error:
            self.set_status('Translated, but history could not be saved: ' + error, BAD)
        else:
            self.set_status(direction + ' - done.', OK)

        self.refresh_history()

        if not self.muted.get():
            self.play_audio(announce=False)

    def play_audio(self, announce=True):
        if not self.last_morse:
            if announce:
                self.set_status('Translate something before playing it.', BAD)
            return
        if not self.player.available:
            if announce:
                self.set_status('No sound device is available.', BAD)
            return

        try:
            data = audio.render_wav(self.last_morse, wpm=self.wpm.get())
            self.player.play(data)
        except Exception as error:
            self.set_status('Could not play audio: ' + str(error), BAD)

    def save_audio(self):
        if not self.last_morse:
            self.set_status('Translate something before saving it.', BAD)
            return

        path = filedialog.asksaveasfilename(
            defaultextension='.wav',
            filetypes=[('WAV audio', '*.wav')],
            initialfile='morse.wav',
        )
        if not path:
            return

        try:
            audio.save_wav(self.last_morse, path, wpm=self.wpm.get())
            self.set_status('Saved to ' + path, OK)
        except Exception as error:
            messagebox.showerror('Save failed', str(error))

    def copy_output(self):
        text = self.output_box.get('1.0', tk.END).strip()
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.set_status('Output copied to the clipboard.', OK)

    def clear(self):
        self.input_box.delete('1.0', tk.END)
        self.show_output('')
        self.last_morse = ''
        self.player.stop()
        self.set_status('')
        self.input_box.focus_set()

    def refresh_history(self):
        self.tree.delete(*self.tree.get_children())
        for entry in self.history.search(self.search_var.get()):
            self.tree.insert('', tk.END, values=(
                entry.get('time', ''),
                entry.get('direction', ''),
                entry.get('input', ''),
                entry.get('output', ''),
            ))

    def reuse_entry(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], 'values')
        if len(values) < 3:
            return
        self.input_box.delete('1.0', tk.END)
        self.input_box.insert('1.0', values[2])
        self.set_status('Loaded from history - press Translate to run it again.')

    def clear_history(self):
        if not len(self.history):
            self.set_status('There is no history to clear.')
            return
        if not messagebox.askyesno(
            'Clear history',
            'Delete all {} saved translations? This cannot be undone.'.format(
                len(self.history)
            ),
        ):
            return
        error = self.history.clear()
        self.refresh_history()
        self.set_status(error or 'History cleared.', BAD if error else OK)

    def export_history(self):
        if not len(self.history):
            self.set_status('There is no history to export.')
            return

        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV file', '*.csv')],
            initialfile='morse_history.csv',
        )
        if not path:
            return

        error = self.history.export_csv(path)
        self.set_status(error or ('Exported to ' + path), BAD if error else OK)


def main():
    root = tk.Tk()
    TranslatorApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
