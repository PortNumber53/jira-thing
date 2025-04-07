#!/usr/bin/env python3

import argparse
import sys
from dotenv import load_dotenv
import os
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

def handle_help(args):
    """
    Display help information for the CLI.
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    parser.print_help()

def handle_jira_project_list(args):
    """
    Handle the 'jira project list' command.
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    projects = get_jira_projects()
    print("Available Jira Projects:")
    if projects:
        for project in projects:
            print(f"Key: {project['key']}, Name: {project['name']}, ID: {project['id']}")
    else:
        print("No Jira projects found")

def handle_jira_project_create(args):
    """
    Handle the 'jira project create' command.
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    print(f"Creating Jira project: name={args.name}, key={args.key}, type={args.type}")

def handle_jira_task_create(args):
    """
    Handle the 'jira task create' command.
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    print(f"Creating Jira task for project: {args.project}")

def main():
    """
    Main entry point for the CLI application.
    """
    # If no arguments are provided, show help
        parser.print_help(file=sys.stderr)
        sys.exit(1)
    
    # Parse arguments and call the appropriate handler
    args = parser.parse_args()
    args.func(args)

# Create the top-level parser
parser = argparse.ArgumentParser(description='Jira CLI Tool')
subparsers = parser.add_subparsers(help='Commands')

# Help command (default)
parser.set_defaults(func=handle_help)

# Jira group
jira_parser = subparsers.add_parser('jira', help='Jira-related commands')
jira_subparsers = jira_parser.add_subparsers(help='Jira subcommands')

# Jira project subcommands
jira_project_parser = jira_subparsers.add_parser('project', help='Jira project commands')
jira_project_subparsers = jira_project_parser.add_subparsers(help='Jira project subcommands')

# Jira project list
jira_project_list_parser = jira_project_subparsers.add_parser('list', help='List Jira projects')
jira_project_list_parser.set_defaults(func=handle_jira_project_list)

# Jira project create
jira_project_create_parser = jira_project_subparsers.add_parser('create', help='Create a Jira project')
jira_project_create_parser.add_argument('--name', required=True, help='Project name')
jira_project_create_parser.add_argument('--key', required=True, help='Project key')
jira_project_create_parser.add_argument('--type', default='software', choices=['software', 'service'], help='Project type')
jira_project_create_parser.set_defaults(func=handle_jira_project_create)

# Jira task subcommands
jira_task_parser = jira_subparsers.add_parser('task', help='Jira task commands')
jira_task_subparsers = jira_task_parser.add_subparsers(help='Jira task subcommands')

# Jira task create
jira_task_create_parser = jira_task_subparsers.add_parser('create', help='Create a Jira task')
jira_task_create_parser.add_argument('--project', required=True, help='Project key')
jira_task_create_parser.set_defaults(func=handle_jira_task_create)

if __name__ == '__main__':
    main()
