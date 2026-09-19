from google import genai
from backend.config import GEMINI_API_KEY, GEMINI_MODEL

def generate_narrative(structured_result):
    if not GEMINI_API_KEY:
        return None
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f'''
You are an environmental science communication assistant.
Rewrite the supplied assessment clearly.
Do not invent facts, percentages, studies or sources.
Keep uncertainty explicit and explain interactions among multiple environmental variables.

STRUCTURED ASSESSMENT:
{structured_result}
'''
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text
