from datetime import datetime
from database import init_db, insert_log, fetch_logs, clear_logs


class AttackLogger:
    def __init__(self):
        init_db()

    def log(self, password_length: int, attack_type: str, attempts: int,
            time_taken: float, result: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_log(timestamp, password_length, attack_type, attempts, time_taken, result)

    def get_recent(self, limit=50):
        return fetch_logs(limit)

    def clear(self):
        clear_logs()
