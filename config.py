#!/usr/bin/env python3

import os
import sys
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('jira_app.log')
    ]
)
logger = logging.getLogger(__name__)

def load_environment_variables():
    """
    Load environment variables from .env file.
    
    Raises:
        SystemExit: If required environment variables are missing
    """
    load_dotenv()

    # Check Gemini API configuration
    api_key = os.getenv('GEMINI_API_KEY')
    gemini_model_name = os.getenv('GEMINI_MODEL_NAME')

    if not api_key:
        logger.error("GEMINI_API_KEY not found in .env file")
        sys.exit(1)

    if not gemini_model_name:
        logger.error("GEMINI_MODEL_NAME not found in .env file")
        sys.exit(1)

    # Configure Gemini API
    genai.configure(api_key=api_key)

    # Check Jira configuration
    jira_server = os.getenv('JIRA_BASE_URL')
    jira_token = os.getenv('JIRA_API_TOKEN')
    jira_username = os.getenv('JIRA_USERNAME')

    if not all([jira_server, jira_token, jira_username]):
        logger.error("Missing Jira connection parameters in .env file")
        sys.exit(1)

    return {
        'gemini_model_name': gemini_model_name,
        'jira_server': jira_server,
        'jira_token': jira_token,
        'jira_username': jira_username
    }

# Load environment variables when this module is imported
config = load_environment_variables()
