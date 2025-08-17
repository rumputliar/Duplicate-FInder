# utils.py
import time
import threading
import itertools
import sys

class ProgressSpinner:
    """Manajer konteks untuk menampilkan spinner di terminal."""
    def __init__(self, message="Memproses..."):
        self.spinner = itertools.cycle(['-', '\\', '|', '/'])
        self.message = message
        self.running = False
        self.spinner_thread = None

    def _spin(self):
        while self.running:
            spinner_char = next(self.spinner)
            sys.stdout.write(f'\r{self.message} {spinner_char}')
            sys.stdout.flush()
            time.sleep(0.1)
        # Hapus baris spinner setelah selesai
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()

    def __enter__(self):
        self.running = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.running = False
        self.spinner_thread.join()