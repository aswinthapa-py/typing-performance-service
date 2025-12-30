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
import uuid


# Flask app setup
app = Flask(__name__)

# Utility: get random typing text
def get_random_text():
    text_files = ["short.txt", "medium.txt", "long.txt", "paragraphs.txt"]
    chosen = random.choice(text_files)
    path = ROOT_DIR / "texts" / chosen

    with open(path, "r", encoding="utf-8") as f:
        blocks = [
            block.strip()
            for block in f.read().split("\n\n")
            if block.strip()
        ]

    return random.choice(blocks)


# Main route: typing test
@app.route("/")
def index():
    
    user_id=request.cookies.get("user_id")

    if not user_id:
        user_id=str(uuid.uuid4())
    reference_text = get_random_text()

    response = make_response(
        render_template("index.html", reference_text=reference_text)
    )

    # Store reference text for /submit
    response.set_cookie("reference_text", reference_text)
    response.set_cookie("user_id",user_id,httponly=True)

    return response

# submit route (AJAX / fetch)
@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()

    user_id = request.cookies.get("user_id")
    if not user_id:
        return "User not identified",400
    
    typed_text = data.get("typed_text", "")
    elapsed_time = float(data.get("elapsed_time", 0))
    wpm_samples=data.get("wpm_samples",[])

    reference_text = request.cookies.get("reference_text")
    if not reference_text:
        return "Reference text missing", 400

    session = TypingSession()
    session.input_tracker.typed_buffer = typed_text
    session.finish()

    result = session.evaluate(
        reference_text=reference_text,
        elapsed_time=elapsed_time,
        wpm_samples=wpm_samples,
        user_id=user_id
    )

    return render_template("result.html", result=result)

# History & progress page
@app.route("/history")
def history():
    user_id=request.cookies.get("user_id")

    db = DatabaseManager()

    sessions = db.get_sessions_by_user(user_id)

    total_sessions= len(sessions)
    avg_net_wpm = (
        sum(row[3] for row in sessions) / total_sessions
        if total_sessions else 0
    )
    avg_accuracy = (
        sum(row[4] for row in sessions) / total_sessions
        if total_sessions else 0
    )

    

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
    if len(net_wpm_data) <2:
        trend="-"
    else:
        trend = "↑" if net_wpm_data[-1] >= net_wpm_data[0] else "↓"

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
