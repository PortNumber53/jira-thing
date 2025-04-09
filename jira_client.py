#!/usr/bin/env python3

import logging
from jira import JIRA
from config import config

# Use the root logger instead of creating a new named logger
logger = logging.getLogger()

class JiraManager:
    def __init__(self):
        """
        Initialize the Jira client using environment variables.

        Raises:
            RuntimeError: If Jira connection cannot be established
        """
        try:
            # Initialize Jira client
            self.client = JIRA(
                server=config['jira_server'],
                basic_auth=(config['jira_username'], config['jira_token'])
            )

            # Verify connection by getting current user
            self.client.current_user = self.client.current_user()

            logger.info(f"Successfully connected to Jira at {config['jira_server']}")
        except Exception as e:
            logger.critical(f"Failed to initialize Jira client: {e}", exc_info=True)
            raise RuntimeError(f"Jira client initialization failed: {e}")

    def get_projects(self):
        """
        Retrieve a list of available Jira projects.

        Returns:
            list: A list of project dictionaries containing project details.
        """
        try:
            # Retrieve projects
            projects = self.client.projects()
            project_list = [
                {
                    'key': project.key,
                    'name': project.name
                }
                for project in projects
            ]

            logger.debug(f"Successfully retrieved {len(project_list)} Jira projects. Project keys: {[p['key'] for p in project_list]}")
            return project_list

        except Exception as e:
            logger.error(f"Failed to retrieve Jira projects: {e}", exc_info=True)
            raise

    def create_project(self, name, key, project_type='software'):
        """
        Create a new Jira project.

        Args:
            name (str): Project name
            key (str): Project key
            project_type (str, optional): Project type. Defaults to 'software'.

        Returns:
            dict: Created project details or None if creation fails
        """
        try:
            project_dict = {
                'key': key,
                'name': name,
                'projectTypeKey': project_type
            }

            new_project = self.client.create_project(**project_dict)
            logger.info(f"Successfully created project: {name} ({key})")
            return {
                'key': new_project.key,
                'name': new_project.name,
                'id': new_project.id
            }
        except Exception as e:
            logger.error(f"Failed to create project {name}: {e}", exc_info=True)
            return None

    def create_task(self, project_key, summary, description=None, task_type='Task'):
        """
        Create a new Jira task.

        Args:
            project_key (str): Project key
            summary (str): Task summary
            description (str, optional): Task description
            task_type (str, optional): Task type. Defaults to 'Task'.

        Returns:
            dict: Created task details or None if creation fails
        """
        try:
            task_dict = {
                'project': project_key,
                'summary': summary,
                'description': description or '',
                'issuetype': {'name': task_type}
            }

            new_task = self.client.create_issue(**task_dict)
            logger.info(f"Successfully created task: {summary} in project {project_key}")
            return {
                'key': new_task.key,
                'summary': new_task.fields.summary,
                'project': new_task.fields.project.key
            }
        except Exception as e:
            logger.error(f"Failed to create task {summary}: {e}", exc_info=True)
            return None

    def get_tasks(self, project_key=None, assignee=None, labels=None, sprint=None, status=None):
        """
        Retrieve Jira tasks with optional filtering.

        Args:
            project_key (str, optional): Filter tasks by project key
            assignee (str, optional): Filter tasks by assignee username
            labels (list, optional): Filter tasks by labels
            sprint (str, optional): Filter tasks by sprint name or ID
            status (str, optional): Filter tasks by status (e.g., 'To Do', 'In Progress', 'Done')

        Returns:
            list: A list of task dictionaries containing task details
        """
        try:
            # If no specific filters, get all statuses for the project to help diagnose
            if project_key and not any([assignee, labels, sprint, status]):
                # Get all issues for the project to capture all statuses
                all_issues = self.client.search_issues(f"project = '{project_key}'",
                                                       fields=['status'],
                                                       maxResults=1000)
                if all_issues:
                    # Collect unique statuses
                    unique_statuses = set(issue.fields.status.name for issue in all_issues)

                    print("Available statuses:")
                    for unique_status in sorted(unique_statuses):
                        print(f"- {unique_status}")

            # Construct JQL query dynamically
            jql_conditions = []
            if project_key:
                jql_conditions.append(f"project = '{project_key}'")
            if assignee:
                jql_conditions.append(f"assignee = '{assignee}'")
            if labels:
                jql_conditions.extend([f"labels = '{label}'" for label in labels])
            if sprint:
                jql_conditions.append(f"sprint = '{sprint}'")
            if status:
                jql_conditions.append(f"status = '{status}'")

            # Combine conditions
            jql_query = " AND ".join(jql_conditions) if jql_conditions else ""

            # Search for issues
            issues = self.client.search_issues(jql_query, maxResults=1000,
                                               fields=['summary', 'description', 'status', 'assignee', 'project', 'labels'])

            task_list = [
                {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'description': issue.fields.description,
                    'status': issue.fields.status.name,
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    'project': issue.fields.project.key,
                    'labels': issue.fields.labels
                }
                for issue in issues
            ]

            logger.debug(f"Successfully retrieved {len(task_list)} Jira tasks.")
            return task_list

        except Exception as e:
            # Add more detailed error logging
            logger.error(f"Failed to retrieve Jira tasks: {e}", exc_info=True)

            # If it's a status-related error, try to get available statuses
            if "does not exist for the field 'status'" in str(e):
                try:
                    # Fetch all statuses for the project
                    project_statuses = self.client.project(project_key).statuses
                    print("Valid statuses for this project:")
                    for status_obj in project_statuses:
                        print(status_obj.name)
                except Exception as status_error:
                    logger.error(f"Could not retrieve project statuses: {status_error}")

            raise

    def get_statuses(self, project_key=None):
        """
        Retrieve all available statuses for a Jira project.

        Args:
            project_key (str, optional): Project key to retrieve statuses for.
                                         If None, retrieves global statuses.

        Returns:
            list: A list of dictionaries containing status details grouped by issue type
        """
        try:
            # If no project key is provided, fall back to global statuses
            if not project_key:
                statuses = self.client.statuses()
                return [
                    {
                        'id': status.id,
                        'name': status.name,
                        'description': status.description or '',
                        'category': status.statusCategory.name if status.statusCategory else ''
                    }
                    for status in statuses
                ]

            # Use the REST API directly to get project-specific statuses
            url = f'{self.client.server_url}/rest/api/2/project/{project_key}/statuses'
            response = self.client._session.get(url)

            # Raise an exception for bad responses
            response.raise_for_status()

            # Parse the JSON response
            project_statuses = response.json()

            # Flatten and format the statuses
            formatted_statuses = []
            for issue_type in project_statuses:
                issue_type_name = issue_type['name']
                for status in issue_type['statuses']:
                    formatted_statuses.append({
                        'id': status['id'],
                        'name': status['name'],
                        'description': status.get('description', ''),
                        'issue_type': issue_type_name,
                        'category': status.get('statusCategory', {}).get('name', '')
                    })

            logger.warning(f"Retrieved {len(formatted_statuses)} statuses for project {project_key}")
            return formatted_statuses

        except Exception as e:
            logger.error(f"Failed to retrieve statuses for project {project_key}: {e}", exc_info=True)
            raise
