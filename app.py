from flask import Flask, request, jsonify
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

from youtube_processor import YouTubeProcessor
from summary_processor import SummaryProcessor
from quiz_processor import QuizProcessor

app = Flask(__name__)
CORS(app)

yt = YouTubeProcessor()
sp = SummaryProcessor()
qp = QuizProcessor()


@app.route("/api/process", methods=["POST"])
def process():
    try:
        difficulty = request.json.get("difficulty", "medium")
        num_questions = int(request.json.get("num_questions", 5))
        language = request.json.get("language", "en")
        url = request.json.get("youtube_url")

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        print("🎥 Processing:", url)

        # 🔥 ALWAYS GET TEXT (NO FAIL SYSTEM)
        text = yt.get_best_transcript(url)

        # ⚡ PARALLEL PROCESS
        with ThreadPoolExecutor() as executor:
            summary = executor.submit(sp.summarize, text, language).result()
            questions = executor.submit(
                qp.generate_questions,
                text,
                num_questions,
                difficulty
            ).result()

        video_info = yt.get_video_details(url)

        return jsonify({
            "success": True,
            "summary": summary,
            "questions": questions,
            "video": video_info
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    print("🚀 Server running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)