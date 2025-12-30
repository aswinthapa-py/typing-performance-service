class ErrorDetector:
    def __init__(self, reference_text: str, typed_text: str):
        self.reference_text = reference_text
        self.typed_text = typed_text

    def detect_errors(self):
        """
        Compares typed text with reference text.

        Returns:
            error_list (list): list of error dictionaries
            uncorrected_errors (int): total uncorrected errors
        """
        error_list=[]
        uncorrected_errors=0

        max_length = max(len(self.reference_text), len(self.typed_text))

        for i in range(max_length):
            expected_char= (
                self.reference_text[i] if i < len(self.reference_text) else None
            )
            typed_char=(
                self.typed_text[i] if i < len(self.typed_text) else None
            )
            # Ignore space-related mismatches
            if expected_char == " " or typed_char == " ":
                continue

            # If characters differ, record error
            if expected_char != typed_char:
                uncorrected_errors +=1

                if expected_char is None and typed_char is not None:
                    error_type="insertion"
            
                elif expected_char is not None and typed_char is None:
                    error_type="omission"
                
                else:
                    error_type="substitution"


                error_list.append(
                {
                    "position":i,
                    "expected":expected_char,
                    "typed":typed_char,
                    "error_type":"uncorrected"
                }
            )
        return error_list, uncorrected_errors

