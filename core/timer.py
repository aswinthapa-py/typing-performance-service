import time


class TestTimer:
    def __init__(self, duration_seconds: int):
        self.duration_seconds = duration_seconds
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def is_time_up(self) -> bool:
        return self.elapsed() >= self.duration_seconds
