# Fix import path
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))



# Standard imports
from flask import Flask, render_template, request,jsonify,make_response
from core.session_controller import TypingSession
from core.database import DatabaseManager
import time
import random


# Flask app setup
app = Flask(__name__)

# Utility: get random typing text
def get_random_text():
    text_file = ROOT_DIR / "texts" / "medium.txt"
    with open(text_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return random.choice(lines)


# Main route: typing test
@app.route("/")
def index():
    reference_text = get_random_text()

    response = make_response(
        render_template("index.html", reference_text=reference_text)
    )

    # Store reference text for /submit
    response.set_cookie("reference_text", reference_text)

    return response

# submit route (AJAX / fetch)
@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()

    typed_text = data.get("typed_text", "")
    elapsed_time = float(data.get("elapsed_time", 0))

    reference_text = request.cookies.get("reference_text")
    if not reference_text:
        return "Reference text missing", 400

    # Create typing session
    session = TypingSession()
    session.input_tracker.typed_buffer = typed_text
    session.finish()

    # Evaluate
    result = session.evaluate(
        reference_text=reference_text,
        elapsed_time=elapsed_time
    )

    return render_template("result.html", result=result)

# History & progress page
@app.route("/history")
def history():
    db = DatabaseManager()

    sessions = db.get_all_sessions()
    avg_net_wpm, avg_accuracy, total_sessions = db.get_summary_stats()

    # -------------------------------
    # CONFIG
    # -------------------------------
    MAX_POINTS = 25   # show last 25 attempts only

    # Keep only recent attempts
    sessions = sessions[-MAX_POINTS:]

    # -------------------------------
    # Chart data (attempt-based)
    # -------------------------------
    labels = list(range(1, len(sessions) + 1))

    net_wpm_data = [
        round(float(row[3] or 0), 1)
        for row in sessions
    ]

    accuracy_data = [
        round(max(0, float(row[4] or 0)), 1)
        for row in sessions
    ]

    # -------------------------------
    # Trend (compare first vs last)
    # -------------------------------
    trend = "↑" if len(net_wpm_data) > 1 and net_wpm_data[-1] >= net_wpm_data[0] else "↓"

    return render_template(
        "history.html",
        sessions=sessions,
        total_sessions=total_sessions or 0,
        avg_net_wpm=round(avg_net_wpm or 0, 1),
        avg_accuracy=round(avg_accuracy or 0, 1),
        trend=trend,
        labels=labels,
        net_wpm_data=net_wpm_data,
        accuracy_data=accuracy_data
    )

# -------------------------------
# Run server (development only)
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
