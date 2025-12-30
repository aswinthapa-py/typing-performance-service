from core.test_state import TestState
from core.timer import TestTimer
from core.input_tracker import InputTracker
from core.error_detector import ErrorDetector
from core.metrics import MetricsCalculator
from core.feedback_engine import FeedbackEngine
from core.database import DatabaseManager
from datetime import datetime


class TypingSession:
    def __init__(self, duration_seconds: float | None=None):
        
        self.state = TestState.IDLE
        self.timer = TestTimer(duration_seconds)
        self.input_tracker = InputTracker()
        self.db=DatabaseManager()

    def start_if_needed(self):
        if self.state == TestState.IDLE:
            self.state = TestState.RUNNING
            self.timer.start()
    def finalize_if_time_up(self):
        if self.state == TestState.RUNNING and self.timer.is_time_up():
            self.state = TestState.FINISHED

    def handle_char_input(self, char: str):
        if self.state == TestState.FINISHED:
            return

        self.start_if_needed()

        timestamp = self.timer.elapsed()
        position = len(self.input_tracker.typed_buffer)

        self.input_tracker.insert_char(char, timestamp, position)

        if self.timer.is_time_up():
            self.state = TestState.FINISHED

    def handle_backspace(self):
        if self.state != TestState.RUNNING:
            return

        timestamp = self.timer.elapsed()
        self.input_tracker.backspace(timestamp)

        if self.timer.is_time_up():
            self.state = TestState.FINISHED
    
    def finish(self):
        self.state=TestState.FINISHED

    def evaluate(self, reference_text: str, elapsed_time: float=None):
        if self.state != TestState.FINISHED:
            raise RuntimeError("Session is not finished yet")

        detector = ErrorDetector(
            reference_text=reference_text,
            typed_text=self.input_tracker.typed_buffer
        )
        error_list, uncorrected_errors = detector.detect_errors()

        calculator = MetricsCalculator(
            typed_text=self.input_tracker.typed_buffer,
            time_seconds = elapsed_time if elapsed_time is not None else self.timer.elapsed(),
            uncorrected_errors=uncorrected_errors,
            corrected_errors=0
        )
        metrics = calculator.calculate()

        error_data = {
            "error_list": error_list,
            "uncorrected_errors": uncorrected_errors
        }

        feedback_engine = FeedbackEngine(metrics=metrics, error_data=error_data)
        feedback = feedback_engine.generate_feedback()

        # Save session to database
        self.db.save_session(
            session_date=datetime.now().isoformat(),
            gross_wpm=metrics["gross_wpm"],
            net_wpm=metrics["net_wpm"],
            accuracy=metrics["accuracy"]
        )

        return {
            "typed_text": self.input_tracker.typed_buffer,
            "errors": error_list,
            "metrics": metrics,
            "feedback": feedback
        }
