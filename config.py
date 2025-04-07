#!/usr/bin/env python3

import os
import sys
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Explicitly load .env file
# Load .env file
load_dotenv(override=True)

# Configure logging based on environment variable
debug_level = os.getenv('DEBUG_LEVEL', 'INFO').upper()

log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Disable any existing loggers
logging.getLogger().handlers.clear()

# Create a custom handler with the desired log level
handler = logging.StreamHandler()
level = os.getenv('DEBUG_LEVEL', 'INFO').upper()
handler.setLevel(getattr(logging, level, logging.WARNING))

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Configure the root logger
root_logger = logging.getLogger()
root_logger.setLevel(log_levels.get(debug_level, logging.WARNING))
if root_logger.hasHandlers():
    root_logger.handlers = []  # Clear any existing handlers
root_logger.addHandler(handler)

# Add file logging
file_handler = logging.FileHandler('jira_app.log')
file_handler.setLevel(log_levels.get(debug_level, logging.WARNING))
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

# Silence third-party library loggers if needed
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('google').setLevel(logging.WARNING)

# Create a logger for the current module
logger = logging.getLogger(__name__)

def load_environment_variables():
    """
    Load environment variables from .env file.

    Raises:
        SystemExit: If required environment variables are missing
    """
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
        raise ValueError("Missing Jira connection parameters in .env file")

    return {
        'gemini_model_name': gemini_model_name,
        'jira_server': jira_server,
        'jira_token': jira_token,
        'jira_username': jira_username
    }

# Load environment variables when this module is imported
config = load_environment_variables()
