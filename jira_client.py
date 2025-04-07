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

            logger.debug(f"Successfully retrieved {len(project_list)} Jira projects")
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
