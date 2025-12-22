import os

from dotenv import load_dotenv

# This searches for a .env file and loads the variables
load_dotenv()

# Now you can access it like any other environment variable
api_key = os.getenv("MISTRAL_API_KEY")

if api_key:
    print("Key loaded successfully!")
else:
    print("Key not found. Check your .env file location.")
