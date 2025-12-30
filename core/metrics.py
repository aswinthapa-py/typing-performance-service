class MetricsCalculator:
    def __init__(self, typed_text: str, time_seconds: float, uncorrected_errors: int, corrected_errors: int):
        self.typed_text = typed_text
        self.time_seconds = time_seconds
        self.uncorrected_errors = uncorrected_errors
        self.corrected_errors = corrected_errors

    def calculate(self):
        """
        Will return:
        - gross_wpm
        - net_wpm
        - accuracy
        - error_density
        - correction_ratio
        """
        if self.time_seconds <=0:
            raise ValueError("Time must be greater than zero")
        
        time_minutes = self.time_seconds / 60
        total_chars = len(self.typed_text)

        if total_chars ==0:
            return {
                "gross_wpm": 0.0,
                "net_wpm": 0.0,
                "accuracy": 0.0,
                "error_density": 0.0,
                "correction_ratio": 0.0
            }
        words_typed = total_chars / 5
        gross_wpm = words_typed / time_minutes

        accuracy = ((total_chars - self.uncorrected_errors) / total_chars) * 100
        accuracy=max(0.0, min(accuracy,100.0))

        net_wpm= gross_wpm - (self.uncorrected_errors / time_minutes) 
        if net_wpm < 0:
            net_wpm=0.0
        
        error_density  = (self.uncorrected_errors / total_chars) * 100

        total_errors = self.corrected_errors + self.uncorrected_errors
        if total_errors == 0:
            correction_ratio = 0.0
        else:
            correction_ratio = self.corrected_errors / total_errors
        
        return {
            "gross_wpm": gross_wpm,
            "net_wpm": net_wpm,
            "accuracy": accuracy,
            "error_density": error_density,
            "correction_ratio": correction_ratio
        }



