import time
import threading
import os


WORDLIST_PATH = os.path.join(os.path.dirname(__file__), "wordlists", "common_passwords.txt")


class DictionaryAttackEngine:
    """
    Simulates a dictionary attack using a wordlist file.
    Runs in a background thread.
    """

    def __init__(self, target: str, progress_callback, done_callback):
        self.target = target
        self.progress_callback = progress_callback
        self.done_callback = done_callback
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _load_wordlist(self):
        words = []
        if os.path.exists(WORDLIST_PATH):
            with open(WORDLIST_PATH, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    w = line.strip()
                    if w:
                        words.append(w)
        return words

    def _run(self):
        target_lower = self.target.lower()
        words = self._load_wordlist()
        total = len(words)
        attempts = 0
        start_time = time.time()
        found = False
        current_guess = ""

        for i, word in enumerate(words):
            if self._stop_event.is_set():
                break
            attempts += 1
            current_guess = word
            elapsed = time.time() - start_time
            speed = attempts / elapsed if elapsed > 0 else 0
            progress = int((i / total) * 100) if total > 0 else 0

            if attempts % 100 == 0 or word == target_lower:
                self.progress_callback(
                    current=word,
                    attempts=attempts,
                    elapsed=elapsed,
                    speed=speed,
                    progress=progress,
                )

            if word == target_lower:
                found = True
                self._stop_event.set()
                break

        elapsed = time.time() - start_time
        speed = attempts / elapsed if elapsed > 0 else 0
        self.progress_callback(
            current=current_guess,
            attempts=attempts,
            elapsed=elapsed,
            speed=speed,
            progress=100 if found else 100,
        )
        self.done_callback(
            found=found,
            attempts=attempts,
            elapsed=elapsed,
            speed=speed,
        )
