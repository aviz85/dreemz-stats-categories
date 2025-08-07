import os
from dotenv import load_dotenv
from groq import Groq
import inspect

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Get the signature of the create method
sig = inspect.signature(client.chat.completions.create)
print("Parameters for chat.completions.create:")
for param_name, param in sig.parameters.items():
    print(f"  - {param_name}: {param.annotation if param.annotation != inspect.Parameter.empty else 'Any'}")