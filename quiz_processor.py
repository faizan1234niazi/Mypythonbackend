from transformers import pipeline
import re


class QuizProcessor:

    def __init__(self):
        print("✅ Quiz model loaded (PRO LEVEL)")
        self.model = pipeline(
            "text2text-generation",
            model="google/flan-t5-base"
        )

    def is_valid_question(self, q):
        q_lower = q.lower()

        # ❌ Reject weak/generic patterns
        bad_patterns = [
            "what is this",
            "what is the purpose",
            "what is the main idea",
            "what is the title",
            "which of the following",
            "explain this",
            "define",
        ]

        if any(p in q_lower for p in bad_patterns):
            return False

        # ❌ Too short = meaningless
        if len(q) < 25:
            return False

        return True

    def clean_question(self, text):
        text = text.replace("\n", " ").strip()

        # Remove numbering like "1." "Q:"
        text = re.sub(r"^\d+[\.\)]\s*", "", text)
        text = re.sub(r"^Q[:\-]\s*", "", text)

        return text

    def generate_questions(self, text, num=5, difficulty="medium"):

        # 🎯 STRONG INTERVIEW PROMPT
        difficulty_map = {
            "easy": "basic understanding but still meaningful",
            "medium": "conceptual, analytical, and reasoning-based",
            "hard": "advanced interview-level, requiring deep understanding and critical thinking"
        }

        level = difficulty_map.get(
            difficulty,
            "conceptual, analytical, and reasoning-based"
        )

        questions = []
        seen = set()
        attempts = 0

        while len(questions) < num and attempts < num * 5:
            attempts += 1

            prompt = f"""
You are a senior interviewer at a top tech/company.

Generate ONE {level} question based STRICTLY on the content below.

STRICT RULES:
- Question must test understanding, reasoning, or application
- Avoid generic or surface-level questions
- Avoid repetition
- Do NOT ask obvious questions
- Focus on "why", "how", "impact", "trade-offs"
- Make it sound like a real interview question

Content:
{text[:1200]}
"""

            output = self.model(
                prompt,
                max_new_tokens=80,
                temperature=0.9,
                do_sample=True
            )[0]["generated_text"]

            question = self.clean_question(output)

            # 🔐 Uniqueness check
            key = " ".join(question.lower().split()[:7])

            if (
                key not in seen
                and self.is_valid_question(question)
            ):
                seen.add(key)
                questions.append(question)

        # 🔥 SMART FALLBACK (STILL INTERVIEW LEVEL)
        fallback = [
            "How would you apply the key concept discussed in a real-world scenario, and what challenges might arise?",
            "What are the trade-offs or limitations associated with the approach described in the content?",
            "How does this concept compare with alternative approaches in terms of efficiency or impact?",
            "What assumptions does this approach rely on, and how would you validate them?",
            "How would you improve or optimize the solution presented in the content?"
        ]

        for f in fallback:
            if len(questions) < num:
                questions.append(f)

        return questions[:num]