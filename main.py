#!/usr/bin/env python3

import sys
from cli import setup_cli_parser, help_commands, display_help_summary

def main():
    """
    Main entry point for the CLI application.
    """
    # Create the parser
    parser = setup_cli_parser()

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
        display_help_summary()
    else:
        # Call the appropriate handler
        args.func(args)

if __name__ == '__main__':
    main()
