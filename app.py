from flask import Flask, request, jsonify
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

from youtube_processor import YouTubeProcessor
from summary_processor import SummaryProcessor
from quiz_processor import QuizProcessor


app = Flask(__name__)
CORS(app)


# Load processors once when server starts
print("🚀 Loading processors...", flush=True)
yt = YouTubeProcessor()
sp = SummaryProcessor()
qp = QuizProcessor()
print("✅ All processors loaded successfully", flush=True)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "status": "running",
        "message": "SmartLearn API is live on Hugging Face"
    })


@app.route("/api/process", methods=["POST"])
def process():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid or missing JSON body"
            }), 400

        difficulty = data.get("difficulty", "medium")
        num_questions = int(data.get("num_questions", 5))
        language = data.get("language", "en")
        url = data.get("youtube_url")

        if not url:
            return jsonify({
                "success": False,
                "error": "No YouTube URL provided"
            }), 400

        print(f"🎥 Processing URL: {url}", flush=True)
        print(f"📌 Difficulty: {difficulty}", flush=True)
        print(f"📌 Questions: {num_questions}", flush=True)
        print(f"📌 Language: {language}", flush=True)

        # Get transcript using transcript API or Whisper fallback
        text = yt.get_best_transcript(url)

        if not text or len(text.strip()) < 20:
            return jsonify({
                "success": False,
                "error": "Could not extract enough text from the video"
            }), 400

        # Process summary and quiz
        with ThreadPoolExecutor(max_workers=2) as executor:
            summary_future = executor.submit(sp.summarize, text, language)
            questions_future = executor.submit(
                qp.generate_questions,
                text,
                num_questions,
                difficulty
            )

            summary = summary_future.result()
            questions = questions_future.result()

        video_info = yt.get_video_details(url)

        return jsonify({
            "success": True,
            "summary": summary,
            "questions": questions,
            "video": video_info
        }), 200

    except ValueError:
        return jsonify({
            "success": False,
            "error": "num_questions must be a valid number"
        }), 400

    except Exception as e:
        print(f"❌ ERROR: {str(e)}", flush=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    print("🚀 Server running on http://0.0.0.0:7860", flush=True)
    app.run(host="0.0.0.0", port=7860, debug=False)
