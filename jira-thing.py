from dotenv import load_dotenv
import os
import google.generativeai as genai
from jira import JIRA

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv('GEMINI_API_KEY')

# Check if API key is present
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure the API key
genai.configure(api_key=api_key)

gemini_model_name = os.getenv('GEMINI_MODEL_NAME')

if not gemini_model_name:
    raise ValueError("GEMINI_MODEL_NAME not found in .env file")

# Jira Configuration
jira_token = os.getenv('JIRA_API_TOKEN')
jira_base_url = os.getenv('JIRA_BASE_URL')
jira_username = os.getenv('JIRA_USERNAME')

# Check if Jira credentials are present
if not jira_token or not jira_base_url or not jira_username:
    raise ValueError("JIRA_API_TOKEN or JIRA_BASE_URL or JIRA_USERNAME not found in .env file")

def get_jira_projects():
    """
    Retrieve a list of available Jira projects.

    Returns:
        list: A list of project dictionaries containing project details.
    """
    try:
        # Validate credentials
        if not jira_token or not jira_base_url or not jira_username:
            raise ValueError("Jira credentials are missing")

        # Initialize Jira client with more explicit authentication
        jira_client = JIRA(
            server=jira_base_url,
            basic_auth=(jira_username, jira_token)
        )

        # Get all projects
        projects = jira_client.projects()

        # Convert projects to a list of dictionaries for easier handling
        project_list = [
            {
                'key': project.key,
                'name': project.name,
                'id': project.id
            }
            for project in projects
        ]

        return project_list

    except Exception as e:
        print(f"Detailed error retrieving Jira projects: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        return []

# Initialize the model
model = genai.GenerativeModel(gemini_model_name)  # Use a valid model name, e.g., 'gemini-pro'

# Generate content
# try:
#     response = model.generate_content("Explain how AI works")
#     print(response.text)
# except Exception as e:
#     print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    projects = get_jira_projects()
    print("Available Jira Projects:")
    for project in projects:
        print(f"Key: {project['key']}, Name: {project['name']}, ID: {project['id']}")