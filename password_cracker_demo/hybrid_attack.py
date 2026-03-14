import time
import threading
import os


WORDLIST_PATH = os.path.join(os.path.dirname(__file__), "wordlists", "common_passwords.txt")

NUMBER_SUFFIXES = [
    "", "1", "12", "123", "1234", "12345", "123456",
    "2020", "2021", "2022", "2023", "2024", "2025", "2026",
    "0", "00", "000", "007", "1!", "123!", "!",
    "99", "01", "02", "11", "22", "33",
]

NUMBER_PREFIXES = ["1", "12", "123", "2024", "2025", "2026", "007"]


class HybridAttackEngine:
    """
    Simulates a hybrid attack: dictionary words combined with number/symbol mutations.
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

    def _generate_variants(self, words):
        for word in words:
            # original
            yield word
            # suffix variants
            for suffix in NUMBER_SUFFIXES:
                yield word + suffix
                yield word.capitalize() + suffix
            # prefix variants
            for prefix in NUMBER_PREFIXES:
                yield prefix + word
            # leet speak basic
            yield word.replace("a", "@").replace("e", "3").replace("o", "0").replace("i", "1")

    def _run(self):
        target_lower = self.target.lower()
        words = self._load_wordlist()
        candidates = list(self._generate_variants(words))
        total = len(candidates)

        attempts = 0
        start_time = time.time()
        found = False
        current_guess = ""

        for i, candidate in enumerate(candidates):
            if self._stop_event.is_set():
                break
            attempts += 1
            current_guess = candidate
            elapsed = time.time() - start_time
            speed = attempts / elapsed if elapsed > 0 else 0
            progress = int((i / total) * 100) if total > 0 else 0

            if attempts % 200 == 0 or candidate.lower() == target_lower:
                self.progress_callback(
                    current=candidate,
                    attempts=attempts,
                    elapsed=elapsed,
                    speed=speed,
                    progress=progress,
                )

            if candidate.lower() == target_lower:
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
            progress=100,
        )
        self.done_callback(
            found=found,
            attempts=attempts,
            elapsed=elapsed,
            speed=speed,
        )
