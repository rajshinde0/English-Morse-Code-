"""
Storage for past translations.

Each translation is kept as a record with a timestamp, the direction it was
translated in, the input and the output. Records live in a JSON file, which
means they can be sorted, searched and exported - none of which is practical
when history is a plain block of text.
"""

import json
import os
import csv
from datetime import datetime

HISTORY_FILE = 'history.json'
MAX_ENTRIES = 500


class History:
    """A list of translation records backed by a JSON file."""

    def __init__(self, path=HISTORY_FILE):
        self.path = path
        self.entries = []
        self.load()

    def load(self):
        """
        Read records from disk.

        A missing or corrupt file is treated as an empty history rather than
        an error, so a damaged file can never stop the application starting.
        """
        if not os.path.exists(self.path):
            self.entries = []
            return

        try:
            with open(self.path, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
            self.entries = data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            self.entries = []

    def save(self):
        """Write records to disk. Returns None on success or an error message."""
        try:
            with open(self.path, 'w', encoding='utf-8') as handle:
                json.dump(self.entries, handle, indent=2, ensure_ascii=False)
            return None
        except OSError as error:
            return str(error)

    def add(self, direction, source, result):
        """Record one translation, newest first, and save."""
        self.entries.insert(0, {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'direction': direction,
            'input': source,
            'output': result,
        })
        # Keep the file from growing without limit.
        del self.entries[MAX_ENTRIES:]
        return self.save()

    def clear(self):
        """Remove every record."""
        self.entries = []
        return self.save()

    def search(self, term):
        """Return records whose input or output contains term, ignoring case."""
        if not term or not term.strip():
            return list(self.entries)
        needle = term.strip().lower()
        return [
            entry for entry in self.entries
            if needle in entry.get('input', '').lower()
            or needle in entry.get('output', '').lower()
        ]

    def export_csv(self, path):
        """Write the history to a CSV file. Returns None or an error message."""
        try:
            with open(path, 'w', newline='', encoding='utf-8') as handle:
                writer = csv.DictWriter(
                    handle, fieldnames=['time', 'direction', 'input', 'output']
                )
                writer.writeheader()
                writer.writerows(self.entries)
            return None
        except OSError as error:
            return str(error)

    def __len__(self):
        return len(self.entries)
