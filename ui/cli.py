import time
from core.session_controller import TypingSession
from core.database import DatabaseManager
from datetime import datetime
import random
from pathlib import Path


class CLIMenu():
    def show_menu(self):
        print("\n=== Typing Performance Service ===")
        print("1. Start typing test")
        print("2. View typing history")
        print("3. Exit")
    
    def get_choice(self):
        choice= input("Choose an option: ")
        return choice.strip()
    
    def start_typing_test(self):
        print("\nChoose difficulty level:")
        print("1. Short")
        print("2. Medium")
        print("3. Long")

        choice=input("Enter choice (1-3): ").strip()

        reference_text=self.get_text_by_difficulty(choice)

        print("\n--- Typing Test ---")
        print("Type the following text exactly as shown:")
        print("\n", reference_text)
        print("\nPress Enter when you are ready to start...")
        input() # wait for user to be ready

        session= TypingSession(duration_seconds=15)
        start_time= time.time()

        print("\nStart typing below:\n")
        typed_text=input()

        elapsed_time=time.time() - start_time

        for ch in typed_text:
            session.handle_char_input(ch)

        session.finish()
        
        result = session.evaluate(reference_text, elapsed_time=elapsed_time)

        print("\n--- Result ---")
        print("Time Taken:",round(elapsed_time,2),"seconds")

        print("\nMetrices:")
        for key,value in result["metrics"].items():
            print(f" {key}: {round(value,2)}")
        
        print("\nFeedback:")
        print(" ",result["feedback"]["speed_feedback"])
        print(" ",result["feedback"]["accuracy_feedback"])

        for insight in result["feedback"]["behavior_insights"]:
            print("-",insight)
        
        print("\nRecommendations:")
        for rec in result["feedback"]["recommendations"]:
            print("-",rec)


    
    def view_history(self):
        db=DatabaseManager()
        sessions= db.get_all_sessions()

        avg_net_wpm, avg_accuracy, total = db.get_summary_stats()

        if not sessions:
            print("\nNo typing history found.\n")
            return
        
        print("\n--- Progress Summary ---")
        print(f"Total Sessions: {total}")
        print(f"Average Net WPM: {avg_net_wpm:.2f}")
        print(f"Average Accuracy: {avg_accuracy:.2f}%")

        if len(sessions) >= 2:
            first_net = sessions[0][3]
            last_net = sessions[-1][3]

            if last_net > first_net:
                trend = "Improving ↑"
            elif last_net < first_net:
                trend = "Declining ↓"
            else:
                trend = "Stable →"

            print(f"Trend: {trend}")

        
        
        print("\n--- Typing History ---")
        print(f"{'No.':<4} {'Date & Time':<20} {'Net WPM':<10} {'Accuracy'}")
        print("-" * 50)

        for idx, session in enumerate(sessions, start=1):
            _, session_date, gross_wpm, net_wpm, accuracy = session

            formatted_date = datetime.fromisoformat(session_date).strftime(
                "%Y-%m-%d %H:%M")
            
            print(
                f"{idx:<4} {formatted_date:<20} {net_wpm:<10.2f} {accuracy:.2f}%")
        input("\nPress Enter to return to menu...")

            
        
    
    def run(self):
        while True:
            self.show_menu()
            choice=self.get_choice()

            if choice == "1":
                self.start_typing_test()
            elif choice == "2":
                self.view_history()
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def get_random_text(self):
        text_file=Path("texts") / "paragraphs.txt"

        if not text_file.exists():
            raise FileNotFoundError("Typing text file not found.")
        
        with open(text_file,"r",encoding="utf-8") as file:
            lines=[line.strip() for line in file if line.strip()]
        
        if not lines:
            raise ValueError("No typing text available.")
        
        return random.choice(lines)
    
    def get_text_by_difficulty(self,level):
        files={
            "1":"short.txt",
            "2":"medium.txt",
            "3":"long.txt"
        }
        filename=files.get(level,"medium.txt")
        text_path=Path("texts") / filename

        if not text_path.exists():
            raise FileNotFoundError(f"{filename} not found.")
        
        with open(text_path,"r",encoding="utf-8") as file:
            lines=[line.strip() for line in file if line.strip()]
        
        return random.choice(lines)

