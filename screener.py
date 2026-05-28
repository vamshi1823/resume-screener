import json
import os

from groq import Groq

SYSTEM_PROMPT = """You are an expert technical recruiter and resume analyst.
Your job is to analyze how well a candidate's resume matches a job description.

You must respond ONLY with a valid JSON object — no extra text, no markdown, no explanation.

Return exactly this structure:
{
  "match_score": <integer 0-100>,
  "matched_skills": [<list of strings>],
  "missing_skills": [<list of strings>],
  "strong_points": [<list of 2-3 strings>],
  "improvement_suggestions": [<list of 2-3 strings>],
  "verdict": "<one of: Strong Match | Good Match | Partial Match | Weak Match>"
}"""

def screen_resume(job_description: str, resume_text: str) -> dict:
    # Client created here — after API key is set in sidebar
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    user_message = f"""
JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Analyze the match and return the JSON response.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Failed to parse response. Please try again."}
    except Exception as e:
        return {"error": str(e)}