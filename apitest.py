import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')
print(f"Key found: {api_key[:10] if api_key else 'NONE'}...")
