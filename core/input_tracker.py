class InputTracker:
    def __init__(self):
        self.typed_buffer = ""
        self.keystroke_log = []

    def insert_char(self, char: str, timestamp: float, position: int):
        self.typed_buffer += char
        self.keystroke_log.append({
            "action": "INSERT",
            "char": char,
            "time": timestamp,
            "position": position
        })

    def backspace(self, timestamp: float):
        if self.typed_buffer:
            self.typed_buffer = self.typed_buffer[:-1]
            self.keystroke_log.append({
                "action": "BACKSPACE",
                "char": None,
                "time": timestamp,
                "position": len(self.typed_buffer)
            })
