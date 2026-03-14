import string
import time
import threading
import itertools


class BruteForceEngine:
    """
    Simulates a brute force attack by iterating through character combinations.
    Runs in a background thread; calls progress_callback and done_callback.
    """

    CHARSET = string.ascii_lowercase + string.digits

    def __init__(self, target: str, progress_callback, done_callback, max_length=6):
        self.target = target
        self.progress_callback = progress_callback
        self.done_callback = done_callback
        self.max_length = max_length
        self._stop_event = threading.Event()
        self._thread = None
        self._report_interval_seconds = 0.05

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _run(self):
        target_lower = self.target.lower()
        attempts = 0
        start_time = time.monotonic()
        found = False
        stopped = False
        current_guess = ""
        last_report_time = start_time

        # Count total combinations up to max_length for progress calculation
        total = sum(len(self.CHARSET) ** l for l in range(1, self.max_length + 1))

        for length in range(1, self.max_length + 1):
            if self._stop_event.is_set():
                stopped = True
                break
            for guess in self._generate(length):
                if self._stop_event.is_set():
                    stopped = True
                    break
                attempts += 1
                current_guess = guess
                now = time.monotonic()
                elapsed = now - start_time
                speed = attempts / elapsed if elapsed > 0 else 0
                progress = min(int((attempts / total) * 100), 99) if total else 0

                should_report = (
                    (now - last_report_time) >= self._report_interval_seconds
                    or guess == target_lower
                )
                if should_report:
                    last_report_time = now
                    self.progress_callback(
                        current=guess,
                        attempts=attempts,
                        elapsed=elapsed,
                        speed=speed,
                        progress=progress,
                    )

                if guess == target_lower:
                    found = True
                    self._stop_event.set()
                    break
            if found:
                break

        elapsed = time.monotonic() - start_time
        speed = attempts / elapsed if elapsed > 0 else 0
        final_progress = 100 if found else min(int((attempts / total) * 100), 99) if total else 0
        self.progress_callback(
            current=current_guess,
            attempts=attempts,
            elapsed=elapsed,
            speed=speed,
            progress=final_progress,
        )
        self.done_callback(
            found=found,
            stopped=stopped and not found,
            attempts=attempts,
            elapsed=elapsed,
            speed=speed,
        )

    def _generate(self, length: int):
        """Yield all combinations of CHARSET of given length iteratively."""
        for combo in itertools.product(self.CHARSET, repeat=length):
            if self._stop_event.is_set():
                return
            yield "".join(combo)
