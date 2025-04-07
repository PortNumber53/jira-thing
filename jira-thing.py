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

# Global Jira client variable
jira_client = None

def initialize_jira_client():
    """
    Initialize the Jira client using environment variables.
    
    Returns:
        JIRA: Initialized Jira client
    
    Raises:
        RuntimeError: If Jira connection cannot be established
    """
    global jira_client
    
    try:
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Retrieve Jira connection parameters from environment
        jira_server = os.getenv('JIRA_BASE_URL')
        jira_token = os.getenv('JIRA_API_TOKEN')
        jira_username = os.getenv('JIRA_USERNAME')
        
        # Validate required parameters
        if not all([jira_server, jira_token, jira_username]):
            raise ValueError("Missing Jira connection parameters in .env file")
        
        # Initialize Jira client
        jira_client = JIRA(
            server=jira_server, 
            basic_auth=(jira_username, jira_token)
        )
        
        # Verify connection by getting current user
        jira_client.current_user = jira_client.current_user()
        
        logger.info(f"Successfully connected to Jira at {jira_server}")
        return jira_client
    
    except Exception as e:
        logger.error(f"Failed to initialize Jira client: {e}", exc_info=True)
        raise RuntimeError(f"Jira client initialization failed: {e}")

# Call initialization at script import
try:
    initialize_jira_client()
except Exception as e:
    logger.warning(f"Jira client not initialized on import: {e}")
    # Allow script to continue running, but operations will fail if Jira client is needed

def get_jira_projects():
    """
    Retrieve a list of available Jira projects.

    Returns:
        list: A list of project dictionaries containing project details.
    """
    try:
        # Validate credentials
        if not jira_client:
            raise ValueError("Jira client is not initialized")

        logger.info(f"Attempting to connect to Jira at {jira_client.server}")

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
    
    Raises:
        Exception: If project creation fails
    """
    try:
        # Validate input parameters
        if not args.name or not args.key:
            raise ValueError("Project name and key are required")
        
        # Use the existing JIRA connection from the global context
        if not jira_client:
            raise RuntimeError("Jira client not initialized. Please check your Jira connection settings.")
        
        # Attempt to create the project
        project_type_map = {
            'software': 'software',
            'service': 'service'
        }
        
        new_project = jira_client.create_project(
            key=args.key.upper(),  # Jira typically requires uppercase keys
            name=args.name,
            projectTypeKey=project_type_map.get(args.type, 'software'),
            lead=jira_client.current_user  # Use the current user as project lead
        )
        
        # Log successful project creation
        logger.info(f"Successfully created Jira project: {args.name} (Key: {args.key})")
        print(f"Project '{args.name}' created successfully with key {args.key}")
        
        return new_project
    
    except Exception as e:
        # Log the error and provide a user-friendly error message
        logger.error(f"Failed to create Jira project: {e}", exc_info=True)
        print(f"Error creating Jira project: {e}")
        raise

def handle_jira_task_create(args):
    """
    Handle the 'jira task create' command.
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments
    
    Raises:
        Exception: If task creation fails
    """
    try:
        # Validate input parameters
        if not args.project:
            raise ValueError("Project key is required to create a task")
        
        # Use the existing JIRA connection from the global context
        if not jira_client:
            raise RuntimeError("Jira client not initialized. Please check your Jira connection settings.")
        
        # Prepare task creation dictionary
        issue_dict = {
            'project': {'key': args.project.upper()},  # Ensure uppercase project key
            'summary': args.summary if hasattr(args, 'summary') else 'New Task Created via CLI',
            'description': args.description if hasattr(args, 'description') else 'Task created using Jira CLI tool',
            'issuetype': {'name': args.type if hasattr(args, 'type') else 'Task'}
        }
        
        # Attempt to create the task
        new_task = jira_client.create_issue(fields=issue_dict)
        
        # Log successful task creation
        logger.info(f"Successfully created Jira task in project {args.project}: {new_task.key}")
        print(f"Task created successfully: {new_task.key}")
        
        return new_task
    
    except Exception as e:
        # Log the error and provide a user-friendly error message
        logger.error(f"Failed to create Jira task: {e}", exc_info=True)
        print(f"Error creating Jira task: {e}")
        raise

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
jira_task_create_parser.add_argument('--summary', help='Task summary')
jira_task_create_parser.add_argument('--description', help='Task description')
jira_task_create_parser.add_argument('--type', default='Task', choices=['Task', 'Sub-task', 'Epic'], help='Task type')
jira_task_create_parser.set_defaults(func=handle_jira_task_create)

if __name__ == '__main__':
    main()
