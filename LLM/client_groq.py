from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client        # same client for all avoid unnecessity

    if _client is None:
        _client = Groq()

    return _client