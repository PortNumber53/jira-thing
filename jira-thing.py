from dotenv import load_dotenv
import os
import sys
import logging
import google.generativeai as genai
from jira import JIRA

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO to see general logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler('jira_app.log')  # Output to file
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv('GEMINI_API_KEY')

# Check if API key is present
if not api_key:
    logger.error("GEMINI_API_KEY not found in .env file")
    sys.exit(1)

# Configure the API key
genai.configure(api_key=api_key)

gemini_model_name = os.getenv('GEMINI_MODEL_NAME')

if not gemini_model_name:
    logger.error("GEMINI_MODEL_NAME not found in .env file")
    sys.exit(1)

# Jira Configuration
jira_token = os.getenv('JIRA_API_TOKEN')
jira_base_url = os.getenv('JIRA_BASE_URL')
jira_username = os.getenv('JIRA_USERNAME')

# Check if Jira credentials are present
if not jira_token or not jira_base_url or not jira_username:
    logger.error("JIRA_API_TOKEN or JIRA_BASE_URL or JIRA_USERNAME not found in .env file")
    sys.exit(1)

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

        logger.info(f"Attempting to connect to Jira at {jira_base_url}")

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

        logger.info(f"Successfully retrieved {len(project_list)} Jira projects")
        return project_list

    except Exception as e:
        # Log the full exception with traceback
        logger.exception("Error retrieving Jira projects")
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