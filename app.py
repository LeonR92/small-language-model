from config import AI_MODEL, SYSTEM_PROMPT, TEMPERATURE, USER_PROMPT
from utils import talk_to_ai

if __name__ == "__main__":
    print(
        talk_to_ai(
            USER_PROMPT,
            ai_model=AI_MODEL,
            system_prompt=SYSTEM_PROMPT,
            temperature=TEMPERATURE,
        )
    )
