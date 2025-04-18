#!/usr/bin/env python3

import sys
import argparse
import logging
from jira_client import JiraManager

logger = logging.getLogger(__name__)

# Define help commands
help_commands = ['help', '-h', '--help']

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
        func.metadata = {
            'category': category,
            'name': name,
            'description': description,
            'usage': usage,
            'options': options or []
        }
        return func
    return decorator

def display_help_summary(context=None):
    """
    Display a comprehensive help summary for the Jira CLI tool.

    Args:
        context (str, optional): Specific context to display help for
                                 (e.g., 'jira', 'jira project', 'jira task')
    """
    print("Jira CLI Tool Help")
    print("=================")

    if context == 'jira':
        print("\nAvailable Jira Commands:")
        print("  project   Manage Jira projects")
        print("  task      Manage Jira tasks")
    elif context == 'jira project':
        print("\nJira Project Commands:")
        print("  list      List all Jira projects")
        print("  create    Create a new Jira project")
        print("  statuses  List available statuses for a Jira project")
    elif context == 'jira project list':
        print("\nJira Project List Command:")
        print("  Lists all available Jira projects")
        print("\nUsage:")
        print("  ./main.py jira project list")
    elif context == 'jira project create':
        print("\nJira Project Create Command:")
        print("  Creates a new Jira project")
        print("\nUsage:")
        print("  ./main.py jira project create --name 'Project Name' --key PROJ --type software")
        print("\nOptions:")
        print("  --name     Project name (required)")
        print("  --key      Project key (required)")
        print("  --type     Project type (optional, default: software)")
    elif context == 'jira project statuses':
        print("\nJira Project Statuses Command:")
        print("  Lists available statuses for a Jira project")
        print("\nUsage:")
        print("  ./main.py jira project statuses [--project PROJECT_KEY]")
        print("\nOptions:")
        print("  --project     Project key (optional)")
    elif context == 'jira task':
        print("\nJira Task Commands:")
        print("  create    Create a new Jira task")
        print("  list      List tasks for a project")
    elif context == 'jira task create':
        print("\nJira Task Create Command:")
        print("  Creates a new Jira task")
        print("\nUsage:")
        print("  ./main.py jira task create --project PROJ --summary 'Task Summary'")
        print("\nOptions:")
        print("  --project     Project key (required)")
        print("  --summary     Task summary (required)")
        print("  --description Task description (optional)")
        print("  --type        Task type (optional, default: Task)")
    elif context == 'jira task list':
        print("\nJira Task List Command:")
        print("  Lists tasks for a project with optional filters")
        print("\nUsage:")
        print("  ./main.py jira task list --project KEY [--assignee USER] [--status STATUS] [--labels LABEL1 LABEL2]")
        print("\nOptions:")
        print("  --project     Project key (required)")
        print("  --assignee    Assignee (optional)")
        print("  --status      Status (optional)")
        print("  --labels      Labels (optional)")
    else:
        print("\nUsage: jira [command] [subcommand] [options]")
        print("\nCommands:")
        print("  jira project   Manage Jira projects")
        print("  jira task      Manage Jira tasks")
        print("\nUse 'jira [command] --help' for more information about a command.")

    return


@command_metadata('project', 'list', 'List all Jira projects')
def handle_jira_project_list(args):
    """
    Handle the 'jira project list' command.
    """
    try:
        jira_manager = JiraManager()
        projects = jira_manager.get_projects()

        if not projects:
            print("No projects found.")
            return

        print("Jira Projects:")
        for project in projects:
            print(f"- {project['key']}: {project['name']}")
    except JiraException as e:
        logger.error(f"Error listing projects: {e}")
        print("Failed to list projects. Please check the logs for more details.")

@command_metadata('project', 'create', 'Create a new Jira project',
                  usage='jira project create --name "Project Name" --key PROJ --type software')
def handle_jira_project_create(args):
    """
    Handle the 'jira project create' command.

    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    try:
        jira_manager = JiraManager()
        project = jira_manager.create_project(
            name=args.name,
            key=args.key,
            project_type=args.type
        )

        if project:
            print(f"Project created successfully:")
            print(f"- Key: {project['key']}")
            print(f"- Name: {project['name']}")
        else:
            print("Failed to create project.")
    except JiraException as e:
        logger.error(f"Error creating project: {e}")
        print("Failed to create project. Please check the logs for more details.")

@command_metadata('project', 'statuses', 'List available statuses for a Jira project',
                  usage='jira project statuses [--project PROJECT_KEY]')
def handle_jira_project_statuses(args):
    """
    Handle the 'jira project statuses' command.

    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    try:
        jira_manager = JiraManager()
        statuses = jira_manager.get_statuses(project_key=args.project)

        if not statuses:
            print("No statuses found.")
            return

        print(f"Statuses{' for Project ' + args.project if args.project else ''}:")

        # Group statuses by issue type
        issue_type_statuses = {}
        for status in statuses:
            issue_type = status.get('issue_type', 'Unknown')
            if issue_type not in issue_type_statuses:
                issue_type_statuses[issue_type] = []
            issue_type_statuses[issue_type].append(status)

        # Print statuses grouped by issue type
        for issue_type, type_statuses in issue_type_statuses.items():
            print(f"\n{issue_type} Issue Type Statuses:")
            for status in type_statuses:
                print(f"- {status['id']} - {status['name']}")
                if status.get('description'):
                    print(f"  Description: {status['description']}")
                if status.get('category'):
                    print(f"  Category: {status['category']}")
            print()
    except Exception as e:
        logger.error(f"Error retrieving statuses: {e}")
        print("Failed to retrieve statuses. Please check the logs for more details.")

@command_metadata('task', 'create', 'Create a new Jira task',
                  usage='jira task create --project PROJ --summary "Task Summary" --type Task')
def handle_jira_task_create(args):
    """
    Handle the 'jira task create' command.

    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    try:
        jira_manager = JiraManager()
        task = jira_manager.create_task(
            project_key=args.project,
            summary=args.summary,
            description=args.description,
            task_type=args.type
        )

        if task:
            print(f"Task created successfully:")
            print(f"- Key: {task['key']}")
            print(f"- Summary: {task['summary']}")
            print(f"- Project: {task['project']}")
        else:
            print("Failed to create task.")
    except JiraException as e:
        logger.error(f"Error creating task: {e}")
        print("Failed to create task. Please check the logs for more details.")

@command_metadata('task', 'list', 'List tasks for a project with optional filters',
                  usage='jira task list --project KEY [--assignee USER] [--status STATUS] [--labels LABEL1 LABEL2]')
def handle_jira_task_list(args):
    """
    Handle the 'jira task list' command.

    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    try:
        jira_manager = JiraManager()
        tasks = jira_manager.get_tasks(
            project_key=args.project,
            assignee=args.assignee,
            labels=args.labels,
            sprint=args.sprint,
            status=args.status
        )

        if not tasks:
            print("No tasks found matching the specified criteria.")
            return

        print(f"Tasks for Project {args.project}:")
        for task in tasks:
            print(f"- {task['key']}: {task['summary']}")
            print(f"  Status: {task['status']}")
            print(f"  Assignee: {task['assignee']}")
            if task['labels']:
                print(f"  Labels: {', '.join(task['labels'])}")
            print()
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        print("Failed to list tasks. Please check the logs for more details.")

def handle_help(args):
    """
    Display help information for the CLI.

    Args:
        args (argparse.Namespace): Parsed command-line arguments
    """
    display_help_summary()

def setup_cli_parser():
    """
    Set up the CLI argument parser.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
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
    jira_project_list_parser = jira_project_subparsers.add_parser(
        'list',
        help='List all Jira projects',
        description='Retrieve and display a list of all Jira projects in your workspace.',
        epilog='Example: ./main.py jira project list'
    )
    jira_project_list_parser.set_defaults(func=handle_jira_project_list)

    # Jira project create
    jira_project_create_parser = jira_project_subparsers.add_parser(
        'create',
        help='Create a new Jira project',
        description='Create a new Jira project with specified details.',
        epilog='Example: ./main.py jira project create --name "My Project" --key MYPROJ'
    )
    jira_project_create_parser.add_argument('--name', required=True, help='Project name (required)')
    jira_project_create_parser.add_argument('--key', required=True, help='Project key (required, must be unique)')
    jira_project_create_parser.add_argument('--type', default='software', choices=['software', 'service'],
                                            help='Project type (optional, default: software)')
    jira_project_create_parser.set_defaults(func=handle_jira_project_create)

    # Jira project statuses
    jira_project_statuses_parser = jira_project_subparsers.add_parser(
        'statuses',
        help='List available statuses for a Jira project',
        description='List available statuses for a Jira project.',
        epilog='Example: ./main.py jira project statuses [--project PROJECT_KEY]'
    )
    jira_project_statuses_parser.add_argument('--project', help='Project key (optional)')
    jira_project_statuses_parser.set_defaults(func=handle_jira_project_statuses)

    # Jira task subcommands
    jira_task_parser = jira_subparsers.add_parser('task', help='Jira task commands', add_help=False)
    jira_task_subparsers = jira_task_parser.add_subparsers(help='Jira task subcommands', dest='task_command')
    jira_task_parser.add_argument('-h', '--help', action='store_true', help='Show Jira task command help')
    jira_task_parser.set_defaults(func=handle_help)

    # Jira task create
    jira_task_create_parser = jira_task_subparsers.add_parser(
        'create',
        help='Create a new Jira task',
        description='Create a new task in a specified Jira project.',
        epilog='Example: ./main.py jira task create --project MYPROJ --summary "Implement feature"'
    )
    jira_task_create_parser.add_argument('--project', required=True, help='Project key (required)')
    jira_task_create_parser.add_argument('--summary', required=True, help='Task summary (required)')
    jira_task_create_parser.add_argument('--description', help='Task description (optional)')
    jira_task_create_parser.add_argument('--type', default='Task',
                                         choices=['Task', 'Sub-task', 'Epic'],
                                         help='Task type (optional, default: Task)')
    jira_task_create_parser.set_defaults(func=handle_jira_task_create)

    # Jira task list
    jira_task_list_parser = jira_task_subparsers.add_parser(
        'list',
        help='List tasks for a project with optional filters',
        description='List tasks for a project with optional filters.',
        epilog='Example: ./main.py jira task list --project MYPROJ'
    )
    jira_task_list_parser.add_argument('--project', required=True, help='Project key (required)')
    jira_task_list_parser.add_argument('--assignee', help='Assignee (optional)')
    jira_task_list_parser.add_argument('--status', help='Status (optional). Common values might include: To Do, In Progress, Done. Use exact status name from your Jira project.')
    jira_task_list_parser.add_argument('--labels', nargs='+', help='Labels (optional)')
    jira_task_list_parser.add_argument('--sprint', help='Sprint (optional)')
    jira_task_list_parser.set_defaults(func=handle_jira_task_list)

    return parser

def main():
    """
    Main entry point for the CLI application.
    """
    # Create the parser
    parser = setup_cli_parser()

    # Check for help scenarios before parsing
    if len(sys.argv) > 1:
        # Check for help in nested commands
        if sys.argv[-1] in help_commands:
            context = None
            if len(sys.argv) > 2:
                context = ' '.join(sys.argv[1:-1])
            display_help_summary(context)

    # If no arguments are provided or help is explicitly requested
    if len(sys.argv) == 1 or \
       (len(sys.argv) > 1 and (sys.argv[1] in ['-h', '--help', 'help'])):
        display_help_summary()

    # Parse arguments
    args = parser.parse_args()

    # If no function is set (which happens when no subcommand is used),
    # default to help function
    if not hasattr(args, 'func'):
        display_help_summary()
    else:
        # Call the appropriate handler
        args.func(args)

if __name__ == "__main__":
    main()
