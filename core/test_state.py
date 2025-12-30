from enum import Enum


class TestState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"