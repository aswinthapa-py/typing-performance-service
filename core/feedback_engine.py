class FeedbackEngine:
    def __init__(self, metrics: dict, error_data: dict):
        self.metrics = metrics
        self.error_data = error_data

    def generate_feedback(self):
        """
        Returns structured feedback:
        - speed_feedback
        - accuracy_feedback
        - behavior_insights
        - recommendations
        """
        feedback = {
            "speed_feedback": "",
            "accuracy_feedback": "",
            "behavior_insights": [],
            "recommendations": []
        }

        net_wpm=self.metrics.get("net_wpm",0)
        accuracy = self.metrics.get("accuracy",0)
        correction_ratio=self.metrics.get("correction_ratio",0)

        # ---------- Speed Feedback ----------
        if net_wpm < 25:
            feedback["speed_feedback"] = "Your typing speed is at a beginner level. Focus on accuracy before increasing speed."

        elif net_wpm < 40:
            feedback["speed_feedback"] = "Your typing speed is developing. Consistent practice will help you improve."

        elif net_wpm < 60:
            feedback["speed_feedback"] = "You have a good typing speed. Focus on maintaining accuracy."

        else:
            feedback["speed_feedback"] = "You have an excellent typing speed. Work on endurance and consistency."
        
        # ---------- Accuracy Feedback ----------
        
        if accuracy >= 97:
            feedback["accuracy_feedback"] = "Excellent accuracy. You make very few mistakes."
        elif accuracy >= 94:
            feedback["accuracy_feedback"] = "Accuracy is acceptable, but small improvements will help."
        else:
            feedback["accuracy_feedback"] = "Accuracy needs improvement. Slow down and focus on correct keystrokes."
        
        # ---------- General Behavior ----------
        
        if correction_ratio > 0.6:
            feedback["behavior_insights"].append(
                "You frequently correct mistakes. This suggests careful typing but possible hesitation."
            )
        elif correction_ratio < 0.3 and accuracy < 94:
            feedback["behavior_insights"].append(
                "You tend to rush and leave mistakes uncorrected."
            )
        # ---------- Error Analysis ----------
        
        error_list=self.error_data.get("error_list", [])
        
        error_type_count = {
            "substitution": 0,
            "omission": 0,
            "insertion": 0
        }
        for error in error_list:
            error_type=error.get("error_type")
            if error_type in error_type_count:
                error_type_count[error_type]+=1

        
        dominant_error_type=None
        if any(error_type_count.values()):
            dominant_error_type=max(
                error_type_count,
                key=lambda k: error_type_count[k]
            )
        
        # ---------- Category-aware Feedback ----------
        if dominant_error_type == "substitution":
            feedback["behavior_insights"].append(
                "You often replace letters with incorrect ones. Focus on accuracy over speed."
            )
        elif dominant_error_type == "omission":
            feedback["behavior_insights"].append(
                "You tend to skip characters while typing. Slow down and ensure each keypress is deliberate."
            )
        elif dominant_error_type == "insertion":
            feedback["behavior_insights"].append(
                "You frequently add extra characters. Try to maintain controlled typing speed."
            )
        
        #-------Character-Level Insights--------
        error_char_count={}
        for error in error_list:
            char = error.get("typed")
            if char:
                error_char_count[char] = error_char_count.get(char, 0) + 1
        
        if error_char_count:
            most_common_char = max(error_char_count, key=error_char_count.get)
            feedback["behavior_insights"].append(
                f"You frequently make mistakes on the character '{most_common_char}'."
            )

        # ---------Recommendations ----------
        
        if accuracy < 94:
            feedback["recommendations"].append(
                "Practice slow typing sessions focusing on accuracy."
            )

        if net_wpm < 40:
            feedback["recommendations"].append(
                "Practice daily for 10–15 minutes using real-world text."
            )

        if not feedback["recommendations"]:
            feedback["recommendations"].append(
                "Maintain your current practice routine to sustain performance."
            )
        
        return feedback

