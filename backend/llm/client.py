import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def query_llm(system_prompt: str, user_prompt: str = "Please provide the guidance.") -> str:
    """
    Sends the prompts to Google Gemini (Flash) and returns the text response.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt
        )

        response = model.generate_content(user_prompt)
        
        return response.text.strip()
    
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I am unable to generate guidance right now."
