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

    except OSError as e:
        logger.error(f"Failed to load environment variables: {e}", exc_info=True)
        raise RuntimeError(f"Failed to load environment variables: {e}")
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

        # Get Jira server URL from environment variable
        jira_server = os.getenv('JIRA_BASE_URL', 'Unknown Server')
        logger.info(f"Attempting to connect to Jira at {jira_server}")

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

def display_help_summary(context=None):
    """
    Display a comprehensive help summary for the Jira CLI tool.
    
    Args:
        context (str, optional): Specific context to display help for 
                                 (e.g., 'jira', 'jira project', 'jira task')
    """
    print("Jira CLI Tool - Command Reference\n")
    print("Easily manage your Jira projects and tasks from the command line.\n")
    
    # Collect all functions with command metadata
    commands = []
    for name, obj in globals().items():
        if hasattr(obj, 'command_metadata'):
            commands.append(obj.command_metadata)
    
    # Group commands by category
    command_groups = {}
    for cmd in commands:
        if cmd['category'] not in command_groups:
            command_groups[cmd['category']] = []
        command_groups[cmd['category']].append(cmd)
    
    # Determine which categories to display
    display_categories = command_groups.keys()
    if context:
        context_parts = context.split()
        if len(context_parts) > 1 and context_parts[1] in command_groups:
            display_categories = [context_parts[1]]
    
    # Display commands
    for category in display_categories:
        category_commands = command_groups[category]
        print(f"{category.capitalize()} Commands:")
        for cmd in category_commands:
            # Basic command format with description
            cmd_str = f"  jira {category} {cmd['name']}"
            
            # Pad the command string to align descriptions
            cmd_str = cmd_str.ljust(35)
            print(f"{cmd_str} {cmd['description']}")
        print()
    
    print("Global Options:")
    print("  -h, --help    Show help for a specific command\n")
    print("Get started by exploring available commands!")

def command_metadata(category, name, description, usage=None, options=None):
    """
    Decorator to add metadata to CLI command functions.

    Args:
        category (str): The command category (e.g., 'project', 'task')
        name (str): The command name (e.g., 'list', 'create')
        description (str): A user-friendly description of the command
        usage (str, optional): Example usage of the command
        options (list, optional): List of command options
    """
    def decorator(func):
        func.command_metadata = {
            'category': category,
            'name': name,
            'description': description,
            'usage': usage or '',
            'options': options or []
        }
        return func
    return decorator

@command_metadata('project', 'list', 'List all Jira projects')
def handle_jira_project_list(args):
    """
    Handle the 'jira project list' command.
    """
    projects = get_jira_projects()
    print("Available Jira Projects:")
    if projects:
        for project in projects:
            print(f"Key: {project['key']}, Name: {project['name']}, ID: {project['id']}")
    else:
        print("No Jira projects found")

@command_metadata('project', 'create', 'Create a new Jira project',
                  usage='jira project create --name "My Project" --key MYPROJ --type software',
                  options=['--name NAME', '--key KEY', '--type [software|service]'])
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

        try:
            new_project = jira_client.create_project(
                key=args.key.upper(),  # Jira typically requires uppercase keys
                name=args.name,
                projectTypeKey=project_type_map.get(args.type, 'software'),
                lead=jira_client.current_user  # Use the current user as project lead
            )
        except Exception as e:
            logger.error(f"Failed to create Jira project: {e}", exc_info=True)
            print(f"Error creating Jira project: {e}")
            raise

        # Log successful project creation
        logger.info(f"Successfully created Jira project: {args.name} (Key: {args.key})")
        print(f"Project '{args.name}' created successfully with key {args.key}")

        return new_project

    except Exception as e:
        # Log the error and provide a user-friendly error message
        logger.error(f"Failed to create Jira project: {e}", exc_info=True)
        print(f"Error creating Jira project: {e}")
        raise

@command_metadata('task', 'create', 'Create a new Jira task',
                  usage='jira task create --project MYPROJ --summary "New Task" --description "Task details"',
                  options=['--project PROJECT_KEY', '--summary SUMMARY', '--description DESC', '--type [Task|Sub-task|Epic]'])
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

def handle_help(args):
    """
    Display help information for the CLI.

    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    # If no specific help context is provided, show the comprehensive summary
    display_help_summary()

def main():
    """
    Main entry point for the CLI application.
    """
    # Special handling for help commands with full context
    help_commands = ['help', '-h', '--help']
    
    # Check for full command help scenarios
    if len(sys.argv) > 3 and sys.argv[-1] in help_commands:
        # Detailed help for specific commands
        if sys.argv[1] == 'jira' and sys.argv[2] == 'project' and sys.argv[3] == 'create':
            print("Jira Project Create Command\n")
            print("Create a new Jira project with specified details.\n")
            print("Usage: jira project create --name PROJECT_NAME --key PROJECT_KEY [--type software|service]\n")
            print("Options:")
            print("  --name NAME     Name of the project (required)")
            print("  --key KEY       Unique project key (required)")
            print("  --type TYPE     Project type (optional, default: software)")
            print("\nExample:")
            print("  jira project create --name \"My Awesome Project\" --key MYPROJ --type software")
            sys.exit(0)
        elif sys.argv[1] == 'jira' and sys.argv[2] == 'project' and sys.argv[3] == 'list':
            print("Jira Project List Command\n")
            print("List all available Jira projects in your organization.\n")
            print("Usage: jira project list\n")
            print("This command retrieves and displays all Jira projects you have access to.")
            print("Each project will show its key, name, and other basic information.\n")
            print("Example:")
            print("  jira project list")
            sys.exit(0)
        elif sys.argv[1] == 'jira' and sys.argv[2] == 'task' and sys.argv[3] == 'create':
            print("Jira Task Create Command\n")
            print("Create a new Jira task within a project.\n")
            print("Usage: jira task create --project PROJECT_KEY --summary TASK_SUMMARY [options]\n")
            print("Options:")
            print("  --project KEY     Project key where task will be created (required)")
            print("  --summary TEXT    Brief description of the task (required)")
            print("  --description DESC  Detailed task description (optional)")
            print("  --type TYPE       Task type (optional, default: Task)")
            print("\nExample:")
            print("  jira task create --project MYPROJ --summary \"Fix login bug\" --description \"Resolve authentication issue\"")
            sys.exit(0)

    # If no arguments are provided or help is explicitly requested
    if len(sys.argv) == 1 or \
       (len(sys.argv) > 1 and (sys.argv[1] in ['-h', '--help', 'help'])):
        display_help_summary()
        sys.exit(0)

    # Special handling for help in nested commands
    if len(sys.argv) > 1 and sys.argv[1] == 'jira':
        if len(sys.argv) > 2 and sys.argv[2] in help_commands:
            # General Jira help
            display_help_summary('jira')
            sys.exit(0)
        elif len(sys.argv) > 3 and sys.argv[3] in help_commands:
            # Specific Jira subcommand help
            display_help_summary(f'jira {sys.argv[2]}')
            sys.exit(0)

    # Parse arguments
    args = parser.parse_args()

    # If no function is set (which happens when no subcommand is used), 
    # default to help function
    if not hasattr(args, 'func'):
        handle_help(args)
    else:
        # Call the appropriate handler
        args.func(args)

# Create the top-level parser
parser = argparse.ArgumentParser(description='Jira CLI Tool', add_help=False)
subparsers = parser.add_subparsers(help='Commands', dest='command')

# Add custom help handling
parser.add_argument('command', nargs='?', default=None, help='Command to execute')
parser.add_argument('subcommand', nargs='?', default=None, help='Subcommand to execute')
parser.add_argument('action', nargs='?', default=None, help='Action to perform')
parser.add_argument('-h', '--help', action='store_true', help='Show help')

# Help command (default)
parser.set_defaults(func=handle_help)

# Jira group
jira_parser = subparsers.add_parser('jira', help='Jira-related commands', add_help=False)
jira_subparsers = jira_parser.add_subparsers(help='Jira subcommands', dest='jira_command')
jira_parser.add_argument('-h', '--help', action='store_true', help='Show Jira command help')
jira_parser.set_defaults(func=handle_help)

# Jira project subcommands
jira_project_parser = jira_subparsers.add_parser('project', help='Jira project commands', add_help=False)
jira_project_subparsers = jira_project_parser.add_subparsers(help='Jira project subcommands', dest='project_command')
jira_project_parser.add_argument('-h', '--help', action='store_true', help='Show Jira project command help')
jira_project_parser.set_defaults(func=handle_help)

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
jira_task_parser = jira_subparsers.add_parser('task', help='Jira task commands', add_help=False)
jira_task_subparsers = jira_task_parser.add_subparsers(help='Jira task subcommands', dest='task_command')
jira_task_parser.add_argument('-h', '--help', action='store_true', help='Show Jira task command help')
jira_task_parser.set_defaults(func=handle_help)

# Jira task create
jira_task_create_parser = jira_task_subparsers.add_parser('create', help='Create a Jira task')
jira_task_create_parser.add_argument('--project', required=True, help='Project key')
jira_task_create_parser.add_argument('--summary', help='Task summary')
jira_task_create_parser.add_argument('--description', help='Task description')
jira_task_create_parser.add_argument('--type', default='Task', choices=['Task', 'Sub-task', 'Epic'], help='Task type')
jira_task_create_parser.set_defaults(func=handle_jira_task_create)

if __name__ == '__main__':
    main()
