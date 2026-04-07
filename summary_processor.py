from transformers import pipeline
from deep_translator import GoogleTranslator


class SummaryProcessor:

    def __init__(self):
        self.model = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6"
        )

    def summarize(self, text, lang="en"):

        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        results = []

        for chunk in chunks:
            if len(chunk) < 50:
                continue

            summary = self.model(chunk, max_new_tokens=150)[0]["summary_text"]
            results.append(summary)

        combined = " ".join(results)

        # 🌐 TRANSLATE OUTPUT
        if lang != "en":
            try:
                combined = GoogleTranslator(
                    source='auto',
                    target=lang
                ).translate(combined)
            except:
                pass

        return f"""
# 📌 Summary

{combined}

## 🎯 Key Insights
- Easy understanding
- Practical application
"""