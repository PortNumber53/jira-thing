from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv('GEMINI_API_KEY')

# Check if API key is present
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure the API key
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')  # Use a valid model name, e.g., 'gemini-pro'

# Generate content
try:
    response = model.generate_content("Explain how AI works")
    print(response.text)
except Exception as e:
    print(f"An error occurred: {e}")
# Print the response
print(response.text)